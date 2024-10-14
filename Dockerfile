# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app/team_fundraising

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy the project files into the container
COPY . /app/team_fundraising/

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Set the port Django will run on
EXPOSE 8000

# Run the application server
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]