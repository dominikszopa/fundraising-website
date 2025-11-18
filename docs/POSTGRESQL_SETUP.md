# PostgreSQL Setup Guide

This guide helps you set up PostgreSQL for the fundraising website, including how to fix common authentication issues.

## Table of Contents
- [Common Error: Peer Authentication Failed](#common-error-peer-authentication-failed)
- [Complete Setup Instructions](#complete-setup-instructions)
- [Testing Your Connection](#testing-your-connection)
- [Troubleshooting](#troubleshooting)

## Common Error: Peer Authentication Failed

If you're seeing this error:
```
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL:  Peer authentication failed for user "postgres"
```

This means PostgreSQL is configured to only allow connections from system users that match the database username. Follow the steps below to fix it.

## Complete Setup Instructions

### Step 1: Locate and Edit pg_hba.conf

The `pg_hba.conf` file controls PostgreSQL authentication methods.

**Find the file location:**

```bash
# On Ubuntu/Debian/WSL
sudo find /etc/postgresql -name pg_hba.conf

# Common locations:
# /etc/postgresql/14/main/pg_hba.conf
# /etc/postgresql/15/main/pg_hba.conf
# /etc/postgresql/16/main/pg_hba.conf
```

**Edit the file:**

```bash
# Replace the version number with your PostgreSQL version
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

### Step 2: Change Authentication Method

Find the lines that look like this:

```
# "local" is for Unix domain socket connections only
local   all             postgres                                peer
local   all             all                                     peer
```

**Change "peer" to "md5"** (password authentication):

```
# "local" is for Unix domain socket connections only
local   all             postgres                                md5
local   all             all                                     md5
```

**Alternative:** Use `scram-sha-256` for stronger encryption (PostgreSQL 10+):

```
local   all             postgres                                scram-sha-256
local   all             all                                     scram-sha-256
```

Save the file (Ctrl+O, Enter, Ctrl+X in nano).

### Step 3: Restart PostgreSQL

```bash
# On Ubuntu/Debian/WSL
sudo service postgresql restart

# Verify it's running
sudo service postgresql status
```

### Step 4: Set Password for postgres User

Now that password authentication is enabled, you can set a password:

```bash
# Connect as the postgres system user (this still works with peer authentication)
sudo -u postgres psql

# Inside psql, set a password:
ALTER USER postgres WITH PASSWORD 'your_strong_password';

# Exit psql
\q
```

### Step 5: Test Connection with Password

```bash
# This should now prompt for a password
psql -U postgres -h localhost

# Or specify the password in the connection
PGPASSWORD=your_strong_password psql -U postgres -h localhost
```

### Step 6: Create Database and User for Django

```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Create the database
CREATE DATABASE fundraising;

# Create a dedicated user (recommended for security)
# CREATEDB permission is needed for Django to create test databases
CREATE USER fundraiser WITH PASSWORD 'your_fundraiser_password' CREATEDB;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE fundraising TO fundraiser;

# For PostgreSQL 15+, also grant schema permissions
\c fundraising
GRANT ALL ON SCHEMA public TO fundraiser;

# Exit
\q
```

### Step 7: Update Your .env File

Edit your `.env` file with the credentials:

```
DATABASE_NAME=fundraising
DATABASE_USER=fundraiser
DATABASE_PASSWORD=your_fundraiser_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

**Important:** If using `localhost`, you may also need to ensure the `pg_hba.conf` has host-based authentication:

```
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
```

### Step 8: Run Django Migrations

```bash
python3 manage.py migrate
```

## Testing Your Connection

### Test with psql Command Line

```bash
# Test with username and password
psql -U fundraiser -h localhost -d fundraising
```

### Test with Python

Create a test script:

```python
import psycopg2

try:
    conn = psycopg2.connect(
        dbname="fundraising",
        user="fundraiser",
        password="your_fundraiser_password",
        host="localhost",
        port="5432"
    )
    print("✓ Connection successful!")
    conn.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

## Troubleshooting

### Still Getting "Peer authentication failed"?

1. **Make sure you restarted PostgreSQL** after editing pg_hba.conf
   ```bash
   sudo service postgresql restart
   ```

2. **Check if your changes were saved:**
   ```bash
   sudo cat /etc/postgresql/16/main/pg_hba.conf | grep -A 5 "local"
   ```

3. **Make sure you're connecting to localhost:**
   - Use `-h localhost` in psql commands
   - In Django settings, use `HOST: localhost` (not empty string)

### "Role does not exist"

Create the user first:
```bash
sudo -u postgres psql
CREATE USER fundraiser WITH PASSWORD 'password';
```

### "Database does not exist"

Create the database:
```bash
sudo -u postgres psql
CREATE DATABASE fundraising;
```

### Permission Denied on Schema (PostgreSQL 15+)

PostgreSQL 15 changed default permissions. After creating the database:
```bash
psql -U postgres -h localhost -d fundraising
GRANT ALL ON SCHEMA public TO fundraiser;
GRANT ALL ON ALL TABLES IN SCHEMA public TO fundraiser;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO fundraiser;
```

### Can't Find pg_hba.conf

```bash
# Ask PostgreSQL where it is
sudo -u postgres psql -c "SHOW hba_file;"
```

### PostgreSQL Won't Start After Editing pg_hba.conf

You may have a syntax error. Check the logs:
```bash
# On Ubuntu/Debian/WSL
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

Restore from backup if needed:
```bash
sudo cp /etc/postgresql/16/main/pg_hba.conf.backup /etc/postgresql/16/main/pg_hba.conf
sudo service postgresql restart
```

## Quick Reference

### Common PostgreSQL Commands

```bash
# Connect as postgres user
sudo -u postgres psql

# Connect as specific user to specific database
psql -U fundraiser -h localhost -d fundraising

# List databases
\l

# List users
\du

# Connect to database
\c fundraising

# List tables
\dt

# Show current connection info
\conninfo

# Quit
\q
```

### Security Notes

- **Never commit passwords** to version control
- Use strong, unique passwords for production
- Consider using environment-specific users (dev vs prod)
- In production, use more restrictive pg_hba.conf settings
- Consider using SSL/TLS connections for production
