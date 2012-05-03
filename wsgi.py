from django.core.handlers.wsgi import WSGIHandler

import pinax.env


# setup the environment for Django and Pinax
pinax.env.setup_environ(__file__)


# set application for WSGI processing
application = WSGIHandler()

# mount this application at the webroot
applications = { '/': 'application' }