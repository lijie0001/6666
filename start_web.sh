#!/bin/sh
set -e
PORT=${PORT:-5000}
echo "Starting on port $PORT"
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app
