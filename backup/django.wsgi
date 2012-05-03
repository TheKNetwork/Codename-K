import os
import sys

sys.path = ['/srv/www'] + sys.path
os.environ['DJANGO_SETTINGS_MODULE'] = 'codenamek.settings'
os.environ['DJANGO_ENV'] = 'RACKSPACE'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
