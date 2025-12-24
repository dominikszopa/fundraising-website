from .base import *
import os

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# Google reCAPTCHA settings for development
# Use Google's official test keys (always pass validation - for testing)
# In production, real keys must be provided via environment variables
RECAPTCHA_PUBLIC_KEY = os.getenv(
    'RECAPTCHA_PUBLIC_KEY',
    '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
)
RECAPTCHA_PRIVATE_KEY = os.getenv(
    'RECAPTCHA_PRIVATE_KEY',
    '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
)

# Silence RECAPTCHA test key warning in development/CI
SILENCED_SYSTEM_CHECKS = [
    'django_recaptcha.recaptcha_test_key_error',
]

# Whitenoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

if TESTING:
    STORAGES["staticfiles"] = {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }

# SECURITY WARNING: keep the secret key used in production secret!
# loaded from environment or .env file
SECRET_KEY = get_env_variable('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = read_boolean(get_env_variable('DEBUG'))

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

# AWS SES settings (with defaults for dev/test environments)
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_SES_REGION = os.getenv('AWS_SES_REGION', 'us-east-1')
DEFAULT_FROM_EMAIL = 'fundraising@triplecrownforheart.ca'

PAYPAL_TEST = read_boolean(os.getenv('PAYPAL_TEST'))
PAYPAL_ACCOUNT = os.getenv('PAYPAL_ACCOUNT')
