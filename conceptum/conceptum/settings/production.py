"""Production settings and globals."""

from __future__ import absolute_import

from json import load
from os import environ
import os.path

from .base import *

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured

secrets_file_name = os.path.join(DJANGO_ROOT, 'secrets.json')

def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

def get_secrets_setting(secrets, setting):
    """
    Get the requested configuration option from the secrets json file or
    throw an exception.
    """
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Key %s missing from secrets file (%s)." % (setting, secrets_file_name)
        raise ImproperlyConfigured(error_msg)

secrets_file = open(secrets_file_name)

secrets = load(secrets_file)

secrets_file.close()

########## HOST CONFIGURATION
# See: https://docs.djangoproject.com/en/1.5/releases/1.5/#allowed-hosts-required-in-production
ALLOWED_HOSTS = ['.swarthmore.edu', '.swarthmore.edu.', 'localhost', 'wasabi']
########## END HOST CONFIGURATION

########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = get_secrets_setting(secrets, 'email_host')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = get_secrets_setting(secrets, 'email_password')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = get_secrets_setting(secrets, 'email_user')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = get_secrets_setting(secrets, 'email_port')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s %s] ' % (SITE_NAME, CI_COURSE)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = get_secrets_setting(secrets, 'email_tls')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER

DEFAULT_FROM_EMAIL = get_secrets_setting(secrets, 'default_from_email')
########## END EMAIL CONFIGURATION

########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_secrets_setting(secrets, 'db_name'),
        'USER': get_secrets_setting(secrets, 'db_user'),
        'PASSWORD': get_secrets_setting(secrets, 'db_pass'),
        'HOST': get_secrets_setting(secrets, 'db_host'),
        'PORT': get_secrets_setting(secrets, 'db_port'),
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


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = get_secrets_setting(secrets, 'secret_key')
########## END SECRET CONFIGURATION
