"""Development settings and globals."""

from __future__ import absolute_import

from os.path import join, normpath

from .base import *

import os


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend

#using this backend prints emails to console instead of mailing them
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#These settings should only work on Oberlin computers,
#   but hopefully not much tweaking is required.
#   Strangely, different versions of DEFAULT_FROM_EMAIL cause errors.
EMAIL_HOST = 'mail.cs.oberlin.edu'
EMAIL_HOST_USER = 'brempel'
EMAIL_HOST_PASSWORD = os.environ["BEN_EHP"]
DEFAUL_FROM_EMAIL = 'brempel@occs.cs.oberlin.edu'  
EMAIL_USE_TLS = True

########## END EMAIL CONFIGURATION


########## SITES CONFIGURATION

#How to change "example.com" (and info about the sites framework):
#http://stackoverflow.com/questions/5812985/django-password-reset-email-subject-line-contains-example-com
SIDE_ID = 2

########## END SITES CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': normpath(join(DJANGO_ROOT, 'default.db')),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
########## END CACHE CONFIGURATION


########## TOOLBAR CONFIGURATION
# See: http://django-debug-toolbar.readthedocs.org/en/latest/installation.html#explicit-setup
INSTALLED_APPS += (
    'debug_toolbar',
    'django.contrib.auth',
    'django.contrib.sites',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
INTERNAL_IPS = ('127.0.0.1',)
########## END TOOLBAR CONFIGURATION