from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
import traceback
from urllib.parse import quote
from.forms import ContactForm

# Rate limit: 3 submissions per IP per 15 minutes
CONTACT_RATE_LIMIT = 3
CONTACT_RATE_LIMIT_SECONDS = 900 # 15 minutes

def contact(request):
    """
    Handle contact form submissions with anti-spam and rate limiting.

    Features:
    1. IP-based rate limiting: 3 submissions per 15 minutes
    2. Honeypot field to catch bots
    3. Timestamp validation to prevent instant submits
    4. ZW phone normalization to +263 format
    5. Email notification + WhatsApp prefill link generation
    6. Spam keyword filtering

    Args:
        request: Django HttpRequest object

    Returns:
        HttpResponse: Rendered contact page with form context
    """
    # Get client IP for rate limiting. Check X-Forwarded-For first for proxy setups
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown')).split(',')[0].strip()
    cache_key = f'contact_limit_{ip}'
    submissions = cache.get(cache_key, 0)

    if request.method == 'POST':
        # Rate limit check before processing form
        if submissions >= CONTACT_RATE_LIMIT:
            messages.error(request, _('Too many messages sent. Please wait 15 minutes or contact us on WhatsApp.'))
            # Keep form bound so user sees their input + errors. Critical for tests.
            form = ContactForm(request.POST)
        else:
            form = ContactForm(request.POST)

            if form.is_valid():
                cd = form.cleaned_data
                subject_map = dict(form.fields['subject'].choices)

                # Build email content
                email_subject = f"{settings.EMAIL_SUBJECT_PREFIX}{subject_map.get(cd['subject'], cd['subject'])}"
                email_body = (
                    f"Name: {cd['name']}\n"
                    f"Phone: {cd['phone']}\n" # Already normalized to +263 format by form
                    f"Subject: {subject_map.get(cd['subject'])}\n"
                    f"IP: {ip}\n\n"
                    f"Message:\n{cd['message']}"
                )

                try:
                    # Send email notification to pharmacy
                    EmailMessage(
                        subject=email_subject,
                        body=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[settings.CONTACT_EMAIL],
                        reply_to=[cd['phone']]
                    ).send(fail_silently=False)

                    # Build WhatsApp prefill link. Remove + from number for wa.me URL
                    wa_number = settings.CONTACT_WHATSAPP.replace('+', '')
                    wa_text = (
                        f"Hello Thosheck Pharmacies\n"
                        f"Name: {cd['name']}\n"
                        f"Phone: {cd['phone']}\n"
                        f"Subject: {subject_map.get(cd['subject'])}\n\n"
                        f"Message: {cd['message']}"
                    )
                    request.session['wa_link'] = f"https://wa.me/{wa_number}?text={quote(wa_text)}"

                    # Increment rate limit counter. Expires in 15 minutes
                    cache.set(cache_key, submissions + 1, CONTACT_RATE_LIMIT_SECONDS)

                    messages.success(request, _('Thank you! Your message has been sent.'))
                    # PRG pattern: redirect after POST to prevent double submit
                    return redirect('contact')

                except Exception as e:
                    # Log error for debugging but don't expose to user
                    print(f"EMAIL ERROR: {e}")
                    traceback.print_exc()
                    messages.error(request, _('Sorry, email failed to send. Please try WhatsApp instead.'))
            else:
                # Show non-field errors like honeypot/timestamp at top of form
                if form.non_field_errors():
                    messages.error(request, form.non_field_errors()[0])
    else:
        # GET request: show empty form
        form = ContactForm()

    # Pop wa_link from session so WhatsApp button only shows once after successful submit
    wa_link = request.session.pop('wa_link', None)

    context = {
        'form': form,
        'contact_email': settings.CONTACT_EMAIL,
        'contact_whatsapp': settings.CONTACT_WHATSAPP,
        'wa_link': wa_link,
    }
    return render(request, 'website/contact.html', context)

def home(request):
    """Render homepage. Static content only."""
    return render(request, 'website/home.html')

def services(request):
    """Render services page listing pharmacy services."""
    return render(request, 'website/services.html')

def about(request):
    """Render about us page with pharmacy info."""
    return render(request, 'website/about.html')

def branches(request):
    """Render branches page with Harare location details."""
    return render(request, 'website/branches.html')

def products(request):
    """Render products/services catalog page."""
    return render(request, 'website/products.html')

def privacy(request):
    """Render privacy policy page."""
    return render(request, 'website/privacy.html')
