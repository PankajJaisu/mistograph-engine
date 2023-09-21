
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mistograph_core.settings')
application = get_wsgi_application()
app = application #add here
