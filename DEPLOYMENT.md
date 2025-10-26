# Deployment Runbook — writing.geoglypha1.org

Step-by-step operator guide. Assumes you've already read `DEPLOYMENT_PLAN.md`
in the parent folder.

## 0. Prerequisites

- `gcloud` CLI installed and authenticated: `gcloud auth login`
- A GitHub repo for this code with admin access
- Cloudflare access for `geoglypha1.org`
- Billing enabled on GCP project `precise-equator-411516`

## 1. One-time GCP setup

```bash
cd worldbuildingapi
GITHUB_REPO="<your-org>/<your-repo>" bash setup-gcp.sh
```

The script is idempotent — re-run it if anything fails partway. At the end
it prints the seven values you need to paste into GitHub Secrets. Copy them.

Approx run time: 8–12 minutes (Cloud SQL provisioning is the slow part).

## 2. Add GitHub repo secrets

GitHub → Settings → Secrets and variables → Actions → New repository secret.
Add each line printed by `setup-gcp.sh` exactly:

| Secret name             | Value                                          |
|-------------------------|------------------------------------------------|
| `GCP_PROJECT_ID`        | `precise-equator-411516`                       |
| `GCP_REGION`            | `us-central1`                                  |
| `GCP_WIF_PROVIDER`      | `projects/.../providers/github-provider`       |
| `GCP_DEPLOY_SA_EMAIL`   | `gh-deployer@precise-equator-411516...`        |
| `GCP_RUNTIME_SA_EMAIL`  | `writing-runtime@precise-equator-411516...`    |
| `GCP_SQL_INSTANCE`      | `precise-equator-411516:us-central1:writing-pg`|
| `GCP_DB_NAME`           | `worldbuilding`                                |
| `GCP_DB_USER`           | `worldbuilding_app`                            |
| `GCP_GCS_BUCKET`        | `precise-equator-411516-writing-media`         |
| `GCP_AR_REPO`           | `writing`                                      |

## 3. First deploy

```bash
git add .
git commit -m "Initial production deploy config"
git push origin main
```

Watch Actions tab. The workflow takes ~6 minutes the first time:

1. Build + push backend image to Artifact Registry
2. Deploy `writing-backend` Cloud Run service (creates DB schema via `migrate`)
3. Build + push frontend image
4. Deploy `writing-frontend` Cloud Run service with `BACKEND_URL` env wired

If the workflow logs end with `::notice::Frontend deployed at https://...`,
the deploy succeeded. Open that URL in a browser to verify React loads.

## 4. Create the first superuser

Run a one-off Cloud Run job (admin tasks shouldn't live in the always-on service):

```bash
gcloud run jobs create create-superuser \
    --image="us-central1-docker.pkg.dev/precise-equator-411516/writing/backend:latest" \
    --region=us-central1 \
    --service-account="writing-runtime@precise-equator-411516.iam.gserviceaccount.com" \
    --set-cloudsql-instances="precise-equator-411516:us-central1:writing-pg" \
    --set-env-vars="DJANGO_ENV=production,USE_POSTGRESQL=True,DB_NAME=worldbuilding,DB_USER=worldbuilding_app,DB_HOST=/cloudsql/precise-equator-411516:us-central1:writing-pg,DJANGO_SUPERUSER_USERNAME=admin,DJANGO_SUPERUSER_EMAIL=roylaffman@gmail.com" \
    --set-secrets="SECRET_KEY=django-secret-key:latest,DB_PASSWORD=db-password:latest,DJANGO_SUPERUSER_PASSWORD=django-superuser-password:latest" \
    --command="python" --args="manage.py,createsuperuser,--noinput"

# Stash a one-time superuser password in Secret Manager first:
echo -n "$(openssl rand -base64 24)" | \
    gcloud secrets create django-superuser-password --data-file=-

gcloud run jobs execute create-superuser --region=us-central1 --wait
gcloud secrets versions access latest --secret=django-superuser-password
# ↑ that prints the admin password. Save it in your password manager, then:
gcloud secrets delete django-superuser-password
```

## 5. Map the custom domain

```bash
gcloud beta run domain-mappings create \
    --service=writing-frontend \
    --domain=writing.geoglypha1.org \
    --region=us-central1
```

The output prints a CNAME target like `ghs.googlehosted.com`. Note it.

If GCP asks you to verify domain ownership (`Domain ownership verified`),
follow the link, add the TXT record it shows in Cloudflare DNS, wait 1–2 min,
re-run the command above. You only do this once per domain.

## 6. Cloudflare DNS

In Cloudflare → DNS → Records:

- Type: `CNAME`
- Name: `writing`
- Target: `ghs.googlehosted.com`
- Proxy status: **DNS only** (gray cloud) — keep it gray until the cert is ACTIVE

Check cert status:

```bash
gcloud beta run domain-mappings describe \
    --domain=writing.geoglypha1.org --region=us-central1 \
    --format='value(status.conditions)'
```

Look for `CertificateProvisioned: True`. Takes 5–30 minutes.

Once issued, you can flip Cloudflare proxy to **Proxied** (orange) and set
SSL/TLS encryption mode to **Full (strict)** — both endpoints are HTTPS.

## 7. Smoke test

```bash
curl -I https://writing.geoglypha1.org/                  # 200 OK, React app
curl    https://writing.geoglypha1.org/api/v1/health/    # 200, {"status":"healthy",...}
```

Browse to `https://writing.geoglypha1.org/`, register an account, create a
world, upload an image. Verify the image URL is `https://storage.googleapis.com/.../...`.

## 8. Iterating after first deploy

Just push to `main`. The workflow is idempotent and Cloud Run's revisions are
versioned — if something breaks you can roll back instantly:

```bash
gcloud run services update-traffic writing-backend \
    --region=us-central1 --to-revisions=writing-backend-00001-abc=100
```

## Known tech debt (does not block deploy)

**Pre-existing TypeScript errors (~49)** in `frontend/src/pages/content/ContentPage.tsx`
and a few sibling files. The `Content` type is a union (`Page | Essay | Character
| Story | Image`) but the code accesses subtype-specific fields like `.full_name`,
`.species`, `.genre` without narrowing the union. `npm run dev` and `vite build`
both ignore this because Vite transpiles TS with esbuild (no type-checking).
Only `tsc` catches it, so we've split the scripts:

- `npm run build` — production build, no type-check (used by Docker + CI)
- `npm run build:strict` — `tsc && vite build`, currently fails
- `npm run typecheck` — run `tsc --noEmit` alone

To fix properly, add discriminator narrowing:
```ts
if (content.content_type === 'character') { /* content.full_name available */ }
```
or a runtime `switch (content.content_type)`.

## Common breakages

**`CSRF verification failed`** in Django admin
→ `CSRF_TRUSTED_ORIGINS` env var must include the full URL with scheme,
  e.g. `https://writing.geoglypha1.org`. Set in workflow already.

**`502 Bad Gateway` from frontend**
→ Frontend container's `BACKEND_URL` env var is missing or wrong.
  Check `gcloud run services describe writing-frontend --format='value(spec.template.spec.containers[0].env)'`.

**Image upload returns 500**
→ Runtime SA missing `roles/storage.objectAdmin` on the bucket. Re-run
  `setup-gcp.sh` — the IAM binding step is idempotent.

**Cold start > 10s**
→ Cloud SQL connections are slow on cold start. Set `--min-instances=1` on
  the backend (~$5/mo extra) once you have real traffic.
