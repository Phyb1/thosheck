from.base import *
from decouple import config

DEBUG = True
SECRET_KEY = config('SECRET_KEY', default='dev-secret-key')
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Thosheck Dev <dev@thosheck.local>'
EMAIL_SUBJECT_PREFIX = '[Thosheck Dev] '

CONTACT_EMAIL = config('CONTACT_EMAIL', default='dev@thosheck.local')
CONTACT_WHATSAPP = config('CONTACT_WHATSAPP', default='263776298873')
