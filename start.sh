#!/bin/bash
echo "Starting Flask app at $(date)"
echo "Using hardcoded port 8080"
exec gunicorn --workers 2 --bind 0.0.0.0:8080 app:app