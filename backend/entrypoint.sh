#!/usr/bin/env sh

set -e

uv run python manage.py migrate
uv run uvicorn squidfall.asgi:application --host 0.0.0.0 --port 8000
