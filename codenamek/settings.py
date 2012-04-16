# Django settings for codenamek project.
import os, sys
from ConfigParser import RawConfigParser

LOCAL_TEMPLATE_CONTEXT_PROCESSORS_PREFIX = LOCAL_TEMPLATE_CONTEXT_PROCESSORS = LOCAL_MIDDLEWARE_CLASSES_PREFIX = LOCAL_MIDDLEWARE_CLASSES = LOCAL_INSTALLED_APPS_PREFIX = LOCAL_INSTALLED_APPS = ()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))

STATIC_FILE_PATH = os.path.join(os.path.dirname(__file__), 'static')
TEMPLATE_FILE_PATH = os.path.join(os.path.dirname(__file__), 'templates')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS
RUN_ENV = 'DJANGO_ENV'

if os.getenv(RUN_ENV, '') == 'prod':
    DEBUG = False
    
    config = RawConfigParser()
    config.read('/environments/db/postgresql_prod.ini')
elif os.getenv(RUN_ENV, '') == 'staging':
    DEBUG = True
    
    config = RawConfigParser()
    config.read('/environments/db/postgresql_staging.ini')
else:
    DEBUG = True
    
    config = RawConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'developer.ini'))

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

EMAIL_USE_TLS = config.get('email', 'EMAIL_USE_TLS')
EMAIL_HOST = config.get('email', 'EMAIL_HOST')
EMAIL_HOST_USER = config.get('email', 'EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config.get('email', 'EMAIL_HOST_PASSWORD')
EMAIL_PORT = config.get('email', 'EMAIL_PORT')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/srv/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    STATIC_FILE_PATH,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'd$y-3-@&ljccptb1c)4fe9%qvy-6x%3!bw70t%b9yd=nqbik1*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    # 'django.template.loaders.eggs.Loader',
    # 'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'codenamek.urls'

TEMPLATE_DIRS = (
    TEMPLATE_FILE_PATH,
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_socketio',
    'registration',
    'profiles',
    # 'south',
    'django.contrib.admin',
    'codenamek.usermanagement',
    'codenamek.schools',
    'codenamek.whiteboard',
    'codenamek.chat',
)

# django needs to know what port to talk to for chat
SOCKETIO_HOST = 'staging.theknetwork.org'
SOCKETIO_PORT = 9000

ACCOUNT_ACTIVATION_DAYS = 7

AUTH_PROFILE_MODULE = 'usermanagement.UserProfile'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'dev': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

KHAN_URL = ""
CONSUMER_KEY = ""
CONSUMER_SECRET = ""


MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
try:
    from settings_local import *
except ImportError:
    pass

TEMPLATE_CONTEXT_PROCESSORS = \
    LOCAL_TEMPLATE_CONTEXT_PROCESSORS_PREFIX + \
    TEMPLATE_CONTEXT_PROCESSORS + \
    LOCAL_TEMPLATE_CONTEXT_PROCESSORS
MIDDLEWARE_CLASSES = \
    LOCAL_MIDDLEWARE_CLASSES_PREFIX + \
    MIDDLEWARE_CLASSES + \
    LOCAL_MIDDLEWARE_CLASSES
INSTALLED_APPS = \
    LOCAL_INSTALLED_APPS_PREFIX + \
    INSTALLED_APPS + \
    LOCAL_INSTALLED_APPS
