#!/bin/bash
echo "Starting Flask app at $(date)"
echo "Environment variables:"
env
echo "PORT is set to: '$PORT'"
if [ -z "$PORT" ]; then
    echo "PORT is not set, defaulting to 8080"
    PORT=8080
fi
echo "Binding gunicorn to 0.0.0.0:$PORT"
exec gunicorn --workers 2 --bind 0.0.0.0:$PORT app:app