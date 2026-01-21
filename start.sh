#!/bin/bash
# Render startup script

echo "Starting PlateVision AI..."

# Check if gunicorn is installed
if command -v gunicorn &> /dev/null
then
    echo "Using Gunicorn..."
    exec gunicorn app:app --bind 0.0.0.0:$PORT --timeout 600 --workers 1 --log-level info
else
    echo "Gunicorn not found, using Flask development server..."
    exec python app.py
fi
