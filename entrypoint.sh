#!/bin/sh

# Ensure the SQLite directory exists
mkdir -p /app/db

# Make migrations and migrate
python manage.py makemigrations
python manage.py migrate

exec "$@"