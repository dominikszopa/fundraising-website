from .base import *
import os

# Debug must be off in production
DEBUG = False

# SECRET_KEY is read from environment variable for security
SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = [
    'donations.triplecrownforheart.ca',
    'fundraising.triplecrownforheart.ca',
    'localhost'
    ]
