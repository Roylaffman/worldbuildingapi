# Google Cloud Console Deployment Setup

## Complete Deployment Guide

This guide provides step-by-step instructions for deploying both the Django backend and Next.js frontend on Google Cloud Console.

## Prerequisites

### Required Tools
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install Docker
# Follow instructions at: https://docs.docker.com/get-docker/

# Install Node.js 18+
# Download from: https://nodejs.org/
```

### Google Cloud Account Setup
1. Create Google Cloud account at https://cloud.google.com
2. Create new project or select existing project
3. Enable billing for the project
4. Install and initialize gcloud CLI

## Step 1: Google Cloud Project Configuration

### Initialize Project
```bash
# Set your project ID
export PROJECT_ID="worldbuilding-platform"

# Create project (if new)
gcloud projects create $PROJECT_ID --name="Worldbuilding Platform"

# Set active project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable storage-component.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

### Set up IAM and Service Accounts
```bash
# Create service account for deployment
gcloud iam service-accounts create worldbuilding-deploy \
    --description="Service account for worldbuilding platform deployment" \
    --display-name="Worldbuilding Deploy"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:worldbuilding-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:worldbuilding-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:worldbuilding-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

## Step 2: Database Setup (Cloud SQL)

### Create PostgreSQL Instance
```bash
# Create Cloud SQL instance
gcloud sql instances create worldbuilding-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=your-secure-password \
    --storage-type=SSD \
    --storage-size=10GB

# Create database
gcloud sql databases create worldbuilding \
    --instance=worldbuilding-db

# Create database user
gcloud sql users create worldbuilding-user \
    --instance=worldbuilding-db \
    --password=your-user-password
```

### Database Connection Configuration
```bash
# Get connection name
gcloud sql instances describe worldbuilding-db --format="value(connectionName)"

# Example output: project-id:us-central1:worldbuilding-db
```

## Step 3: Backend Deployment (Django API)

### Prepare Django for Cloud Run
```python
# worldbuilding/settings/production.py
import os
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['*']  # Cloud Run handles host validation

# Database configuration for Cloud SQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'worldbuilding'),
        'USER': os.environ.get('DB_USER', 'worldbuilding-user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': f'/cloudsql/{os.environ.get("CLOUD_SQL_CONNECTION_NAME")}',
        'PORT': '5432',
    }
}

# Static files configuration
STATIC_URL = f'https://storage.googleapis.com/{os.environ.get("GS_BUCKET_NAME")}/static/'
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME')

# CORS configuration for frontend
CORS_ALLOWED_ORIGINS = [
    "https://worldbuilding.app",
    "https://www.worldbuilding.app",
]

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=worldbuilding.settings.production

# Run migrations and start server
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 worldbuilding.wsgi:application
```

### Deploy Backend to Cloud Run
```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/worldbuilding-backend

gcloud run deploy worldbuilding-backend \
    --image gcr.io/$PROJECT_ID/worldbuilding-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $PROJECT_ID:us-central1:worldbuilding-db \
    --set-env-vars "CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:us-central1:worldbuilding-db" \
    --set-env-vars "DB_NAME=worldbuilding" \
    --set-env-vars "DB_USER=worldbuilding-user" \
    --set-secrets "DB_PASSWORD=db-password:latest" \
    --set-env-vars "GS_BUCKET_NAME=worldbuilding-static-assets" \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10
```

## Step 4: Frontend Deployment (Next.js)

### Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### Deploy Frontend to Cloud Run
```bash
# Build and deploy frontend
gcloud builds submit --tag gcr.io/$PROJECT_ID/worldbuilding-frontend

gcloud run deploy worldbuilding-frontend \
    --image gcr.io/$PROJECT_ID/worldbuilding-frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "NEXT_PUBLIC_API_URL=https://worldbuilding-backend-[hash]-uc.a.run.app" \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10
```

## Step 5: Storage and CDN Setup

### Create Storage Bucket
```bash
# Create bucket for static assets
gsutil mb gs://worldbuilding-static-assets

# Set bucket permissions
gsutil iam ch allUsers:objectViewer gs://worldbuilding-static-assets

# Enable CDN
gcloud compute backend-buckets create worldbuilding-static-backend \
    --gcs-bucket-name=worldbuilding-static-assets
```

### Configure Cloud CDN
```bash
# Create URL map
gcloud compute url-maps create worldbuilding-url-map \
    --default-backend-bucket=worldbuilding-static-backend

# Create HTTPS proxy
gcloud compute target-https-proxies create worldbuilding-https-proxy \
    --url-map=worldbuilding-url-map \
    --ssl-certificates=worldbuilding-ssl-cert

