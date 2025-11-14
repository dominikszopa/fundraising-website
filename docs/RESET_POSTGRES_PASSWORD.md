# How to Reset PostgreSQL postgres User Password

If you've enabled password authentication but don't know the postgres user password, follow these steps:

## Option 1: Temporarily Use Peer Authentication (Recommended)

1. **Edit pg_hba.conf to temporarily allow peer authentication for postgres user:**

   ```bash
   sudo nano /etc/postgresql/16/main/pg_hba.conf
   ```

2. **Change ONLY the first line to use peer temporarily:**

   ```
   # Temporarily use peer for postgres, md5 for everyone else
   local   all             postgres                                peer
   local   all             all                                     md5
   ```

3. **Restart PostgreSQL:**

   ```bash
   sudo service postgresql restart
   ```

4. **Now connect without password and set one:**

   ```bash
   sudo -u postgres psql
   ```

   Inside psql:
   ```sql
   ALTER USER postgres WITH PASSWORD 'your_strong_password';
   \q
   ```

5. **Change pg_hba.conf back to md5:**

   ```bash
   sudo nano /etc/postgresql/16/main/pg_hba.conf
   ```

   ```
   # Now use md5 for everything
   local   all             postgres                                md5
   local   all             all                                     md5
   ```

6. **Restart PostgreSQL again:**

   ```bash
   sudo service postgresql restart
   ```

7. **Test with password:**

   ```bash
   psql -U postgres -h localhost
   # Enter your password when prompted
   ```

## Option 2: Use Trust Authentication (Less Secure, Dev Only)

If you're only doing development and want quick access:

1. **Edit pg_hba.conf:**

   ```bash
   sudo nano /etc/postgresql/16/main/pg_hba.conf
   ```

2. **Change to trust (NO PASSWORD REQUIRED - DEV ONLY):**

   ```
   local   all             all                                     trust
   ```

3. **Restart and connect:**

   ```bash
   sudo service postgresql restart
   psql -U postgres
   ```

**Warning:** Only use this for local development. Never use `trust` in production!

## Option 3: Create Database Without Using postgres User

You can skip the postgres user entirely and create everything as the system postgres user:

```bash
# Create database as system user
sudo -u postgres createdb fundraising

# Create your application user
sudo -u postgres psql -c "CREATE USER fundraiser WITH PASSWORD 'your_password';"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fundraising TO fundraiser;"

# Connect to the database and grant schema permissions (PostgreSQL 15+)
sudo -u postgres psql -d fundraising -c "GRANT ALL ON SCHEMA public TO fundraiser;"
```

Now you can use the `fundraiser` user (which has a password you just set) in your Django app!

## Which Option Should You Choose?

- **Option 1**: Most secure, best practice - do this for production
- **Option 2**: Quick for development, but insecure
- **Option 3**: Good compromise - bypass postgres user entirely and just use your app user

For your current situation, I recommend **Option 3** since it's the quickest path to getting Django working!
