# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://worldbuilding_user:password@db:5432/worldbuilding
POSTGRES_DB=worldbuilding
POSTGRES_USER=worldbuilding_user
POSTGRES_PASSWORD=secure_password_here

# Redis (for caching/sessions)
REDIS_URL=redis://redis:6379/0

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Security Settings (for production)
SECURE_SSL_REDIRECT=False
SECURE_PROXY_SSL_HEADER=
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# File Storage (for production)
# AWS_ACCESS_KEY_ID=your-aws-access-key
# AWS_SECRET_ACCESS_KEY=your-aws-secret-key
# AWS_STORAGE_BUCKET_NAME=your-bucket-name
# AWS_S3_REGION_NAME=us-east-1

# Google Cloud Storage (alternative)
# GS_BUCKET_NAME=your-gcs-bucket-name
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Monitoring and Logging
LOG_LEVEL=INFO
SENTRY_DSN=

# Application Settings
SITE_NAME=Collaborative Worldbuilding
SITE_URL=http://localhost:3000
ADMIN_EMAIL=admin@example.com