# Backend Dockerfile — Cloud Run target
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps:
#   libpq-dev, build-essential — to compile psycopg2 wheel for psycopg2-binary fallback
#   curl                       — for HEALTHCHECK
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps first for better layer caching.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x /app/entrypoint.sh

# Pre-collect static files so the container starts fast on Cloud Run.
# DJANGO_ENV=production toggles WhiteNoise hashed-manifest storage.
ENV DJANGO_ENV=production \
    SECRET_KEY=build-time-only-not-for-runtime \
    USE_POSTGRESQL=False
RUN python manage.py collectstatic --noinput

# Cloud Run will set $PORT; default for local runs.
ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT}/api/v1/health/" || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
