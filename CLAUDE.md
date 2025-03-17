# CLAUDE.md - Development Guide

## Common Commands
- Run server: `python3 manage.py runserver localhost:8000`
- Run tests: `python3 manage.py test team_fundraising.tests`
- Run single test: `python3 manage.py test team_fundraising.tests.test_models.TestCampaignModel`
- Lint code: `python3 -m flake8`
- Install dependencies: `poetry install`
- Create migrations: `python3 manage.py makemigrations`
- Apply migrations: `python3 manage.py migrate`
- Load test data: `python3 manage.py loaddata startingdata`

## Code Style
- Follow PEP 8 with 100 character line limit
- Sort imports alphabetically: standard library, third-party, local
- Use Django's built-in error handling (`get_object_or_404`, form validation)
- Function and variable names should be snake_case
- Class names should be PascalCase
- Include docstrings for classes, methods and functions
- Test method names should be descriptive (test_empty_fundraiser)
- Use Python type hints where possible
- Use Django's ORM query optimization methods

## Project Structure
- Django 4.2 with Python 3.12
- Follows Django app-based architecture (team_fundraising app)
- Bootstrap 4 for frontend with crispy-forms
- PayPal integration for payment processing