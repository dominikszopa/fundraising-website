# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=fundraiser.settings.prod

# Set the working directory
WORKDIR /app/team_fundraising

# Install system dependencies
# libpq-dev is required for psycopg2 (PostgreSQL adapter)
RUN apt-get update && apt-get install -y \
    nginx \
    libpq-dev \
    gcc \
    && apt-get clean

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy the project files into the container
COPY . /app/team_fundraising/

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/team_fundraising/entrypoint.sh

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Make the entrypoint script executable
RUN chmod +x /app/team_fundraising/entrypoint.sh

# Install Gunicorn
RUN pip install gunicorn

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Set the entrypoint script
ENTRYPOINT ["/app/team_fundraising/entrypoint.sh"]

# Default command to run the application
# Railway requires binding to PORT env var, with increased timeout and workers
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --workers 4 \
    --worker-class gthread \
    --threads 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    fundraiser.wsgi:application
