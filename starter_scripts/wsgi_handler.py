import sys
import os

sys.path.append("/var/www")
sys.path.append("/var/www/quinnan")
sys.path.append("/var/www/quinnan/quinnan")
os.environ['DJANGO_SETTINGS_MODULE'] = 'quinnan.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

