#!/bin/bash
echo "Starting Flask app at $(date)"

# Use Railway's port or default to 8080
PORT=${PORT:-8080}

echo "Using PORT: $PORT"
exec gunicorn --workers 2 --bind 0.0.0.0:$PORT app:app