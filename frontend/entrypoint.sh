#!/bin/sh
# Frontend nginx container entrypoint.
#
# Cloud Run sets $PORT (default 8080); deploy-time env sets $BACKEND_URL,
# e.g. https://writing-backend-abc123-uc.a.run.app. envsubst renders the
# template into the real nginx.conf, then we exec nginx in the foreground.
set -eu

: "${PORT:=8080}"
: "${BACKEND_URL:?BACKEND_URL must be set to the Django Cloud Run service URL}"

# Strip trailing slash from BACKEND_URL — nginx proxy_pass + location prefix
# already provides path joining, and a double slash breaks Django routing.
BACKEND_URL="${BACKEND_URL%/}"
export PORT BACKEND_URL

echo "[entrypoint] Templating nginx.conf (PORT=${PORT}, BACKEND_URL=${BACKEND_URL})"
envsubst '${PORT} ${BACKEND_URL}' \
    < /etc/nginx/nginx.conf.template \
    > /etc/nginx/nginx.conf

# Quick sanity check; fail loudly on bad config rather than CrashLoop.
nginx -t

exec nginx -g 'daemon off;'
