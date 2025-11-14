# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands
- Run server: `python3 manage.py runserver localhost:8000`
- Run tests: `python3 manage.py test team_fundraising.tests`
- Run single test: `python3 manage.py test team_fundraising.tests.test_models.TestCampaignModel`
- Lint code: `python3 -m flake8`
- Install dependencies: `poetry install`
- Activate virtual environment: `poetry shell`
- Create migrations: `python3 manage.py makemigrations`
- Apply migrations: `python3 manage.py migrate`
- Create superuser: `python3 manage.py createsuperuser`
- Load test data: `python3 manage.py loaddata startingdata`
- Collect static files: `python3 manage.py collectstatic`
- Migrate from SQLite to PostgreSQL: `python3 manage.py migrate_sqlite_to_postgres`

## Code Style
- Follow PEP 8 with 100 character line limit (enforced by .flake8)
- Sort imports alphabetically: standard library, third-party, local
- Use Django's built-in error handling (`get_object_or_404`, form validation)
- Function and variable names should be snake_case
- Class names should be PascalCase
- Include docstrings for classes, methods and functions
- Test method names should be descriptive (test_empty_fundraiser)
- Use Python type hints where possible
- Use Django's ORM query optimization methods

## Project Structure
- Django 5.2 with Python 3.12
- Uses split settings: `fundraiser/settings/` with `base.py`, `dev.py`, `prod.py`
- Default settings module: `fundraiser.settings.dev` (set in manage.py)
- Main Django app: `team_fundraising` (contains models, views, forms, templates)
- Bootstrap 4 for frontend with django-crispy-forms (using crispy_bootstrap4)
- PayPal integration via django-paypal with IPN (Instant Payment Notification)
- PostgreSQL database (configurable via environment variables)
- Media files (photos) uploaded to `media/photos/` with thumbnails in `media/photos_small/`
- Static files collected to `static/` directory

## Key Architecture

### Data Model
Three main models in `team_fundraising/models.py`:
- **Campaign**: Parent object with overall fundraising goal
- **Fundraiser**: Individual fundraiser pages linked to a Campaign and User
- **Donation**: Individual donations linked to Fundraisers

Additional models:
- **Donor**: Proxy model that aggregates Donations by email/name for reporting
- **ProxyUser**: Proxy model extending Django User with fundraiser methods

### Settings & Environment
- Environment variables loaded from `.env` file via python-dotenv
- Required env vars: `SECRET_KEY`, `DEBUG`
- Database: `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`
- Optional: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- PayPal: `PAYPAL_TEST`, `PAYPAL_ACCOUNT`
- Use `get_env_variable()` and `read_boolean()` helpers from `base.py`

### Image Handling
- Fundraiser photos automatically generate thumbnail versions on save
- Uses PIL (Pillow) to create 800x800 thumbnails
- Original stored in `photo`, thumbnail in `photo_small`

### URL Structure
- Main campaign view: `/team_fundraising/` (redirects to latest active campaign)
- Specific campaign: `/team_fundraising/<campaign_id>/`
- Fundraiser page: `/team_fundraising/fundraiser/<fundraiser_id>/`
- Donations handled via PayPal IPN at `/paypal/` URLs

## Testing
- Test files in `team_fundraising/tests/`: test_models.py, test_views.py, test_forms.py, test_donations.py, test_signup.py
- Uses Django's TestCase framework
- Test data fixtures available via `loaddata startingdata`
