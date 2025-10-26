#!/usr/bin/env bash
# One-time GCP provisioning for writing.geoglypha1.org.
#
# Idempotent: safe to re-run. Each step checks existence before creating.
# Run from your local machine after `gcloud auth login` and selecting the
# right project. Total runtime ~10 minutes (Cloud SQL takes most of that).
#
# Usage:  bash setup-gcp.sh
set -euo pipefail

# ─── Configuration ─────────────────────────────────────────────────────────
PROJECT_ID="${PROJECT_ID:-precise-equator-411516}"
REGION="${REGION:-us-central1}"
SQL_INSTANCE="${SQL_INSTANCE:-writing-pg}"
SQL_DB_NAME="${SQL_DB_NAME:-worldbuilding}"
SQL_DB_USER="${SQL_DB_USER:-worldbuilding_app}"
GCS_BUCKET="${GCS_BUCKET:-${PROJECT_ID}-writing-media}"
AR_REPO="${AR_REPO:-writing}"
RUNTIME_SA="${RUNTIME_SA:-writing-runtime}"
DEPLOY_SA="${DEPLOY_SA:-gh-deployer}"
WIF_POOL="${WIF_POOL:-github-pool}"
WIF_PROVIDER="${WIF_PROVIDER:-github-provider}"
GITHUB_REPO="${GITHUB_REPO:-}"  # e.g. "yourorg/collaborative-worldbuilding"

# ─── Helpers ───────────────────────────────────────────────────────────────
say() { printf "\n\033[1;36m▶ %s\033[0m\n" "$*"; }
ok()  { printf "  \033[32m✓\033[0m %s\n" "$*"; }
skip(){ printf "  \033[33m·\033[0m %s (already exists)\n" "$*"; }

require() {
  command -v "$1" >/dev/null 2>&1 || { echo "Need '$1' on PATH" >&2; exit 1; }
}
require gcloud
require gsutil

# ─── Project ───────────────────────────────────────────────────────────────
say "Setting active project to ${PROJECT_ID}"
gcloud config set project "${PROJECT_ID}"
ok "active project = $(gcloud config get-value project)"

say "Enabling required GCP APIs"
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    iamcredentials.googleapis.com \
    storage.googleapis.com \
    compute.googleapis.com \
    cloudresourcemanager.googleapis.com
ok "APIs enabled"

# ─── Cloud SQL ─────────────────────────────────────────────────────────────
say "Cloud SQL Postgres instance"
if gcloud sql instances describe "${SQL_INSTANCE}" >/dev/null 2>&1; then
  skip "instance ${SQL_INSTANCE}"
else
  gcloud sql instances create "${SQL_INSTANCE}" \
      --database-version=POSTGRES_15 \
      --tier=db-f1-micro \
      --region="${REGION}" \
      --storage-size=10GB \
      --storage-auto-increase \
      --backup \
      --backup-start-time=08:00
  ok "created ${SQL_INSTANCE}"
fi

if gcloud sql databases describe "${SQL_DB_NAME}" --instance="${SQL_INSTANCE}" >/dev/null 2>&1; then
  skip "database ${SQL_DB_NAME}"
else
  gcloud sql databases create "${SQL_DB_NAME}" --instance="${SQL_INSTANCE}"
  ok "created database ${SQL_DB_NAME}"
fi

# Generate a strong DB password and stash it in Secret Manager. If the secret
# already exists, we keep its current value (don't rotate on re-run).
say "Cloud SQL user + password (Secret Manager)"
if gcloud secrets describe db-password >/dev/null 2>&1; then
  skip "secret db-password"
  DB_PASSWORD="$(gcloud secrets versions access latest --secret=db-password)"
else
  DB_PASSWORD="$(LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32)"
  printf '%s' "${DB_PASSWORD}" | gcloud secrets create db-password --data-file=-
  ok "created secret db-password"
fi

if gcloud sql users describe "${SQL_DB_USER}" --instance="${SQL_INSTANCE}" >/dev/null 2>&1; then
  # Keep the password in sync with the secret on re-runs.
  gcloud sql users set-password "${SQL_DB_USER}" \
      --instance="${SQL_INSTANCE}" --password="${DB_PASSWORD}" >/dev/null
  skip "user ${SQL_DB_USER} (password synced)"
else
  gcloud sql users create "${SQL_DB_USER}" \
      --instance="${SQL_INSTANCE}" --password="${DB_PASSWORD}"
  ok "created user ${SQL_DB_USER}"
fi

# Django SECRET_KEY → Secret Manager.
say "Django SECRET_KEY (Secret Manager)"
if gcloud secrets describe django-secret-key >/dev/null 2>&1; then
  skip "secret django-secret-key"
else
  python3 -c "import secrets; print(secrets.token_urlsafe(64))" \
      | tr -d '\n' \
      | gcloud secrets create django-secret-key --data-file=-
  ok "created secret django-secret-key"
fi

# ─── GCS bucket for media ──────────────────────────────────────────────────
say "GCS bucket for user-uploaded media"
if gsutil ls -b "gs://${GCS_BUCKET}" >/dev/null 2>&1; then
  skip "bucket gs://${GCS_BUCKET}"
else
  gsutil mb -l "${REGION}" -b on "gs://${GCS_BUCKET}"
  # Make objects publicly readable so <img src> works in browsers without
  # signed URLs. Adjust if you want private + signed URLs later.
  gsutil iam ch allUsers:objectViewer "gs://${GCS_BUCKET}"
  ok "created bucket gs://${GCS_BUCKET}"
