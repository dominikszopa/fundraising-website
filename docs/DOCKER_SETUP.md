# Docker Setup Guide

This guide explains the different Docker configurations available for the fundraising website.

## Overview

The project supports two Docker deployment modes:

1. **Self-Contained Mode** (default) - PostgreSQL runs in a Docker container
2. **Local PostgreSQL Mode** - Docker containers connect to host PostgreSQL database

## File Structure

- `docker-compose.yml` - Base configuration (PostgreSQL container + Django)
- `docker-compose.prod.yml` - Production overrides
- `docker-compose.override.yml.example` - Example for using local PostgreSQL
- `docker-compose.override.yml` - Your local config (gitignored)

## Mode 1: Self-Contained (Default)

**Best for:** Production, testing, isolated environments

### What it does:
- Runs PostgreSQL 16 in a Docker container
- Persists data in `postgres_data` volume
- Complete isolation from host system
- Everything runs in Docker

### Usage:

```bash
# Development
docker-compose up -d

# Production (with production settings)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Configuration:

Only need `.env` file with:
- `SECRET_KEY`
- `DATABASE_PASSWORD`

Database connection is automatically configured to use the `db` service.

## Mode 2: Local PostgreSQL

**Best for:** Development when you want to share data between local dev and Docker

### What it does:
- Django runs in Docker
- Connects to PostgreSQL running on your host machine
- Shares database with local development

### Setup:

1. Install and configure local PostgreSQL (see main README)

2. Create override file:
   ```bash
   cp docker-compose.override.yml.example docker-compose.override.yml
   ```

3. Edit `docker-compose.override.yml` and set `DATABASE_HOST`:

   **For Mac/Windows:**
   ```yaml
   - DATABASE_HOST=host.docker.internal
   ```

   **For Linux:**
   ```yaml
   - DATABASE_HOST=172.17.0.1
   ```

4. Configure PostgreSQL to accept connections from Docker:

   **For Linux:**
   Edit `pg_hba.conf` and add:
   ```
   host    all             all             172.17.0.0/16           md5
   ```

   **For Mac/Windows:**
   Connections via `host.docker.internal` use localhost, so no changes needed if you already have `host all all 127.0.0.1/32 md5`

5. Restart PostgreSQL:
   ```bash
   sudo service postgresql restart
   ```

6. Start Docker:
   ```bash
   docker-compose up -d
   ```

## Networking Details

### How Docker Reaches Host PostgreSQL

**Mac/Windows (Docker Desktop):**
- Uses special DNS name `host.docker.internal`
- Automatically resolves to host machine
- Works out of the box

**Linux:**
- Uses Docker bridge network IP: `172.17.0.1`
- This is the default gateway IP of the Docker bridge
- Requires pg_hba.conf configuration

### Verifying Connection

Test from inside the container:

```bash
# Get into the container
docker-compose exec gunicorn bash

# Test PostgreSQL connection
python -c "import psycopg2; psycopg2.connect(host='172.17.0.1', port='5432', user='fundraiser', password='your_password', dbname='fundraising')"
```

## Switching Between Modes

### From Self-Contained to Local PostgreSQL:

1. Stop containers: `docker-compose down`
2. Create `docker-compose.override.yml` (see Mode 2 setup)
3. Start: `docker-compose up -d`

### From Local PostgreSQL to Self-Contained:

1. Stop containers: `docker-compose down`
2. Remove override file: `rm docker-compose.override.yml`
3. Start: `docker-compose up -d`

## Production Deployment

For production, use the self-contained mode with production overrides:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Production settings:**
- PostgreSQL port not exposed to host
- Code baked into image (not mounted)
- Production Django settings
- Ready for SSL/TLS with Nginx

## Troubleshooting

### Can't connect to host PostgreSQL from Docker

**Check PostgreSQL is listening:**
```bash
sudo netstat -plnt | grep postgres
```

Should show: `0.0.0.0:5432` or `127.0.0.1:5432`

**Check pg_hba.conf:**
```bash
sudo cat /etc/postgresql/16/main/pg_hba.conf | grep -v "^#"
```

Should have appropriate entry for Docker network.

**Check from container:**
```bash
docker-compose exec gunicorn ping -c 1 host.docker.internal  # Mac/Windows
docker-compose exec gunicorn ping -c 1 172.17.0.1            # Linux
```

### PostgreSQL denies connection

Check PostgreSQL logs:
```bash
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

Common issues:
- Wrong password in .env
- pg_hba.conf not configured for Docker network
- PostgreSQL not restarted after config change

### Override file not working

Docker Compose only automatically loads `docker-compose.override.yml` (exact name).

Check which files are being used:
```bash
docker-compose config
```

This shows the merged configuration.

## Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_HOST | db | PostgreSQL host (use `host.docker.internal` or `172.17.0.1` for local) |
| DATABASE_PORT | 5432 | PostgreSQL port |
| DATABASE_NAME | fundraising | Database name |
| DATABASE_USER | fundraiser | Database user |
| DATABASE_PASSWORD | (from .env) | Database password |

### Docker Compose Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (deletes database data!)
docker-compose down -v

# Rebuild images
docker-compose build

# Execute command in container
docker-compose exec gunicorn python manage.py shell

# View merged configuration
docker-compose config
```
