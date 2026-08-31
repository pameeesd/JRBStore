#!/bin/sh
set -e

# Run database migrations automatically on startup
python src/manage.py migrate --noinput

# Idempotently seed initial product catalog on container startup
python src/manage.py seed_catalog

# Execute container command
exec "$@"
