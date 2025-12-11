# Event Fundraising Website

An event fundraising website where individuals can create personal pages, set goals and raise money for the overall goal.

Built in Python/Django 4.2 and Bootstrap 4 for the [Triple Crown for Heart](https://triplecrownforheart.ca/) bike ride, because you shouldn't be charged for charity fundraising.

Currently used at: [https://donations.triplecrownforheart.ca/team_fundraising/](https://donations.triplecrownforheart.ca/team_fundraising/). If you would like to use this platform for your charity fundraising event, please contact the [author](#authors).

![Demo screenshot](screenshot.png)

## Table of Contents

* [Features](#features)
* [Installing](#installing)
* [Deployment](#deployment)
* [Support](#support)
* [Build with](#built-with)
* [Contributing](#contributing)
* [Authors](#authors)
* [License](#license)
* [Acknowledgments](#acknowledgments)

## Features

* Fully responsive website that supports phones, tablets and computers
* Integration with PayPal for donations
* Individuals can create custom fundraising pages with a photo, message and fundraising goal
* Email notifications to the fundraiser whenever a donation is received

## Installing

### Prerequisites

* [Python 3.12](https://www.python.org/)
* [PostgreSQL](https://www.postgresql.org/) (version 12 or higher recommended)
* [git](https://git-scm.com/)

### Docker Installation

Docker can be run in two modes:

#### Mode 1: Self-Contained (Recommended for Production)

This mode runs PostgreSQL as a Docker container. Everything is self-contained.

1. Install Docker and Docker Compose

1. Clone this repository:

   ```bash
   git clone https://github.com/dominikszopa/fundraising.git
   cd fundraising
   ```

1. Copy .env.example to .env:

   ```bash
   cp .env.example .env
   ```

1. Edit .env and configure required values:
   * `SECRET_KEY`: A long (32+ chars) random string
   * `DATABASE_PASSWORD`: A secure password for PostgreSQL

1. Start the application:

   ```bash
   # Development/Testing
   docker-compose up -d

   # Production (with production-specific settings)
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

   This will start:
   * PostgreSQL database (port 5432)
   * Django application with Gunicorn (port 8000)
   * Nginx reverse proxy (ports 80/443)

1. The first startup will automatically:
   * Create the PostgreSQL database
   * Run migrations
   * Create a superuser (admin)
   * Load test data

1. Browse to [http://localhost:8000/team_fundraising/](http://localhost:8000/team_fundraising/)

1. Useful commands:
   * View logs: `docker-compose logs -f`
   * Stop: `docker-compose down`
   * Reset database: `docker-compose down -v` (deletes postgres_data volume)

#### Mode 2: Use Local PostgreSQL

This mode connects Docker containers to your local PostgreSQL database (useful for development).

1. Follow steps 1-4 from Mode 1 above

1. Set up local PostgreSQL (see [Local Development Installation](#local-development-installation))

1. Create override file to use host PostgreSQL:

   ```bash
   cp docker-compose.override.yml.example docker-compose.override.yml
   ```

1. Edit `docker-compose.override.yml` and set the correct `DATABASE_HOST`:
   * Mac/Windows: Use `host.docker.internal`
   * Linux: Use `172.17.0.1`

1. Ensure your local PostgreSQL allows connections from Docker:
   * Edit `pg_hba.conf` to allow connections from 172.17.0.0/16 (Linux)
   * Or ensure localhost connections are allowed (Mac/Windows)

1. Start the application:

   ```bash
   docker-compose up -d
   ```

   Docker will automatically merge docker-compose.yml with your override file.

1. The containers will now use your local PostgreSQL database

### Local Development Installation

1. Follow steps 1-4 from [Docker Installation](#docker-installation)

1. Install poetry

   `pip install poetry`

1. Install dependencies:

   `poetry install`

1. Activate the virtual environment

   `poetry shell`

1. Create a PostgreSQL database:

   **Having trouble connecting?** See [PostgreSQL Setup Guide](docs/POSTGRESQL_SETUP.md) for detailed instructions and troubleshooting.

   ```bash
   # Connect to PostgreSQL
   psql -U postgres -h localhost

   # Create the database
   CREATE DATABASE fundraising;

   # Create a user (recommended for security)
   # CREATEDB permission is needed for running Django tests
   CREATE USER fundraiser WITH PASSWORD 'your_password' CREATEDB;

   # Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE fundraising TO fundraiser;

   # For PostgreSQL 15+, also grant schema permissions
   \c fundraising
   GRANT ALL ON SCHEMA public TO fundraiser;

   # Exit psql
   \q
   ```

   **Common Issues:**
   - If you get "Peer authentication failed", see [docs/POSTGRESQL_SETUP.md](docs/POSTGRESQL_SETUP.md)
   - If psql command is not found, install PostgreSQL first: `sudo apt-get install postgresql`

1. Update your .env file with database credentials:

   ```
   DATABASE_NAME=fundraising
   DATABASE_USER=fundraiser
   DATABASE_PASSWORD=your_password
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   ```

1. Run migrations to create database tables:

   `python3 ./manage.py migrate`

1. Create a superuser - please use a strong password:

   `python3 ./manage.py createsuperuser`

1. Load test data into the database from fixtures:

   `python3 ./manage.py loaddata startingdata`

1. If everything installed, you should be able to start the Django development server:

   `python3 ./manage.py runserver localhost:8000`

1. You can browse to [http://localhost:8000/team_fundraising/](http://localhost:8000/team_fundraising/)

### Migrating from SQLite to PostgreSQL

If you have an existing SQLite database with data you want to migrate to PostgreSQL:

1. Follow all the steps above to set up PostgreSQL and run migrations

1. Install pgloader:

   ```bash
   # On Ubuntu/Debian/WSL
   sudo apt-get install pgloader

   # On macOS
   brew install pgloader
   ```

1. Create a pgloader configuration file `migration.load`:

   ```
   LOAD DATABASE
       FROM sqlite://data/db.sqlite3
       INTO postgresql://fundraiser:your_password@localhost/fundraising

   WITH include drop, create tables, create indexes, reset sequences

   SET work_mem to '16MB', maintenance_work_mem to '512 MB';
   ```

1. Run pgloader:

   ```bash
   pgloader migration.load
   ```

   pgloader will:
   - Automatically create tables and indexes
   - Migrate all data with proper type conversions
   - Preserve relationships and foreign keys
   - Handle timezone conversions
   - Show progress and statistics

1. After successful migration:
   - Verify your data: `psql -U fundraiser -h localhost -d fundraising`
   - Your media files are already in place
   - You can backup and remove the old SQLite database

**Note:** pgloader is a dedicated database migration tool that handles edge cases better than custom scripts. It's the recommended approach for production migrations.

### Email

The application sends emails when someone registers as a fundraiser, makes a donation, or receives a donation. Email delivery uses **AWS SES (Simple Email Service)** via the HTTP API.

#### AWS SES Setup

1. **Create an AWS account** at [aws.amazon.com](https://aws.amazon.com) if you don't have one

2. **Set up SES in the AWS Console:**
   - Navigate to Amazon SES service
   - Choose your region (e.g., us-east-1)
   - Verify your sender email address or domain:
     - Go to "Verified identities" → "Create identity"
     - Verify the email address you'll use as the sender
     - Check your email and click the verification link

3. **Request production access:**
   - By default, SES starts in "sandbox mode" (can only send to verified addresses)
   - Go to "Account dashboard" → "Request production access"
   - Fill out the form describing your use case
   - Approval typically takes 24 hours

4. **Create IAM credentials:**
   - Go to IAM → Users → Create user
   - Give it a descriptive name (e.g., "fundraising-ses-user")
   - Attach the `AmazonSESFullAccess` policy (or create a custom policy with `ses:SendEmail` permission)
   - Create access key → Choose "Application running outside AWS"
   - Save the Access Key ID and Secret Access Key

5. **Configure environment variables:**

   Edit your `.env` file and add:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_SES_REGION=us-east-1
   ```

#### Development/Testing

For local development and testing, emails will be **skipped automatically** if AWS credentials are not configured. You'll see debug messages in the console indicating emails were not sent. This allows you to develop and test without setting up AWS SES.

#### Legacy SMTP (Optional)

While the application now uses AWS SES by default, you can still use SMTP for local development if preferred. However, note that many cloud platforms (including Railway) block outbound SMTP connections on ports 25/587/465. The legacy SMTP settings in `.env.example` are commented out but can be used with local mail servers.

### PayPal

The website uses [django-paypal](https://django-paypal.readthedocs.io/en/stable/) to process donations. To test PayPal without having to make payments each time, you can create a sandbox account from the [PayPal Developer Site](https://developer.paypal.com/developer/accounts/). You can then add the sandbox "business account" to PAYPAL_ACCOUNT in the .env file. You can use a sandbox "personal buyer account" to make test donations.

Django-paypal uses [Instant Payment Notification](https://django-paypal.readthedocs.io/en/stable/standard/ipn.html) (IPN) meaning that PayPal will make a request to the app if a transaction is successful. For this to work on a development environment, you need to be using the system from a domain that accepts incoming connections. The easiest way to do this is using [serveo](https://serveo.net/) or [ngrok](https://ngrok.com/).

## Deployment

### Railway Deployment

The application is deployed to [Railway](https://railway.app/) using GitHub Actions for CI/CD.

#### Prerequisites

1. **Railway account** - Sign up at [railway.app](https://railway.app)
2. **AWS SES configured** - See [Email Setup](#email) above
3. **PayPal account** - For donation processing

#### Setup Steps

1. **Create a Railway project:**
   - Go to Railway dashboard → New Project
   - Deploy from GitHub repository
   - Railway will automatically detect the Dockerfile

2. **Configure environment variables in Railway:**
   ```
   DJANGO_SETTINGS_MODULE=fundraiser.settings.prod
   SECRET_KEY=your_long_random_secret_key_here
   DEBUG=False

   # Database (Railway provides PostgreSQL)
   DATABASE_NAME=railway
   DATABASE_USER=postgres
   DATABASE_PASSWORD=<from Railway PostgreSQL service>
   DATABASE_HOST=<from Railway PostgreSQL service>
   DATABASE_PORT=5432

   # AWS SES for email
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_SES_REGION=us-east-1

   # PayPal
   PAYPAL_TEST=False
   PAYPAL_ACCOUNT=your_paypal_business_email

   # Allowed hosts (use your Railway domain)
   ALLOWED_HOSTS=localhost,your-app.up.railway.app
   CSRF_TRUSTED_ORIGINS=https://your-app.up.railway.app
   ```

3. **Add a PostgreSQL service:**
   - In your Railway project → New → Database → PostgreSQL
   - Railway will automatically set database environment variables
   - Copy these values to your application's environment variables

4. **Add a volume for media files:**
   - In Railway project settings → Volumes → New Volume
   - Mount path: `/app/media`
   - This ensures uploaded photos persist across deployments

5. **Deploy:**
   - Push to your GitHub repository
   - Railway will automatically build and deploy
   - First deploy will run migrations automatically (via Dockerfile CMD)

#### Important Notes

- **SMTP Blocked:** Railway blocks outbound SMTP connections on ports 25/587/465. This is why the application uses AWS SES HTTP API instead.
- **Static Files:** Static files are served by WhiteNoise (configured in settings)
- **Media Files:** User-uploaded photos are stored in the Railway volume at `/app/media`
- **Logs:** View logs with `railway logs` (requires Railway CLI)

### Traditional Server Deployment

For deployment to traditional servers (Digital Ocean, VPS, etc.):

1. Get a server and domain through providers like [Digital Ocean](https://www.digitalocean.com/)

2. Follow steps 1-8 from [installing](#installing) above

3. Add environment variables or edit the .env file for production settings

4. Collect static files for production:
   ```bash
   python manage.py collectstatic
   ```

5. Set up nginx, Gunicorn and supervisor as detailed in the [simple is better than complex](https://simpleisbetterthancomplex.com/tutorial/2016/10/14/how-to-deploy-to-digital-ocean.html) article

If you have difficulties, please feel free to contact the [author](#authors).

## Support

For any issues installing, using or contributing, please feel free to contact the [author](#authors).

## Built with

* [Python 3.7](https://docs.python.org/3/) - Primary language
* [Django 2.2](https://docs.djangoproject.com/en/2.2/) - Web Framework
* [django-paypal](https://django-paypal.readthedocs.io/en/stable/) - Payment processor
* [Bootstrap 4](https://getbootstrap.com/docs/4.0/getting-started/introduction/) - Interface
* [django-crispy-forms](https://django-crispy-forms.readthedocs.io/en/latest/) - Bootstrap forms
* [Quill](https://quilljs.com/) - WYSIWYG editor

## Contributing

If you belong to a charity or non-profit event that has a fundraising component and would like to use this platform for your event, the author can help you get set up. This will also help development by making the product more easily adaptable to events.

If you are a Django/Python or CSS developer, we have a healthy list of features we would like to implement in the [TODO](TODO) file. I may move that to a ticket tracker if a few people join. The author will approve pull requests for the time being. I am also looking for designer help to clean up the design and make a nicer "thermometer".

This project has adopted the [Contributor Covenant](https://www.contributor-covenant.org), version 1.4, available at [https://www.contributor-covenant.org/version/1/4/code-of-conduct.html](https://www.contributor-covenant.org/version/1/4/code-of-conduct.html)

## Authors

* **Dominik Szopa** - *Django, HTML, CSS* - [DominikSzopa](https://github.com/dominikszopa) - <techdomi@gmail.com>

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

* [Horizontal Fundraising Thermometer](https://codepen.io/robotballoon/pen/Fjnyp) by [Robot Balloon](https://codepen.io/robotballoon)
* [Simple jQuery Search Filter](https://codepen.io/alexerlandsson/pen/ZbyRoO) by [Alexander Erlandsson](https://codepen.io/alexerlandsson)
* The many useful articles at [simple is better than complex](https://simpleisbetterthancomplex.com/) by [Vitor Freitas](https://simpleisbetterthancomplex.com/about/)
