from .base import *
import os, sys

# Debug must be off in production
DEBUG = False

# SECRET_KEY is read from environment variable for security
SECRET_KEY = os.environ.get('SECRET_KEY')

if (SECRET_KEY is None):
    print('You must set the SECRET_KEY environment variable to a long string')
    sys.exit()

ALLOWED_HOSTS = [
    'donations.triplecrownforheart.ca',
    'fundraising.triplecrownforheart.ca',
    'localhost'
    ]

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'fundraising@triplecrownforheart.ca'
EMAIL_USE_TLS = True

EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')

if (EMAIL_HOST_PASSWORD is None):
    print('You must set the EMAIL_PASSWORD environment variable')
    sys.exit()

# Paypal configuration
# To switch to the sandbox account, set PAYPAL_TEST = True
# and set PAYPAL_ACCOUNT to 'stephen-facilitator@triplecrownforheart.com'

PAYPAL_TEST = False
# PAYPAL_ACCOUNT = 'stephen-facilitator@triplecrownforheart.com'
PAYPAL_ACCOUNT = 'stephen@triplecrownforheart.com'
