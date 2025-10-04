# ☁️ AWS Deployment Guide

Complete guide to deploying the Collaborative Worldbuilding Platform on Amazon Web Services.

## 🎯 **Overview**

This guide covers deployment using:
- **AWS ECS Fargate** (Serverless containers)
- **AWS RDS PostgreSQL** (Managed database)
- **AWS S3** (Static files & media storage)
- **AWS CloudFront** (CDN)
- **AWS Application Load Balancer** (Load balancing)
- **AWS CodePipeline** (CI/CD)

## 📋 **Prerequisites**

- AWS account with appropriate permissions
- AWS CLI installed and configured
- Docker installed locally
- Domain name (optional but recommended)

## 🚀 **Quick Setup**

### **1. Initial AWS Setup**
```bash
# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
# Enter your Access Key ID, Secret Access Key, Region (e.g., us-east-1), and output format (json)

# Create IAM role for ECS tasks
aws iam create-role --role-name WorldbuildingECSTaskRole --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'
```

### **2. Create VPC and Networking**
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=worldbuilding-vpc}]'

# Get VPC ID (replace with actual ID from above command)
VPC_ID="vpc-xxxxxxxxx"

# Create subnets
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone us-east-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=worldbuilding-subnet-1}]'
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone us-east-1b --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=worldbuilding-subnet-2}]'

# Create internet gateway
aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=worldbuilding-igw}]'

# Attach internet gateway to VPC
IGW_ID="igw-xxxxxxxxx"
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID
```

## 🗄️ **Database Setup (RDS PostgreSQL)**

### **1. Create Database Subnet Group**
```bash
# Create DB subnet group
aws rds create-db-subnet-group \
    --db-subnet-group-name worldbuilding-db-subnet-group \
    --db-subnet-group-description "Subnet group for Worldbuilding database" \
    --subnet-ids subnet-xxxxxxxxx subnet-yyyyyyyyy
```

### **2. Create RDS Instance**
```bash
# Create security group for database
aws ec2 create-security-group \
    --group-name worldbuilding-db-sg \
    --description "Security group for Worldbuilding database" \
    --vpc-id $VPC_ID

# Get security group ID
DB_SG_ID="sg-xxxxxxxxx"

# Allow PostgreSQL access from ECS
aws ec2 authorize-security-group-ingress \
    --group-id $DB_SG_ID \
    --protocol tcp \
    --port 5432 \
    --source-group $ECS_SG_ID

# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier worldbuilding-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 14.9 \
    --master-username worldbuilding_user \
    --master-user-password "SECURE_PASSWORD_HERE" \
    --allocated-storage 20 \
    --vpc-security-group-ids $DB_SG_ID \
    --db-subnet-group-name worldbuilding-db-subnet-group \
    --backup-retention-period 7 \
    --storage-encrypted \
    --no-multi-az \
    --no-publicly-accessible
```

## 🪣 **Storage Setup (S3)**

### **1. Create S3 Buckets**
```bash
# Create bucket for static files
aws s3 mb s3://worldbuilding-static-files-$(date +%s)

# Create bucket for media files
aws s3 mb s3://worldbuilding-media-files-$(date +%s)

# Set bucket names (replace with actual bucket names)
STATIC_BUCKET="worldbuilding-static-files-1234567890"
MEDIA_BUCKET="worldbuilding-media-files-1234567890"

