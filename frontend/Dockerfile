# Frontend Dockerfile — Cloud Run target (nginx serving React build + /api proxy)

# ---- Build stage ----
FROM node:18-alpine AS build
WORKDIR /app

# Copy lockfiles first for layer caching.
COPY package*.json ./
# We need devDependencies (vite, typescript, tailwind) at build time, so do
# NOT pass --omit=dev here. The previous --only=production was a bug.
RUN npm ci

# Copy source and build. VITE_API_BASE_URL is embedded into the bundle at
# build time; default to "/api/v1" so the prod nginx proxy handles routing.
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

COPY . .
RUN npm run build

# ---- Runtime stage ----
FROM nginx:alpine

# envsubst comes from gettext.
RUN apk add --no-cache gettext curl

# Static React build → nginx web root.
COPY --from=build /app/dist /usr/share/nginx/html

# Templated nginx config + entrypoint.
COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Cloud Run will set $PORT; default for local runs.
ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT}/healthz" || exit 1

ENTRYPOINT ["/entrypoint.sh"]
