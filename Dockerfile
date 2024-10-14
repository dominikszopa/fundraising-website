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

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/team_fundraising/entrypoint.sh

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Make the entrypoint script executable
RUN chmod +x /app/team_fundraising/entrypoint.sh

# Set the port Django will run on
EXPOSE 8000

# Use the entrypoint script to run the server
ENTRYPOINT ["/app/team_fundraising/entrypoint.sh"]
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]