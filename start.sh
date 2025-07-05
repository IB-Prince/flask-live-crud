#!/bin/bash
echo "Starting Flask app at $(date)"
echo "Environment variables:"
env | grep -E "(PORT|DB_URL|DATABASE_URL)"
echo "PORT is set to: '$PORT'"

# Set default port if PORT is not set or empty
if [ -z "$PORT" ]; then
    echo "PORT is not set, defaulting to 8080"
    export PORT=8080
fi

echo "Binding gunicorn to 0.0.0.0:$PORT"
exec gunicorn --workers 2 --bind 0.0.0.0:$PORT app:app