# Create forwarding rule
gcloud compute forwarding-rules create worldbuilding-https-rule \
    --global \
    --target-https-proxy=worldbuilding-https-proxy \
    --ports=443
```

## Step 6: Domain and SSL Configuration

### Domain Setup
```bash
# Reserve static IP
gcloud compute addresses create worldbuilding-ip --global

# Get the IP address
gcloud compute addresses describe worldbuilding-ip --global

# Create SSL certificate
gcloud compute ssl-certificates create worldbuilding-ssl-cert \
    --domains=worldbuilding.app,www.worldbuilding.app
```

### DNS Configuration
```
# Add these DNS records to your domain registrar:
A     worldbuilding.app        -> [STATIC_IP_ADDRESS]
CNAME www.worldbuilding.app    -> worldbuilding.app
CNAME api.worldbuilding.app    -> [BACKEND_CLOUD_RUN_URL]
```

## Step 7: Monitoring and Logging

### Set up Cloud Monitoring
```bash
# Enable monitoring API
gcloud services enable monitoring.googleapis.com

# Create notification channel (email)
gcloud alpha monitoring channels create \
    --display-name="Worldbuilding Alerts" \
    --type=email \
    --channel-labels=email_address=admin@worldbuilding.app
```

### Application Monitoring
```typescript
// src/lib/monitoring.ts
import { GoogleCloudMonitoring } from '@google-cloud/monitoring'

const monitoring = new GoogleCloudMonitoring()

export const trackCustomMetric = async (metricName: string, value: number) => {
  const request = {
    name: monitoring.projectPath(process.env.GOOGLE_CLOUD_PROJECT),
    timeSeries: [{
      metric: {
        type: `custom.googleapis.com/${metricName}`,
      },
      points: [{
        interval: {
          endTime: {
            seconds: Date.now() / 1000,
          },
        },
        value: {
          doubleValue: value,
        },
      }],
    }],
  }
  
  await monitoring.createTimeSeries(request)
}
```

## Step 8: Security Configuration

### Cloud Armor Security Policy
```bash
# Create security policy
gcloud compute security-policies create worldbuilding-security-policy \
    --description "Security policy for worldbuilding platform"

# Add rate limiting rule
gcloud compute security-policies rules create 1000 \
    --security-policy worldbuilding-security-policy \
    --expression "true" \
    --action "rate-based-ban" \
    --rate-limit-threshold-count 100 \
    --rate-limit-threshold-interval-sec 60 \
    --ban-duration-sec 600
```

### Environment Secrets
```bash
# Create secrets for sensitive data
echo -n "your-database-password" | gcloud secrets create db-password --data-file=-
echo -n "your-jwt-secret" | gcloud secrets create jwt-secret --data-file=-
echo -n "your-nextauth-secret" | gcloud secrets create nextauth-secret --data-file=-

# Grant access to secrets
gcloud secrets add-iam-policy-binding db-password \
    --member="serviceAccount:worldbuilding-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## Step 9: Automated Deployment Pipeline

### Cloud Build Configuration
```yaml
# cloudbuild.yaml
steps:
  # Backend build and deploy
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/worldbuilding-backend', './backend']
    
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/worldbuilding-backend']
    
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'worldbuilding-backend',
           '--image', 'gcr.io/$PROJECT_ID/worldbuilding-backend',
           '--region', 'us-central1']
    
  # Frontend build and deploy
  - name: 'node:18'
    entrypoint: 'bash'
    args: ['-c', 'cd frontend && npm ci && npm run build']
    
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/worldbuilding-frontend', './frontend']
    
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/worldbuilding-frontend']
    
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'worldbuilding-frontend',
           '--image', 'gcr.io/$PROJECT_ID/worldbuilding-frontend',
           '--region', 'us-central1']

timeout: 1200s
```

### Trigger Setup
```bash
# Connect to GitHub repository
gcloud builds triggers create github \
    --repo-name=worldbuilding-platform \
    --repo-owner=your-github-username \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

## Step 10: Production Configuration

### Environment Variables
```bash
# Backend environment variables
gcloud run services update worldbuilding-backend \
    --set-env-vars "DJANGO_SETTINGS_MODULE=worldbuilding.settings.production" \
    --set-env-vars "DEBUG=False" \
    --set-env-vars "ALLOWED_HOSTS=*" \
    --region us-central1