# Configure static bucket for public read
aws s3api put-bucket-policy --bucket $STATIC_BUCKET --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::'$STATIC_BUCKET'/*"
    }
  ]
}'

# Configure CORS for media bucket
aws s3api put-bucket-cors --bucket $MEDIA_BUCKET --cors-configuration '{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3600
    }
  ]
}'
```

### **2. Create IAM Role for S3 Access**
```bash
# Create policy for S3 access
aws iam create-policy --policy-name WorldbuildingS3Policy --policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::'$STATIC_BUCKET'",
        "arn:aws:s3:::'$STATIC_BUCKET'/*",
        "arn:aws:s3:::'$MEDIA_BUCKET'",
        "arn:aws:s3:::'$MEDIA_BUCKET'/*"
      ]
    }
  ]
}'

# Attach policy to ECS task role
aws iam attach-role-policy \
    --role-name WorldbuildingECSTaskRole \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/WorldbuildingS3Policy
```

## 🔐 **Secrets Management (AWS Secrets Manager)**

### **1. Store Application Secrets**
```bash
# Django secret key
aws secretsmanager create-secret \
    --name worldbuilding/django-secret-key \
    --description "Django secret key for Worldbuilding app" \
    --secret-string "your-super-secret-django-key"

# Database credentials
aws secretsmanager create-secret \
    --name worldbuilding/database \
    --description "Database credentials for Worldbuilding app" \
    --secret-string '{
      "username": "worldbuilding_user",
      "password": "SECURE_PASSWORD_HERE",
      "engine": "postgres",
      "host": "worldbuilding-db.xxxxxxxxx.us-east-1.rds.amazonaws.com",
      "port": 5432,
      "dbname": "worldbuilding"
    }'

# Email credentials (if using)
aws secretsmanager create-secret \
    --name worldbuilding/email \
    --description "Email credentials for Worldbuilding app" \
    --secret-string '{
      "host": "smtp.gmail.com",
      "port": 587,
      "username": "your-email@gmail.com",
      "password": "your-app-password"
    }'
```

### **2. Grant ECS Access to Secrets**
```bash
# Create policy for secrets access
aws iam create-policy --policy-name WorldbuildingSecretsPolicy --policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:worldbuilding/*"
      ]
    }
  ]
}'

# Attach policy to ECS task role
aws iam attach-role-policy \
    --role-name WorldbuildingECSTaskRole \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/WorldbuildingSecretsPolicy
```

## 🐳 **Container Setup (ECR)**

### **1. Create ECR Repository**
```bash
# Create ECR repository
aws ecr create-repository --repository-name worldbuilding-backend

# Get login token and login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

### **2. Build and Push Docker Image**
Create `deployment/aws/Dockerfile.aws`:
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

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
RUN pip install gunicorn psycopg2-binary boto3 django-storages

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=worldbuilding.settings.aws

# Create startup script
RUN echo '#!/bin/bash\n\
python manage.py migrate --noinput --settings=worldbuilding.settings.aws\n\
gunicorn --bind 0.0.0.0:8000 --workers 2 worldbuilding.wsgi:application' > start.sh
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
```

```bash
# Build and push image
docker build -f deployment/aws/Dockerfile.aws -t worldbuilding-backend .
docker tag worldbuilding-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/worldbuilding-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/worldbuilding-backend:latest
```

### **3. Create AWS Settings File**
Create `worldbuilding/settings/aws.py`:
```python
from .base import *
import boto3
import json
import os

# AWS Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = AWS_REGION
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

# Secrets Manager
def get_secret(secret_name):
    """Retrieve secret from AWS Secrets Manager"""
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=AWS_REGION
    )
    
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except Exception as e:
        raise e

# Security
DEBUG = False
SECRET_KEY = get_secret('worldbuilding/django-secret-key')
ALLOWED_HOSTS = ['.elb.amazonaws.com', '.amazonaws.com', 'yourdomain.com', 'www.yourdomain.com']

# Database
db_credentials = get_secret('worldbuilding/database')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_credentials['dbname'],
        'USER': db_credentials['username'],
        'PASSWORD': db_credentials['password'],
        'HOST': db_credentials['host'],
        'PORT': db_credentials['port'],
    }
}

# Static files (S3)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

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

## 🚀 **Deploy to ECS Fargate**

### **1. Create ECS Cluster**
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name worldbuilding-cluster
```

### **2. Create Task Definition**
Create `deployment/aws/task-definition.json`:
```json
{
  "family": "worldbuilding-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/WorldbuildingECSTaskRole",
  "containerDefinitions": [
    {
      "name": "worldbuilding-backend",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/worldbuilding-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "AWS_REGION",
          "value": "us-east-1"
        },
        {
          "name": "AWS_STORAGE_BUCKET_NAME",
          "value": "worldbuilding-static-files-1234567890"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/worldbuilding-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://deployment/aws/task-definition.json
```

### **3. Create Application Load Balancer**
```bash
# Create security group for ALB
aws ec2 create-security-group \
    --group-name worldbuilding-alb-sg \
    --description "Security group for Worldbuilding ALB" \
    --vpc-id $VPC_ID

ALB_SG_ID="sg-xxxxxxxxx"

# Allow HTTP and HTTPS traffic
aws ec2 authorize-security-group-ingress --group-id $ALB_SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $ALB_SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0

# Create ALB
aws elbv2 create-load-balancer \
    --name worldbuilding-alb \
    --subnets subnet-xxxxxxxxx subnet-yyyyyyyyy \
    --security-groups $ALB_SG_ID

# Create target group
aws elbv2 create-target-group \
    --name worldbuilding-targets \
    --protocol HTTP \
    --port 8000 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-path /api/health/

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:YOUR_ACCOUNT_ID:loadbalancer/app/worldbuilding-alb/xxxxxxxxx \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:YOUR_ACCOUNT_ID:targetgroup/worldbuilding-targets/xxxxxxxxx
```

### **4. Create ECS Service**
```bash
# Create security group for ECS tasks
aws ec2 create-security-group \
    --group-name worldbuilding-ecs-sg \
    --description "Security group for Worldbuilding ECS tasks" \
    --vpc-id $VPC_ID

ECS_SG_ID="sg-xxxxxxxxx"

# Allow traffic from ALB
aws ec2 authorize-security-group-ingress \
    --group-id $ECS_SG_ID \
    --protocol tcp \
    --port 8000 \
    --source-group $ALB_SG_ID

# Create ECS service
aws ecs create-service \
    --cluster worldbuilding-cluster \
    --service-name worldbuilding-backend-service \
    --task-definition worldbuilding-backend:1 \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxxxxx,subnet-yyyyyyyyy],securityGroups=[$ECS_SG_ID],assignPublicIp=ENABLED}" \
    --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:YOUR_ACCOUNT_ID:targetgroup/worldbuilding-targets/xxxxxxxxx,containerName=worldbuilding-backend,containerPort=8000
```

## 🌐 **Frontend Deployment (S3 + CloudFront)**

### **1. Build and Deploy Frontend**
```bash
cd frontend

# Create production environment file
cat > .env.production << EOF
VITE_API_BASE_URL=https://worldbuilding-alb-xxxxxxxxx.us-east-1.elb.amazonaws.com/api
VITE_APP_TITLE=Collaborative Worldbuilding
EOF

# Build for production
npm run build

# Create S3 bucket for frontend
aws s3 mb s3://worldbuilding-frontend-$(date +%s)
FRONTEND_BUCKET="worldbuilding-frontend-1234567890"

# Upload build files
aws s3 sync dist/ s3://$FRONTEND_BUCKET/

# Configure bucket for static website hosting
aws s3 website s3://$FRONTEND_BUCKET --index-document index.html --error-document index.html

# Set bucket policy for public read
aws s3api put-bucket-policy --bucket $FRONTEND_BUCKET --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::'$FRONTEND_BUCKET'/*"
    }
  ]
}'
```

### **2. Create CloudFront Distribution**
```bash
# Create CloudFront distribution
aws cloudfront create-distribution --distribution-config '{
  "CallerReference": "worldbuilding-'$(date +%s)'",
  "Comment": "Worldbuilding Frontend Distribution",
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-'$FRONTEND_BUCKET'",
    "ViewerProtocolPolicy": "redirect-to-https",
    "MinTTL": 0,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    }
  },
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-'$FRONTEND_BUCKET'",
        "DomainName": "'$FRONTEND_BUCKET'.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "Enabled": true,
  "DefaultRootObject": "index.html"
}'
```

## 🔄 **CI/CD Setup (CodePipeline)**

### **1. Create CodeBuild Project**
Create `deployment/aws/buildspec.yml`:
```yaml
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
  build:
    commands:
      - echo Build started on `date`
      - echo Building the Docker image...
      - docker build -f deployment/aws/Dockerfile.aws -t $IMAGE_REPO_NAME:$IMAGE_TAG .
      - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
  post_build:
    commands:
      - echo Build completed on `date`
      - echo Pushing the Docker image...
      - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
      - echo Writing image definitions file...
      - printf '[{"name":"worldbuilding-backend","imageUri":"%s"}]' $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG > imagedefinitions.json

artifacts:
  files:
    - imagedefinitions.json
```

```bash
# Create CodeBuild project
aws codebuild create-project \
    --name worldbuilding-build \
    --source type=GITHUB,location=https://github.com/Roylaffman/worldbuildingapi.git \
    --artifacts type=CODEPIPELINE \
    --environment type=LINUX_CONTAINER,image=aws/codebuild/standard:5.0,computeType=BUILD_GENERAL1_MEDIUM,privilegedMode=true \
    --service-role arn:aws:iam::YOUR_ACCOUNT_ID:role/CodeBuildServiceRole
```

### **2. Create CodePipeline**
```bash
# Create CodePipeline
aws codepipeline create-pipeline --cli-input-json '{
  "pipeline": {
    "name": "worldbuilding-pipeline",
    "roleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/CodePipelineServiceRole",
    "artifactStore": {
      "type": "S3",
      "location": "worldbuilding-codepipeline-artifacts"
    },
    "stages": [
      {
        "name": "Source",
        "actions": [
          {
            "name": "Source",
            "actionTypeId": {
              "category": "Source",
              "owner": "ThirdParty",
              "provider": "GitHub",
              "version": "1"
            },
            "configuration": {
              "Owner": "Roylaffman",
              "Repo": "worldbuildingapi",
              "Branch": "main",
              "OAuthToken": "YOUR_GITHUB_TOKEN"
            },
            "outputArtifacts": [
              {
                "name": "SourceOutput"
              }
            ]
          }
        ]
      },
      {
        "name": "Build",
        "actions": [
          {
            "name": "Build",
            "actionTypeId": {
              "category": "Build",
              "owner": "AWS",
              "provider": "CodeBuild",
              "version": "1"
            },
            "configuration": {
              "ProjectName": "worldbuilding-build"
            },
            "inputArtifacts": [
              {
                "name": "SourceOutput"
              }
            ],
            "outputArtifacts": [
              {
                "name": "BuildOutput"
              }
            ]
          }
        ]
      },
      {
        "name": "Deploy",
        "actions": [
          {
            "name": "Deploy",
            "actionTypeId": {
              "category": "Deploy",
              "owner": "AWS",
              "provider": "ECS",
              "version": "1"
            },
            "configuration": {
              "ClusterName": "worldbuilding-cluster",
              "ServiceName": "worldbuilding-backend-service",
              "FileName": "imagedefinitions.json"
            },
            "inputArtifacts": [
              {
                "name": "BuildOutput"
              }
            ]
          }
        ]
      }
    ]
  }
}'
```

## 📊 **Monitoring and Logging**

### **1. CloudWatch Setup**
```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/worldbuilding-backend

# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
    --dashboard-name "Worldbuilding-Dashboard" \
    --dashboard-body file://deployment/aws/dashboard.json
```

### **2. Set up Alarms**
```bash
# Create alarm for high CPU usage
aws cloudwatch put-metric-alarm \
    --alarm-name "Worldbuilding-High-CPU" \
    --alarm-description "Alarm when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2

# Create alarm for high error rate
aws cloudwatch put-metric-alarm \
    --alarm-name "Worldbuilding-High-Errors" \
    --alarm-description "Alarm when error rate exceeds 5%" \
    --metric-name HTTPCode_Target_5XX_Count \
    --namespace AWS/ApplicationELB \
    --statistic Sum \
    --period 300 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

## 💰 **Cost Optimization**

### **1. Auto Scaling**
```bash
# Create auto scaling target
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/worldbuilding-cluster/worldbuilding-backend-service \
    --min-capacity 1 \
    --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/worldbuilding-cluster/worldbuilding-backend-service \
    --policy-name worldbuilding-scaling-policy \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
      "TargetValue": 70.0,
      "PredefinedMetricSpecification": {
        "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
      }
    }'
```

### **2. Cost Monitoring**
```bash
# Create budget
aws budgets create-budget \
    --account-id YOUR_ACCOUNT_ID \
    --budget '{
      "BudgetName": "Worldbuilding-Budget",
      "BudgetLimit": {
        "Amount": "50",
        "Unit": "USD"
      },
      "TimeUnit": "MONTHLY",
      "BudgetType": "COST"
    }'
```

## 🎯 **Production Checklist**

- [ ] VPC and networking configured
- [ ] RDS PostgreSQL instance created
- [ ] S3 buckets created and configured
- [ ] ECR repository created
- [ ] Docker image built and pushed
- [ ] ECS cluster and service deployed
- [ ] Application Load Balancer configured
- [ ] Frontend deployed to S3 + CloudFront
- [ ] SSL certificate configured
- [ ] Monitoring and alerts set up
- [ ] Auto scaling configured
- [ ] CI/CD pipeline set up
- [ ] Budget alerts configured

## 📋 **Estimated Costs**

**Monthly costs for small-medium usage:**
- ECS Fargate: $15-30 (2 tasks, 0.25 vCPU, 0.5 GB RAM)
- RDS db.t3.micro: $12-20
- S3 Storage: $1-5
- CloudFront: $1-10
- Application Load Balancer: $16-25
- **Total: ~$45-90/month**

This AWS setup provides a robust, scalable, and cost-effective solution for your collaborative worldbuilding platform! ☁️🚀