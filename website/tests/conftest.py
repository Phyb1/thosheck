import time
import pytest
from django.conf import settings

@pytest.fixture
def valid_contact_data():
    """
    Valid contact form data with timestamp 5 seconds in past.
    Phone is 077 format to test normalization to +263.
    """
    return {
        'name': 'Tendai Moyo',
        'phone': '0771234567',
        'subject': 'prescription',
        'message': 'Do you have Panadol in stock?',
        'website': '', # honeypot must be empty
        'timestamp': str(int(time.time()) - 5)
    }

@pytest.fixture
def email_settings(settings):
    """
    Override EMAIL_BACKEND to locmem for tests.
    Use as: def test_something(self, client, email_settings, mailoutbox):
    """
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    settings.EMAIL_SUBJECT_PREFIX = '[Thosheck Test] '
    settings.CONTACT_EMAIL = 'test@thosheck.co.zw'
    settings.CONTACT_WHATSAPP = '263771234567'
    settings.DEFAULT_FROM_EMAIL = 'noreply@thosheck.co.zw'
    return settings

@pytest.fixture(autouse=True)
def clear_cache():
    """
    Auto-clear Django cache before each test.
    Prevents rate limit state leaking between tests.
    """
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()

@pytest.fixture
def whatsapp_settings(settings):
    """Set WhatsApp number for tests that check wa_link"""
    settings.CONTACT_WHATSAPP = '263771234567'
    return settings
