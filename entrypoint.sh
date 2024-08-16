#!/bin/sh
set -e

./wait-for-it.sh graveboards-postgresql-prod:5432 --timeout=30 --strict -- echo "PostgreSQL is up"
./wait-for-it.sh graveboards-redis-prod:6379 --timeout=30 --strict -- echo "Redis is up"

python setup.py

exec "$@"
