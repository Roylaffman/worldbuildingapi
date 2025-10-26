# ☁️ Google Cloud Platform Deployment Guide

Complete guide to deploying the Collaborative Worldbuilding Platform on Google Cloud Platform.

## 🎯 **Overview**

This guide covers deployment using:
- **Google Cloud Run** (Serverless containers)
- **Google Cloud SQL** (PostgreSQL database)
- **Google Cloud Storage** (Static files & media)
- **Google Cloud Build** (CI/CD)
- **Google Cloud CDN** (Content delivery)

## 📋 **Prerequisites**

- Google Cloud Platform account
- Google Cloud SDK (`gcloud`) installed
- Docker installed locally
- Domain name (optional but recommended)

## 🚀 **Quick Setup**

### **1. Initial GCP Setup**
```bash
# Install Google Cloud SDK (if not already installed)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Login to GCP
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage-component.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### **2. Create Project Structure**
```bash
# Clone your repository
git clone https://github.com/Roylaffman/worldbuildingapi.git
cd worldbuildingapi

# Create GCP-specific files
mkdir -p deployment/gcp
```

## 🗄️ **Database Setup (Cloud SQL)**

### **1. Create PostgreSQL Instance**
```bash
# Create Cloud SQL instance
gcloud sql instances create worldbuilding-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=10GB \
    --backup-start-time=03:00 \
    --enable-bin-log

# Create database
gcloud sql databases create worldbuilding --instance=worldbuilding-db

# Create database user
gcloud sql users create worldbuilding-user \
    --instance=worldbuilding-db \
    --password=SECURE_PASSWORD_HERE
```

### **2. Configure Database Connection**
```bash
# Get connection name
gcloud sql instances describe worldbuilding-db --format="value(connectionName)"

# Note: You'll need this for Cloud Run configuration
```

## 🪣 **Storage Setup (Cloud Storage)**

### **1. Create Storage Buckets**
```bash
# Create bucket for static files
gsutil mb gs://YOUR_PROJECT_ID-static

# Create bucket for media files
gsutil mb gs://YOUR_PROJECT_ID-media

# Set public access for static files
gsutil iam ch allUsers:objectViewer gs://YOUR_PROJECT_ID-static

# Set CORS for media files
echo '[{"origin": ["*"], "method": ["GET"], "maxAgeSeconds": 3600}]' > cors.json
gsutil cors set cors.json gs://YOUR_PROJECT_ID-media
rm cors.json
```

### **2. Create Service Account**
```bash
# Create service account for storage access
gcloud iam service-accounts create worldbuilding-storage \
    --display-name="Worldbuilding Storage Service Account"

# Grant storage permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:worldbuilding-storage@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Create and download key
gcloud iam service-accounts keys create storage-key.json \
    --iam-account=worldbuilding-storage@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## 🔐 **Secrets Management**

### **1. Store Secrets in Secret Manager**
```bash
# Django secret key
echo -n "your-super-secret-django-key" | gcloud secrets create django-secret-key --data-file=-

# Database password
echo -n "SECURE_PASSWORD_HERE" | gcloud secrets create db-password --data-file=-

# Storage service account key
gcloud secrets create storage-service-account --data-file=storage-key.json

# Email credentials (if using)
echo -n "your-email-password" | gcloud secrets create email-password --data-file=-
```

### **2. Grant Access to Secrets**
```bash
# Create service account for Cloud Run
gcloud iam service-accounts create worldbuilding-app \
    --display-name="Worldbuilding App Service Account"

# Grant secret access
gcloud secrets add-iam-policy-binding django-secret-key \
    --member="serviceAccount:worldbuilding-app@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding db-password \
    --member="serviceAccount:worldbuilding-app@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding storage-service-account \
    --member="serviceAccount:worldbuilding-app@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## 🐳 **Container Setup**

### **1. Create Production Dockerfile**
Create `deployment/gcp/Dockerfile.gcp`:
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn psycopg2-binary google-cloud-storage google-cloud-secret-manager

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=worldbuilding.settings.production

# Create startup script
RUN echo '#!/bin/bash\n\
python manage.py migrate --noinput\n\
gunicorn --bind 0.0.0.0:$PORT --workers 2 worldbuilding.wsgi:application' > start.sh
RUN chmod +x start.sh

EXPOSE 8080

CMD ["./start.sh"]
```

### **2. Create Production Settings**
Create `worldbuilding/settings/production.py`:
```python
from .base import *
import os
from google.cloud import secretmanager

# Initialize Secret Manager client
client = secretmanager.SecretManagerServiceClient()
project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')

def get_secret(secret_name):
    """Retrieve secret from Google Secret Manager"""
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Security
DEBUG = False
SECRET_KEY = get_secret('django-secret-key')
ALLOWED_HOSTS = ['.run.app', 'yourdomain.com', 'www.yourdomain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'worldbuilding',
        'USER': 'worldbuilding-user',
        'PASSWORD': get_secret('db-password'),
        'HOST': '/cloudsql/YOUR_PROJECT_ID:us-central1:worldbuilding-db',
        'PORT': '5432',
    }
}

# Static files (Google Cloud Storage)
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'YOUR_PROJECT_ID-static'
GS_MEDIA_BUCKET_NAME = 'YOUR_PROJECT_ID-media'
STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/'
MEDIA_URL = f'https://storage.googleapis.com/{GS_MEDIA_BUCKET_NAME}/'

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## 🚀 **Deploy Backend to Cloud Run**

### **1. Build and Deploy**
```bash
# Build container image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/worldbuilding-backend

# Deploy to Cloud Run
gcloud run deploy worldbuilding-backend \
    --image gcr.io/YOUR_PROJECT_ID/worldbuilding-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --service-account worldbuilding-app@YOUR_PROJECT_ID.iam.gserviceaccount.com \
    --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:worldbuilding-db \
    --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10