fi

# ─── Artifact Registry ─────────────────────────────────────────────────────
say "Artifact Registry repo for Docker images"
if gcloud artifacts repositories describe "${AR_REPO}" --location="${REGION}" >/dev/null 2>&1; then
  skip "repo ${AR_REPO}"
else
  gcloud artifacts repositories create "${AR_REPO}" \
      --repository-format=docker \
      --location="${REGION}" \
      --description="Docker images for writing.geoglypha1.org"
  ok "created repo ${AR_REPO}"
fi

# ─── Service accounts ──────────────────────────────────────────────────────
say "Runtime service account (used by Cloud Run services)"
RUNTIME_EMAIL="${RUNTIME_SA}@${PROJECT_ID}.iam.gserviceaccount.com"
if gcloud iam service-accounts describe "${RUNTIME_EMAIL}" >/dev/null 2>&1; then
  skip "service account ${RUNTIME_EMAIL}"
else
  gcloud iam service-accounts create "${RUNTIME_SA}" \
      --display-name="Cloud Run runtime for writing"
  ok "created ${RUNTIME_EMAIL}"
fi

# Permissions the runtime SA needs.
for ROLE in \
    roles/cloudsql.client \
    roles/secretmanager.secretAccessor \
    roles/storage.objectAdmin \
    roles/logging.logWriter; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
      --member="serviceAccount:${RUNTIME_EMAIL}" \
      --role="${ROLE}" --condition=None >/dev/null
done
ok "runtime SA roles bound"

say "Deployer service account (used by GitHub Actions)"
DEPLOY_EMAIL="${DEPLOY_SA}@${PROJECT_ID}.iam.gserviceaccount.com"
if gcloud iam service-accounts describe "${DEPLOY_EMAIL}" >/dev/null 2>&1; then
  skip "service account ${DEPLOY_EMAIL}"
else
  gcloud iam service-accounts create "${DEPLOY_SA}" \
      --display-name="GitHub Actions deployer for writing"
  ok "created ${DEPLOY_EMAIL}"
fi

for ROLE in \
    roles/run.admin \
    roles/artifactregistry.writer \
    roles/iam.serviceAccountUser \
    roles/cloudsql.client; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
      --member="serviceAccount:${DEPLOY_EMAIL}" \
      --role="${ROLE}" --condition=None >/dev/null
done
ok "deployer SA roles bound"

# ─── Workload Identity Federation (keyless GitHub → GCP auth) ──────────────
if [[ -n "${GITHUB_REPO}" ]]; then
  say "Workload Identity Federation for repo ${GITHUB_REPO}"

  if gcloud iam workload-identity-pools describe "${WIF_POOL}" --location=global >/dev/null 2>&1; then
    skip "pool ${WIF_POOL}"
  else
    gcloud iam workload-identity-pools create "${WIF_POOL}" \
        --location=global --display-name="GitHub pool"
    ok "created pool ${WIF_POOL}"
  fi

  if gcloud iam workload-identity-pools providers describe "${WIF_PROVIDER}" \
        --location=global --workload-identity-pool="${WIF_POOL}" >/dev/null 2>&1; then
    skip "provider ${WIF_PROVIDER}"
  else
    gcloud iam workload-identity-pools providers create-oidc "${WIF_PROVIDER}" \
        --location=global \
        --workload-identity-pool="${WIF_POOL}" \
        --display-name="GitHub OIDC provider" \
        --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
        --attribute-condition="assertion.repository=='${GITHUB_REPO}'" \
        --issuer-uri="https://token.actions.githubusercontent.com"
    ok "created provider ${WIF_PROVIDER}"
  fi

  PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
  WIF_PROVIDER_RESOURCE="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${WIF_POOL}/providers/${WIF_PROVIDER}"
  gcloud iam service-accounts add-iam-policy-binding "${DEPLOY_EMAIL}" \
      --role=roles/iam.workloadIdentityUser \
      --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${WIF_POOL}/attribute.repository/${GITHUB_REPO}" \
      >/dev/null
  ok "WIF binding for ${GITHUB_REPO} → ${DEPLOY_EMAIL}"

  echo
  echo "─── Add these to your GitHub repo Settings → Secrets and variables → Actions ───"
  echo "  GCP_PROJECT_ID         = ${PROJECT_ID}"
  echo "  GCP_REGION             = ${REGION}"
  echo "  GCP_WIF_PROVIDER       = ${WIF_PROVIDER_RESOURCE}"
  echo "  GCP_DEPLOY_SA_EMAIL    = ${DEPLOY_EMAIL}"
  echo "  GCP_RUNTIME_SA_EMAIL   = ${RUNTIME_EMAIL}"
  echo "  GCP_SQL_INSTANCE       = ${PROJECT_ID}:${REGION}:${SQL_INSTANCE}"
  echo "  GCP_DB_NAME            = ${SQL_DB_NAME}"
  echo "  GCP_DB_USER            = ${SQL_DB_USER}"
  echo "  GCP_GCS_BUCKET         = ${GCS_BUCKET}"
  echo "  GCP_AR_REPO            = ${AR_REPO}"
else
  echo
  echo "ℹ  Skipped Workload Identity setup. To enable it later, re-run with:"
  echo "     GITHUB_REPO=your-org/your-repo bash setup-gcp.sh"
fi

say "Done."
echo "Next: push the repo, then GitHub Actions will build and deploy."
