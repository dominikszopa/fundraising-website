#!/bin/sh

# Apply database migrations
poetry run python manage.py migrate

# Create the superuser if it doesn't exist
poetry run python manage.py createsuperuser --noinput --username admin --email foo@bar.com || true

# Load the starting data
poetry run python manage.py loaddata startingdata || true

# Start the server
exec "$@"