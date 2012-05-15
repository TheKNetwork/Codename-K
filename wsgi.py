from django.core.handlers.wsgi import WSGIHandler

import pinax.env
import os
import djcelery
djcelery.setup_loader()
# setup the environment for Django and Pinax
pinax.env.setup_environ(__file__)
os.environ['DJANGO_ENV'] = 'staging'

# set application for WSGI processing
application = WSGIHandler()

# mount this application at the webroot
applications = { '/': 'application' }