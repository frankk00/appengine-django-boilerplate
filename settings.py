# Initialize App Engine and import the default settings (DB backend, etc.).
# If you want to use a different backend you have to remove all occurences
# of "djangoappengine" from this file.
from djangoappengine.settings_base import *
import os

# Uncomment this if you're using the high-replication datastore.
# TODO: Once App Engine fixes the "s~" prefix mess we can remove this.
#DATABASES['default']['HIGH_REPLICATION'] = True

# Activate django-dbindexer for the default database
DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}
DBINDEXER_SITECONF = 'dbindexes'

SECRET_KEY = '=r-$b*8hglm+858&9t043hlm6-&6-3d3vfc4((7yd0dbrakhvi'
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

INSTALLED_APPS = (
#    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'djangotoolbox',
    'dbindexer',

    # djangoappengine should come last, so it can override a few manage.py commands
    'djangoappengine',
    'mediagenerator',

    # project apps
)

MIDDLEWARE_CLASSES = (
    # This loads the index definitions, so it has to come first
    'dbindexer.middleware.DBIndexerMiddleware',
    #mediagenerator middleware
    'mediagenerator.middleware.MediaMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',

    #project context processors
)

# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'

ADMIN_MEDIA_PREFIX = '/media/admin/'
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)

ROOT_URLCONF = 'urls'

#media generator related settings
#from django.conf import settings
MEDIA_DEV_MODE = False
DEV_MEDIA_URL = '/devstatic/'
PRODUCTION_MEDIA_URL = '/static/'
GLOBAL_MEDIA_DIRS = (os.path.join(PROJECT_ROOT, 'media'), )

YUICOMPRESSOR_PATH = os.path.join(PROJECT_ROOT, 'yuicompressor-2.4.6.jar')
if os.path.exists(YUICOMPRESSOR_PATH):
    ROOT_MEDIA_FILTERS = {
        'css': 'mediagenerator.filters.yuicompressor.YUICompressor',
        'js': 'mediagenerator.filters.yuicompressor.YUICompressor',
    }

#media bundles if local
MEDIA_BUNDLES = (
    ('creation.js', 'js/creation.js',),
)


#jinja2 globals and extensions
"""
from mediagenerator.utils import media_url

JINJA2_GLOBALS = {
    'media_url': media_url,
}
"""

JINJA2_EXTENSIONS = (
    'jinja2loader.extensions.URLExtension',
    'jinja2loader.extensions.CsrfExtension',
    'jinja2.ext.do',
    'mediagenerator.contrib.jinja2ext.MediaExtension',
)

#jinja2 template loader
TEMPLATE_LOADERS = (
    'jinja2loader.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, "templates/"),)



#load the local developer settings if possible
try:
    from settings_local import *
except ImportError:
    pass




#TODO: settings.MEDIA_DEV_MODE = True
#TODO: media bundles
#dev: MEDIA_BUNDLES = ()
#prod: settings.MEDIA_BUNDLES = ()
