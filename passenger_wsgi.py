import os
import sys

sys.path.insert(0, '/home/mathxuco/thosheck/public_html')
os.environ['DJANGO_SETTINGS_MODULE'] = 'thosheck.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()