# Frontend environment variables
gcloud run services update worldbuilding-frontend \
    --set-env-vars "NODE_ENV=production" \
    --set-env-vars "NEXT_PUBLIC_API_URL=https://api.worldbuilding.app" \
    --region us-central1
```

### Health Checks
```bash
# Configure health checks for backend
gcloud run services update worldbuilding-backend \
    --port 8000 \
    --region us-central1

# Configure health checks for frontend
gcloud run services update worldbuilding-frontend \
    --port 3000 \
    --region us-central1
```

## Cost Optimization

### Resource Allocation
```bash
# Backend: Optimize for API workload
gcloud run services update worldbuilding-backend \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --concurrency 100

# Frontend: Optimize for web serving
gcloud run services update worldbuilding-frontend \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 5 \
    --concurrency 100
```

### Estimated Monthly Costs
- **Cloud Run Backend**: $30-80 (based on requests)
- **Cloud Run Frontend**: $20-50 (based on requests)
- **Cloud SQL**: $50-100 (db-f1-micro)
- **Cloud Storage**: $5-20 (static assets)
- **Cloud CDN**: $10-30 (bandwidth)
- **Load Balancer**: $18 (fixed)
- **Total**: $133-298/month

## Monitoring and Alerts

### Set up Monitoring Dashboard
```bash
# Create custom dashboard
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json
```

### Alert Policies
```bash
# High error rate alert
gcloud alpha monitoring policies create \
    --policy-from-file=error-rate-policy.yaml

# High latency alert  
gcloud alpha monitoring policies create \
    --policy-from-file=latency-policy.yaml
```

## Backup and Disaster Recovery

### Database Backups
```bash
# Enable automated backups
gcloud sql instances patch worldbuilding-db \
    --backup-start-time=03:00 \
    --enable-bin-log

# Create on-demand backup
gcloud sql backups create \
    --instance=worldbuilding-db \
    --description="Pre-deployment backup"
```

### Application Backups
```bash
# Export database
gcloud sql export sql worldbuilding-db gs://worldbuilding-backups/db-backup-$(date +%Y%m%d).sql \
    --database=worldbuilding

# Backup static files
gsutil -m cp -r gs://worldbuilding-static-assets gs://worldbuilding-backups/static-$(date +%Y%m%d)
```

## Deployment Checklist

### Pre-Deployment
- [ ] Google Cloud project created and configured
- [ ] Required APIs enabled
- [ ] Service accounts and IAM configured
- [ ] Database instance created and configured
- [ ] Storage buckets created
- [ ] Domain and SSL certificates configured

### Backend Deployment
- [ ] Django settings configured for production
- [ ] Database migrations applied
- [ ] Static files collected and uploaded
- [ ] Environment variables configured
- [ ] Health checks configured
- [ ] Monitoring and logging enabled

### Frontend Deployment
- [ ] Next.js build optimized for production
- [ ] Environment variables configured
- [ ] API endpoints tested
- [ ] CDN configuration verified
- [ ] Performance metrics validated

### Post-Deployment
- [ ] End-to-end testing completed
- [ ] Performance monitoring active
- [ ] Error tracking configured
- [ ] Backup procedures tested
- [ ] Documentation updated

## Troubleshooting Guide

### Common Issues

#### Backend Issues
```bash
# Check backend logs
gcloud run services logs read worldbuilding-backend --region us-central1

# Check database connectivity
gcloud sql connect worldbuilding-db --user=worldbuilding-user

# Test API endpoints
curl https://api.worldbuilding.app/api/health/
```

#### Frontend Issues
```bash
# Check frontend logs
gcloud run services logs read worldbuilding-frontend --region us-central1

# Test frontend accessibility
curl https://worldbuilding.app

# Check build issues
gcloud builds log [BUILD_ID]
```

#### Database Issues
```bash
# Check database status
gcloud sql instances describe worldbuilding-db

# Check database connections
gcloud sql operations list --instance=worldbuilding-db

# Run database migrations
gcloud run jobs execute migrate-job --region us-central1
```

## Security Best Practices

### Application Security
- Use HTTPS everywhere
- Implement proper CORS policies
- Validate all user inputs
- Use parameterized queries
- Implement rate limiting
- Regular security updates

### Infrastructure Security
- Use IAM with least privilege
- Enable audit logging
- Use VPC for internal communication
- Implement network security policies
- Regular security scanning

### Data Security
- Encrypt data at rest and in transit
- Regular database backups
- Implement data retention policies
- Use secrets management
- Monitor for suspicious activity

This comprehensive deployment plan ensures a secure, scalable, and cost-effective deployment of the Collaborative Worldbuilding Platform on Google Cloud Console.