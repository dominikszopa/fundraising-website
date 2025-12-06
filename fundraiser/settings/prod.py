from .base import *
import sys
import os


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

# SECRET_KEY is read from environment variable for security
SECRET_KEY = get_env_variable('SECRET_KEY')

# Allow DEBUG to be controlled by environment variable for testing
# WARNING: Set to False in production after testing
DEBUG = read_boolean(os.getenv('DEBUG', 'False'))

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(",")
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS').split(",")

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10  # Timeout after 10 seconds to prevent worker timeout

# Make links sent be HTTPS
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# Paypal configuration
# To switch to the sandbox account, set PAYPAL_TEST = True
# and set PAYPAL_ACCOUNT to 'stephen-facilitator@triplecrownforheart.com'

PAYPAL_TEST = read_boolean(os.getenv('PAYPAL_TEST'))
PAYPAL_ACCOUNT = os.getenv('PAYPAL_ACCOUNT')
