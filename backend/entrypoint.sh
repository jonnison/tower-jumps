#!/bin/bash

echo "Starting Django application..."

# Run migrations in background if needed (but don't block startup)
(
    echo "Running migrations..."
    python manage.py migrate
    echo "Importing initial data..."
    python manage.py import_usa_states || true
    python manage.py import_data Jonnison 4245337_CarrierRecords.csv || true
    python manage.py import_data Nishant 4245337_CarrierRecords.csv || true
    echo "Initial setup completed."
) &

# Start the server immediately
echo "Starting Gunicorn server..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --log-level INFO --workers 2 --worker-connections 1000