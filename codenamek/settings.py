# Django settings for codenamek project.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))

# THESE ARE THE DEFAULT DB SETTINGS.
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''
DATABASE_ENGINE = 'django.db.backends.sqlite3'
DATABASE_NAME = '/srv/www/codenamek/sqlite.db'

# THIS ENVIRONMENT VARIABLE IS LOADED BY THE DJANGO.WSGI FILE
# AT RUNTIME BY THE RACKSPACE SERVER. 
if os.getenv("DJANGO_ENV") == 'RACKSPACE':
    DATABASE_USER = 'knet'
    DATABASE_PASSWORD = 'lsmTO2012'
    DATABASE_HOST = 'localhost'
    DATABASE_PORT = ''
    DATABASE_ENGINE = 'django.db.backends.postgresql_psycopg2'
    DATABASE_NAME = 'codenamek_dev'

# IF YOU WANT TO RUN YOUR OWN DB SETTINGS, YOU CAN OPTIONALLY
# CREATE YOUR OWN ENVIRONMENT VARIABLE AND DETECT THAT VARIABLE
# HERE. COPY AND PASTE THIS SECTION, UNCOMMENT IT AND THEN
# SET YOUR APPROPRIATE DATABASE SETTINGS. DON'T FORGET TO RUN
# SYNCDB!!
# if os.getenv("DJANGO_ENV") == 'YOUR VARIABLE':
#    DATABASE_USER = 'YOUR USER'
#    DATABASE_PASSWORD = 'YOUR PASSWORD'
#    DATABASE_HOST = 'localhost'
#    DATABASE_PORT = ''
#    DATABASE_ENGINE = 'django.db.backends.YOUR_BACKEND_DRIVER'
#    DATABASE_NAME = 'YOUR_DB_NAME'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,
        'NAME': DATABASE_NAME, 
        'USER': DATABASE_USER,                      
        'PASSWORD': DATABASE_PASSWORD,              
        'HOST': DATABASE_HOST,                      
        'PORT': DATABASE_PORT,
    }
}

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
    '/srv/www/codenamek/static',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'd$y-3-@&ljccptb1c)4fe9%qvy-6x%3!bw70t%b9yd=nqbik1*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
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
    "/srv/www/codenamek/templates",
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
    'codenamek.classroom',
    'codenamek.whiteboard',
    'registration',
    'profiles',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

ACCOUNT_ACTIVATION_DAYS = 7

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'knetserverinfo@gmail.com'
EMAIL_HOST_PASSWORD = 'lsmto2012'
EMAIL_PORT = 587

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
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
