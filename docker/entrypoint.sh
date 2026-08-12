#!/bin/sh
set -e

# Run database migrations automatically on startup
python src/manage.py migrate --noinput

# Execute container command
exec "$@"
