#!/bin/sh
# Backend container entrypoint.
#
# Cloud Run starts this on every cold start. It must be idempotent and fast:
# migrations run only when there is something to apply (Django no-ops the rest).
# collectstatic runs at image-build time, not here, so cold starts stay quick.
set -eu

echo "[entrypoint] Running Django migrations..."
python manage.py migrate --noinput

# Cloud Run injects $PORT (default 8080). Honor it so the container is
# portable across Cloud Run, GKE, and local docker.
: "${PORT:=8080}"
: "${GUNICORN_WORKERS:=2}"
: "${GUNICORN_TIMEOUT:=60}"

echo "[entrypoint] Starting gunicorn on 0.0.0.0:${PORT} (workers=${GUNICORN_WORKERS})"
exec gunicorn worldbuilding.wsgi:application \
    --bind "0.0.0.0:${PORT}" \
    --workers "${GUNICORN_WORKERS}" \
    --timeout "${GUNICORN_TIMEOUT}" \
    --access-logfile - \
    --error-logfile -
