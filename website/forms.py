from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import time

SUBJECT_CHOICES = [
    ('', _('Select a subject...')),
    ('prescription', _('Prescription Enquiry')),
    ('stock', _('Stock Availability')),
    ('refill', _('Chronic Medication Refill')),
    ('billing', _('Medical Aid & Billing')),
    ('general', _('General Question')),
]

# Valid ZW mobile: +26377xxxxxxx or 26377xxxxxxx or 077xxxxxxx, 78, 79 only
phone_validator = RegexValidator(
    regex=r'^(?:\+263|263|0)7[7-9]\d{7}$',
    message=_("Enter a valid ZW mobile number: +263771234567, 263771234567 or 0771234567")
)

class PhoneField(forms.CharField):
    """Strip spaces/dashes before validation so regex passes"""
    def to_python(self, value):
        value = super().to_python(value)
        if value:
            return value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        return value

class ContactForm(forms.Form):
    name = forms.CharField(
        label=_("Full Name"),
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': _('Your name'),
            'required': True
        })
    )

    phone = PhoneField(
        label=_("Phone Number"),
        max_length=20,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': '+263771234567 or 0771234567',
            'required': True
        })
    )

    subject = forms.ChoiceField(
        label=_("Subject"),
        choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={'class': 'select', 'required': True})
    )

    message = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(attrs={
            'class': 'textarea',
            'rows': 4,
            'placeholder': _('How can we help you?'),
            'required': True
        })
    )

    # Anti-spam: Honeypot
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'hp-field',
        'autocomplete': 'off',
        'tabindex': '-1'
    }))

    # Anti-spam: Timestamp
    timestamp = forms.CharField(widget=forms.HiddenInput(), initial=lambda: str(int(time.time())))

    def clean_phone(self):
        """Normalize ZW number to +263 format for email + WhatsApp link"""
        phone = self.cleaned_data['phone']

        # Convert 0771234567 -> +263771234567
        if phone.startswith('0'):
            phone = '+263' + phone[1:]

        # Convert 263771234567 -> +263771234567
        if phone.startswith('263') and not phone.startswith('+263'):
            phone = '+' + phone

        return phone

    def clean_website(self):
        """If honeypot filled, reject"""
        if self.cleaned_data.get('website'):
            raise forms.ValidationError("Bot detected")
        return ''

    def clean_timestamp(self):
        """Reject if submitted faster than 3 seconds"""
        ts = int(self.cleaned_data.get('timestamp', 0))
        if int(time.time()) - ts < 3:
            raise forms.ValidationError(_("Form submitted too fast. Please take a moment to write your message."))
        return ts

    def clean_message(self):
        """Block spam links/keywords"""
        msg = self.cleaned_data.get('message', '').lower()
        spam_words = ['http://', 'https://', 'www.', 'viagra', 'cialis', 'loan', 'casino', 'bitcoin', 'weight loss']
        if any(word in msg for word in spam_words):
            raise forms.ValidationError(_("Links and promotional content are not allowed."))
        return msg
