from .base import *
import sys
import os


# Whitenoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STORAGES = {
    "default": {
        # Media files (user uploads) use FileSystemStorage for saving
        # but are served by WhiteNoise in production (configured in wsgi.py)
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # Static files (CSS, JS, images) are served by WhiteNoise middleware
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Template caching - cache compiled templates in production
# Must disable APP_DIRS when defining custom loaders
TEMPLATES[0]['APP_DIRS'] = False
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Whitenoise configuration for better static file performance
WHITENOISE_AUTOREFRESH = False  # Disable in production
WHITENOISE_USE_FINDERS = False  # Don't search for files, use manifest
WHITENOISE_MAX_AGE = 31536000  # 1 year cache for static files

# SECRET_KEY is read from environment variable for security
SECRET_KEY = get_env_variable('SECRET_KEY')

# Allow DEBUG to be controlled by environment variable for testing
# WARNING: Set to False in production after testing
DEBUG = read_boolean(os.getenv('DEBUG', 'False'))

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(",") if os.getenv('ALLOWED_HOSTS') else []
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(",") if os.getenv('CSRF_TRUSTED_ORIGINS') else []

# AWS SES email configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SES_REGION = os.getenv('AWS_SES_REGION', 'us-east-1')
DEFAULT_FROM_EMAIL = 'fundraising@triplecrownforheart.ca'

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
