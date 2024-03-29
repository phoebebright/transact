# settings for viv
import sys, os
import logging
ROOT = lambda base : os.path.abspath(os.path.join(os.path.dirname(__file__), base).replace('\\','/'))

sys.path.insert(0, '/home/django/transact/')
sys.path.insert(0, '/home/django/')

gettext = lambda s: s

SITE_URL = "http://api.transactcarbon.com"



PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = True

# if email in debug mode - don't sent externally
EMAIL_DEBUG = True
# where emails are sent in debug mode
TEST_EMAIL = 'phoebebright310+trans@gmail.com'

'''
EMAIL_HOST = "mail.tinywho.com"
EMAIL_PORT = "25"
EMAIL_HOST_USER = "info@djbono.com"
EMAIL_HOST_PASSWORD = "highyellow"
'''

ADMINS = (
     ('Phoebe Bright', 'phoebebright310@gmail.com'),
)

MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = "info@transactcarbon.com"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'transact',   
        'USER': 'transact',               
        'PASSWORD': 'h8d6e555',           
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

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
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
    'middleware.cors.XsSharing',
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
    os.path.join(os.path.dirname(__file__), "templates/registration"),
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
    'api',
    'web',
    'webtest',
    'utils',
    'django_coverage',

)

LOGIN_REDIRECT_URL = "/"

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

APILOG = "/home/django/transact/api.log"
APILOG_LEVEL = logging.DEBUG

DATE_FORMAT = "M d, Y"
DATE_PY_FORMAT = "%b %d, %Y"
DATETIME_FORMAT = "M d, Y H:i"
DATETIME_PY_FORMAT = "%b %d, %Y %H:%i"
SHORT_DATE_FORMAT = "dM"
SHORT_DATETIME_FORMAT = 'dM H:i'

AUTH_PROFILE_MODULE = 'web.UserProfile'

DEMO_USERNAME = 'test'
DEMO_PASSWORD = 'silicon'


CACHE_PREFIX = 'TransAct'
CACHE_TIMEOUT = 300
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'TransAct',
    }
}

#django_selenium tests
TEST_RUNNER = 'django_selenium.selenium_runner.SeleniumTestRunner'
SELENIUM_DRIVER = 'Firefox'
#SELENIUM_TEST_PRODUCTION = True
SELENIUM_BASE_URL = "http://transactcarbon.com"
SELENIUM_HTTP_AUTH_URL = "http://testuser:silicon@transactcarbon.com/"
try:
    from settings_local import *
except ImportError:
    pass

TEST_RUNNER = 'django_coverage.coverage_runner.CoverageRunner'