```

### **2. Configure Custom Domain (Optional)**
```bash
# Map custom domain
gcloud run domain-mappings create \
    --service worldbuilding-backend \
    --domain api.yourdomain.com \
    --region us-central1
```

## 🌐 **Deploy Frontend**

### **1. Build Frontend for Production**
```bash
cd frontend

# Create production environment file
cat > .env.production << EOF
VITE_API_BASE_URL=https://worldbuilding-backend-HASH-uc.a.run.app/api
VITE_APP_TITLE=Collaborative Worldbuilding
EOF

# Build for production
npm run build
```

### **2. Deploy to Cloud Storage + CDN**
```bash
# Create bucket for frontend
gsutil mb gs://YOUR_PROJECT_ID-frontend

# Enable website configuration
gsutil web set -m index.html -e index.html gs://YOUR_PROJECT_ID-frontend

# Upload build files
gsutil -m cp -r dist/* gs://YOUR_PROJECT_ID-frontend/

# Set public access
gsutil iam ch allUsers:objectViewer gs://YOUR_PROJECT_ID-frontend

# Create load balancer and CDN (optional)
gcloud compute backend-buckets create frontend-backend \
    --gcs-bucket-name=YOUR_PROJECT_ID-frontend

gcloud compute url-maps create frontend-map \
    --default-backend-bucket=frontend-backend

gcloud compute target-http-proxies create frontend-proxy \
    --url-map=frontend-map

gcloud compute forwarding-rules create frontend-rule \
    --global \
    --target-http-proxy=frontend-proxy \
    --ports=80
```

## 🔄 **CI/CD Setup with Cloud Build**

### **1. Create Cloud Build Configuration**
Create `cloudbuild.yaml`:
```yaml
steps:
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/worldbuilding-backend', '-f', 'deployment/gcp/Dockerfile.gcp', '.']
  
  # Push backend image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/worldbuilding-backend']
  
  # Deploy backend to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'worldbuilding-backend'
      - '--image'
      - 'gcr.io/$PROJECT_ID/worldbuilding-backend'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
  
  # Build frontend
  - name: 'node:16'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        cd frontend
        npm ci
        npm run build
        gsutil -m cp -r dist/* gs://$PROJECT_ID-frontend/

substitutions:
  _REGION: us-central1

options:
  logging: CLOUD_LOGGING_ONLY
```

### **2. Set up Triggers**
```bash
# Connect repository
gcloud builds triggers create github \
    --repo-name=worldbuildingapi \
    --repo-owner=Roylaffman \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

## 📊 **Monitoring and Logging**

### **1. Enable Monitoring**
```bash
# Enable monitoring API
gcloud services enable monitoring.googleapis.com

# Create uptime check
gcloud alpha monitoring uptime create \
    --display-name="Worldbuilding API Health Check" \
    --http-check-path="/api/health/" \
    --hostname="worldbuilding-backend-HASH-uc.a.run.app"
```

### **2. Set up Alerts**
```bash
# Create notification channel (email)
gcloud alpha monitoring channels create \
    --display-name="Admin Email" \
    --type=email \
    --channel-labels=email_address=your-email@gmail.com

# Create alert policy for high error rate
gcloud alpha monitoring policies create \
    --policy-from-file=monitoring-policy.yaml
```

## 💰 **Cost Optimization**

### **1. Resource Optimization**
```bash
# Set minimum instances to 0 for cost savings
gcloud run services update worldbuilding-backend \
    --region us-central1 \
    --min-instances 0 \
    --max-instances 5

# Use smaller database instance for development
gcloud sql instances patch worldbuilding-db \
    --tier=db-f1-micro
```

### **2. Budget Alerts**
```bash
# Create budget alert
gcloud billing budgets create \
    --billing-account=YOUR_BILLING_ACCOUNT_ID \
    --display-name="Worldbuilding Budget" \
    --budget-amount=50USD \
    --threshold-rule=percent=80,basis=CURRENT_SPEND
```

## 🛠️ **Maintenance and Updates**

### **1. Database Maintenance**
```bash
# Create database backup
gcloud sql backups create \
    --instance=worldbuilding-db \
    --description="Manual backup before update"

# Run migrations
gcloud run jobs create migrate-job \
    --image gcr.io/YOUR_PROJECT_ID/worldbuilding-backend \
    --command python,manage.py,migrate \
    --region us-central1
```

### **2. Application Updates**
```bash
# Deploy new version
git push origin main  # Triggers automatic deployment

# Or manual deployment
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/worldbuilding-backend
gcloud run deploy worldbuilding-backend \
    --image gcr.io/YOUR_PROJECT_ID/worldbuilding-backend \
    --region us-central1
```

## 🎯 **Production Checklist**

- [ ] Database instance created and configured
- [ ] Storage buckets created with proper permissions
- [ ] Secrets stored in Secret Manager
- [ ] Backend deployed to Cloud Run
- [ ] Frontend deployed to Cloud Storage
- [ ] Custom domain configured (optional)
- [ ] SSL certificates configured
- [ ] Monitoring and alerts set up
- [ ] Backup strategy implemented
- [ ] CI/CD pipeline configured
- [ ] Budget alerts configured

## 📋 **Estimated Costs**

**Monthly costs for small-medium usage:**
- Cloud Run: $0-20 (pay per use)
- Cloud SQL (db-f1-micro): $7-15
- Cloud Storage: $1-5
- Cloud Build: $0-10
- **Total: ~$8-50/month**

This GCP setup provides a scalable, managed solution perfect for your collaborative worldbuilding platform! ☁️🚀