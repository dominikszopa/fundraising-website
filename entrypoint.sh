#!/bin/sh

echo "Waiting for PostgreSQL to be ready..."

# Wait for PostgreSQL to be ready
until poetry run python -c "import psycopg2; psycopg2.connect(host='${DATABASE_HOST:-db}', port='${DATABASE_PORT:-5432}', user='${DATABASE_USER:-fundraiser}', password='${DATABASE_PASSWORD}', dbname='${DATABASE_NAME:-fundraising}')" 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing commands"

# Apply database migrations FIRST
poetry run python manage.py migrate

# Collect static files AFTER migrations
poetry run python manage.py collectstatic --noinput --clear

# Create the superuser if it doesn't exist
poetry run python manage.py createsuperuser --noinput --username admin --email foo@bar.com || true

# REMOVED: loaddata causes duplicate data on every restart
# Only load starting data manually when setting up a new environment
# poetry run python manage.py loaddata startingdata || true

echo "Initialization complete - starting server"

# Start the server
exec "$@"