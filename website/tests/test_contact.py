import time
import pytest
from django.urls import reverse
from website.forms import ContactForm

pytestmark = pytest.mark.django_db

class TestContactForm:
    def test_form_valid_with_077_number(self, valid_contact_data):
        """Form accepts 077 format and normalizes to +263"""
        form = ContactForm(valid_contact_data)
        assert form.is_valid()
        assert form.cleaned_data['phone'] == '+263771234567'

    def test_form_valid_with_plus263_number(self, valid_contact_data): # <-- added fixture param
        """Form accepts +263 format directly"""
        data = valid_contact_data.copy()
        data['phone'] = '+263781234567'
        form = ContactForm(data)
        assert form.is_valid()
        assert form.cleaned_data['phone'] == '+263781234567'

    def test_form_rejects_invalid_phone(self, valid_contact_data):
        """Form rejects landline and invalid mobile prefixes"""
        valid_contact_data['phone'] = '021234567'
        form = ContactForm(valid_contact_data)
        assert not form.is_valid()
        assert 'phone' in form.errors

    def test_honeypot_rejects_bot(self, valid_contact_data):
        """Honeypot field catches bots"""
        valid_contact_data['website'] = 'spam.com'
        form = ContactForm(valid_contact_data)
        assert not form.is_valid()
        assert 'website' in form.errors

    def test_timestamp_rejects_fast_submit(self, valid_contact_data):
        """Form rejects submissions faster than 3 seconds"""
        valid_contact_data['timestamp'] = str(int(time.time()))
        form = ContactForm(valid_contact_data)
        assert not form.is_valid()
        assert 'timestamp' in form.errors

    def test_message_rejects_spam_keywords(self, valid_contact_data):
        """Form blocks URLs and spam keywords"""
        valid_contact_data['message'] = 'Buy viagra cheap http://spam.com'
        form = ContactForm(valid_contact_data)
        assert not form.is_valid()
        assert 'message' in form.errors

    def test_phone_normalizes_formats(self, valid_contact_data):
        """Phone field strips spaces/dashes and normalizes to +263 format"""
        cases = [
            ('077 123 4567', '+263771234567'),
            ('077-123-4567', '+263771234567'),
            ('263771234567', '+263771234567'),
            ('+263 77 123 4567', '+263771234567'),
        ]
        for input_phone, expected in cases:
            data = valid_contact_data.copy()
            data['phone'] = input_phone
            form = ContactForm(data)
            assert form.is_valid(), f"Failed for {input_phone}: {form.errors}"
            assert form.cleaned_data['phone'] == expected

class TestContactView:
    def test_get_contact_page(self, client):
        url = reverse('contact')
        response = client.get(url)
        assert response.status_code == 200
        assert 'form' in response.context

    def test_post_valid_form_sends_email_and_redirects(self, client, valid_contact_data, email_settings, mailoutbox):
        url = reverse('contact')
        response = client.post(url, valid_contact_data)
        assert response.status_code == 302
        assert response.url == reverse('contact')
        assert len(mailoutbox) == 1
        assert 'Tendai Moyo' in mailoutbox[0].body
        assert '+263771234567' in mailoutbox[0].body

    def test_post_creates_whatsapp_session_link(self, client, valid_contact_data, whatsapp_settings):
        url = reverse('contact')
        response = client.post(url, valid_contact_data, follow=True)
        assert 'wa_link' in response.context
        assert 'wa.me/263771234567' in response.context['wa_link']
        assert 'Tendai%20Moyo' in response.context['wa_link']

    def test_rate_limit_blocks_after_3_submissions(self, client, valid_contact_data, email_settings, mailoutbox):
        url = reverse('contact')
        for i in range(3):
            data = valid_contact_data.copy()
            data['timestamp'] = str(int(time.time()) - 5 - i)
            client.post(url, data)
        valid_contact_data['timestamp'] = str(int(time.time()) - 5)
        response = client.post(url, valid_contact_data, follow=True)
        assert response.status_code == 200
        assert 'Too many messages sent' in response.content.decode()
        assert len(mailoutbox) == 3

    def test_email_failure_shows_error(self, client, valid_contact_data, email_settings, monkeypatch):
        def mock_send(*args, **kwargs):
            raise Exception("SMTP error")
        monkeypatch.setattr('django.core.mail.EmailMessage.send', mock_send)
        url = reverse('contact')
        response = client.post(url, valid_contact_data, follow=True)
        assert response.status_code == 200
        content = response.content.decode().lower()
        assert 'failed to send' in content or 'whatsapp' in content

    def test_invalid_form_shows_errors(self, client):
        url = reverse('contact')
        response = client.post(url, {
            'name': '',
            'phone': '123',
            'subject': '',
            'message': '',
            'website': '',
            'timestamp': str(int(time.time()) - 5)
        })
        assert response.status_code == 200
        form = response.context['form']
        assert form.errors
        assert 'phone' in form.errors

class TestOtherViews:
    @pytest.mark.parametrize('url_name', [
        'home', 'about', 'services', 'branches', 'products', 'privacy',
    ])
    def test_static_pages_load(self, client, url_name):
        url = reverse(url_name)
        response = client.get(url)
        assert response.status_code == 200
