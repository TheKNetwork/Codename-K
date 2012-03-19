import os
import sys

sys.path = ['/srv/www'] + sys.path
os.environ['DJANGO_SETTINGS_MODULE'] = 'codenamek.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
