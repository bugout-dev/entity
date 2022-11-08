#!/usr/bin/env sh

# Expects access to Python environment with the requirements
# for this project installed.
set -e

ENTITY_HOST="${ENTITY_HOST:-127.0.0.1}"
ENTITY_PORT="${ENTITY_PORT:-7291}"
ENTITY_WORKERS="${ENTITY_WORKERS:-1}"

uvicorn --reload --port "$ENTITY_PORT" --host "$ENTITY_HOST" --workers "$ENTITY_WORKERS" entityapi.api:app
