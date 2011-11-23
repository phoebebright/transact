# settings for viv
import sys, os
ROOT = lambda base : os.path.abspath(os.path.join(os.path.dirname(__file__), base).replace('\\','/'))

sys.path.insert(0, '//home/django/transact/')
sys.path.insert(0, '//home/django/')

gettext = lambda s: s

SITE_URL = "http://transactcarbon.com"


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = True

# if email in debug mode - don't sent externally
EMAIL_DEBUG = False
# where emails are sent in debug mode
TEST_EMAIL = 'phoebebright310+transact@gmail.com'

ADMINS = (
     ('Phoebe Bright', 'phoebebright310@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'transact',   
        'USER': 'root',               
        'PASSWORD': '578632',           
        'HOST': '',                  
        'PORT': '',                 
    }
}

TIME_ZONE = 'Europe/Dublin'
LANGUAGE_CODE = 'en-gb'
USE_I18N = True
USE_L10N = True
SITE_ID = 1



# Absolute path to the directory that holds media.
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'site_media')
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    ROOT('shared_static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9h!pbkmf#w-jeo^n&!mq*+3-w=5v0f^3zy)ov3@tqh%ed0y0@@'

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

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "django.core.context_processors.csrf"
)


ROOT_URLCONF = 'transact.urls'


TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)


INSTALLED_APPS = (
    'keyedcache',
    'livesettings',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'web',
    'webtest',
    'api',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

DATE_FORMAT = "M d, Y"
DATE_PY_FORMAT = "%b %d, %Y"
DATETIME_FORMAT = "M d, Y H:i"
DATETIME_PY_FORMAT = "%b %d, %Y %H:%i"
SHORT_DATE_FORMAT = "dM"
SHORT_DATETIME_FORMAT = 'dM H:i'

AUTH_PROFILE_MODULE = 'web.UserProfile'

CACHE_PREFIX = 'TransAct'
CACHE_TIMEOUT = 300
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'TransAct',
    }
}


try:
    from settings_local import *
    print "local settings imported successfully"
except ImportError:
    print "no local settings"