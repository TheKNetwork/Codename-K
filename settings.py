# -*- coding: utf-8 -*-
# Django settings for basic pinax project.

import os.path
import posixpath

# INIT THE CONFIG VARIABLE TO READ INI FILES
from ConfigParser import RawConfigParser
config = RawConfigParser()

# import the khan api custom app API call explorer to connect to KHAN
from khanapi.api_explorer_oauth_client import APIExplorerOAuthClient

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SITE_NAME = "The K-Network"
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

# django-compressor is turned off by default due to deployment overhead for
# most users. See <URL> for more information
COMPRESS = False

INTERNAL_IPS = [
    "127.0.0.1",
]

ADMINS = [
    # ("Your Name", "your_email@domain.com"),
]

MANAGERS = ADMINS

# Since database defaults are now set, we can optionally
# override them with calls out to environment specific INI files
RUN_ENV = 'DJANGO_ENV'
SITE_ROOT = 'www.theknetwork.org'
IS_DEFAULT = True

if os.getenv(RUN_ENV, '') == 'prod':
    DEBUG = False
    SITE_ROOT = 'prod.theknetwork.org'
    config.read('/environments/db/postgresql_prod.ini')
    IS_DEFAULT = False
elif os.getenv(RUN_ENV, '') == 'staging':
    DEBUG = True
    SITE_ROOT = 'staging.theknetwork.org'
    config.read('/environments/db/postgresql_staging.ini')
    IS_DEFAULT = False
else:
    DEBUG = True
    SITE_ROOT = 'localhost:8000'
    config.read(os.getenv('KNET_INI', '../knet.ini'))

ENGINE = 'django.db.backends.sqlite3'
USER = ''
PASSWORD = ''
HOST = ''
PORT = ''
NAME = 'sqlite.db'

if not IS_DEFAULT:
    ENGINE = config.get('database', 'ENGINE')
    USER = config.get('database', 'USER')
    PASSWORD = config.get('database', 'PASSWORD')
    HOST = config.get('database', 'HOST')
    PORT = config.get('database', 'PORT')
    NAME = config.get('database', 'NAME')

DATABASES = {
    'default': {
        'ENGINE': ENGINE,
        'NAME': NAME,
        'USER': USER,
        'PASSWORD': PASSWORD,
        'HOST': HOST,
        'PORT': PORT,
    }
}

  
import djcelery  
djcelery.setup_loader() 
BROKER_URL = "django://" # tell kombu to use the Django database as the message queue  
BROKER_BACKEND = "django"
CELERY_IMPORTS = ('schools.views',)

from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    "runs-every-5-minutes": {
        "task": "khanapi.async.UpdateAllUsersRelatedInfo",
        "schedule": timedelta(seconds=60*5),
    },
}

# django needs to know what port to talk to for chat
SOCKETIO_HOST = 'localhost'
SOCKETIO_PORT = 9000

# KHAN API Stuff
KHAN_KEY = config.get('khanapi','KHAN_KEY')
KHAN_SECRET = config.get('khanapi','KHAN_SECRET')

# ASYNC and TASK QUEUEING/SCHEDULING

# Keep around an instance of the client. It's reusable because all the
# stateful stuff is passed around as parameters.
CLIENT = APIExplorerOAuthClient("http://www.khanacademy.org",
                                KHAN_KEY,
                                KHAN_SECRET
        )

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "US/Eastern"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = "/site_media/static/"

# Additional directories which hold static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "static"),
]

STATICFILES_FINDERS = [
    "staticfiles.finders.FileSystemFinder",
    "staticfiles.finders.AppDirectoriesFinder",
    "staticfiles.finders.LegacyAppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Subdirectory of COMPRESS_ROOT to store the cached media files in
COMPRESS_OUTPUT_DIR = "cache"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "p=ahl@)offrpf0y@l0ne+3*t-%#*oh0n6f(j31e*ny^u+wbqy7"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.load_template_source",
    "django.template.loaders.app_directories.load_template_source",
]

MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_openid.consumer.SessionConsumer",
    "django.contrib.messages.middleware.MessageMiddleware",
    "pinax.apps.account.middleware.LocaleMiddleware",
    "pagination.middleware.PaginationMiddleware",
    "pinax.middleware.security.HideSensistiveFieldsMiddleware",
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    
    "staticfiles.context_processors.static",
    
    "pinax.core.context_processors.pinax_settings",
    
    "pinax.apps.account.context_processors.account",
    
    "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
]

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.humanize",
    
    'kombu.transport.django',  
    'djcelery',
    
    "pinax.templatetags",
    
    # theme
    # "pinax_theme_bootstrap",
    # "knet_theme",
    
    # external
    "notification", # must be first
    "staticfiles",
    "compressor",
    "debug_toolbar",
    "mailer",
    "django_openid",
    "timezones",
    "emailconfirmation",
    "announcements",
    "pagination",
    "idios",
    "metron",
    
    # Pinax
    "pinax.apps.account",
    "pinax.apps.signup_codes",
    
    # project
    "khanapi",
    "about",
    "profiles",
    "schools",
    "chat",
    "whiteboard",
]

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

EMAIL_BACKEND = "mailer.backend.DbBackend"

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

AUTH_PROFILE_MODULE = "profiles.Profile"
NOTIFICATION_LANGUAGE_MODULE = "account.Account"

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_USE_OPENID = False
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = False
ACCOUNT_EMAIL_AUTHENTICATION = False
ACCOUNT_UNIQUE_EMAIL = EMAIL_CONFIRMATION_UNIQUE_EMAIL = False

AUTHENTICATION_BACKENDS = [
    "pinax.apps.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/account/login/" # @@@ any way this can be a url name?
LOGIN_REDIRECT_URLNAME = "homeroom"
LOGOUT_REDIRECT_URLNAME = "home"

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

if os.getenv(RUN_ENV, '') == 'staging':
    print "Cache: MEMCACHED (STAGING)"
    CACHES = {
    'memcached': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    },}
else:
    print "Cache: DISK/TMP (DEV)"
    CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    },}
    

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
