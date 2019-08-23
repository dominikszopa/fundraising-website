from .base import *
import sys
import os

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# loaded from environment or .env file
SECRET_KEY = os.getenv('SECRET_KEY')

if (SECRET_KEY is None or SECRET_KEY == ''):
    print('You must set the SECRET_KEY environment variable to a long string')
    sys.exit()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = read_boolean(os.getenv('DEBUG'))

ALLOWED_HOSTS = ['*']

# Django debug toolbar
# https://django-debug-toolbar.readthedocs.io/en/0.11.0/installation.html

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True


PAYPAL_TEST = read_boolean(os.getenv('PAYPAL_TEST'))
PAYPAL_ACCOUNT = os.getenv('PAYPAL_ACCOUNT')
