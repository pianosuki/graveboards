#!/bin/sh
set -e

python setup.py

exec "$@"
