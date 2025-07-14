#!/bin/bash
echo "Starting Flask app at $(date)"
echo "Using port ${PORT:-8080}"
exec gunicorn --workers 2 --bind 0.0.0.0:${PORT:-8080} app:app