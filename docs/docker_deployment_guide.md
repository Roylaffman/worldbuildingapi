# 🐳 Docker Full-Stack Deployment Guide

Complete guide to deploying the Collaborative Worldbuilding Platform using Docker.

## 🎯 **Overview**

This guide covers:
- Local development with Docker
- Production deployment setup
- Environment configuration
- Database management
- SSL/HTTPS setup
- Monitoring and logging

## 📋 **Prerequisites**

- Docker and Docker Compose installed
- Domain name (for production)
- SSL certificates (for HTTPS)
- Database credentials

## 🚀 **Quick Start (Development)**

### **1. Clone and Setup**
```bash
git clone https://github.com/Roylaffman/worldbuildingapi.git
cd worldbuildingapi
```

### **2. Environment Configuration**
```bash
# Copy environment templates
cp .env.example .env
cp frontend/.env.example frontend/.env

# Edit environment variables
nano .env
```

### **3. Start Development Stack**
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### **4. Initialize Database**
```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

### **5. Access Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/

## 🏭 **Production Deployment**

### **1. Production Docker Compose**
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d --build
```

### **2. Environment Variables**

Create `.env` file:
```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@db:5432/worldbuilding
POSTGRES_DB=worldbuilding
POSTGRES_USER=worldbuilding_user
POSTGRES_PASSWORD=secure_password_here

# Redis (for caching/sessions)
REDIS_URL=redis://redis:6379/0

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Security
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

Create `frontend/.env`:
```bash
VITE_API_BASE_URL=https://yourdomain.com/api
VITE_APP_TITLE=Collaborative Worldbuilding
```

## 🔧 **Service Configuration**

### **Backend Service (Django)**
The backend runs on port 8000 and includes:
- Django REST API
- Admin interface
- Static file serving
- Database migrations
- Management commands

### **Frontend Service (React)**
The frontend runs on port 80 (nginx) and includes:
- React application
- Static asset serving
- Client-side routing
- Production optimizations

### **Database Service (PostgreSQL)**
- Persistent data storage
- Automatic backups
- Connection pooling
- Performance tuning

### **Reverse Proxy (Nginx)**
- Load balancing
- SSL termination
- Static file serving
- Rate limiting
- Security headers

## 📊 **Monitoring and Logging**

### **View Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail=100 backend
```

### **Service Status**
```bash
# Check running services
docker-compose ps

# Check resource usage
docker stats

# Check service health
docker-compose exec backend python manage.py check
```

## 🗄️ **Database Management**

### **Backup Database**
```bash
# Create backup
docker-compose exec db pg_dump -U worldbuilding_user worldbuilding > backup.sql

# Or with timestamp
docker-compose exec db pg_dump -U worldbuilding_user worldbuilding > "backup_$(date +%Y%m%d_%H%M%S).sql"
```

### **Restore Database**
```bash
# Restore from backup
docker-compose exec -T db psql -U worldbuilding_user worldbuilding < backup.sql
```

### **Database Maintenance**
```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Database inspection
docker-compose exec backend python manage.py inspect_db overview
```

## 🔒 **SSL/HTTPS Setup**

### **Option 1: Let's Encrypt (Recommended)**
```bash
# Install certbot
sudo apt install certbot

# Get certificates
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Update nginx configuration to use certificates
# Certificates will be in /etc/letsencrypt/live/yourdomain.com/
```

### **Option 2: Custom Certificates**
Place your certificates in:
- `ssl/cert.pem` - SSL certificate
- `ssl/key.pem` - Private key

## 🚀 **Scaling and Performance**

### **Horizontal Scaling**
```bash
# Scale backend service
docker-compose up -d --scale backend=3

# Scale with load balancer
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### **Performance Tuning**
```bash
# Optimize database
docker-compose exec backend python manage.py optimize_db

# Clear cache
docker-compose exec backend python manage.py clear_cache

# Collect static files with compression
docker-compose exec backend python manage.py collectstatic --noinput --clear
```

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **Port Conflicts**
```bash
# Check what's using ports
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# Kill processes using ports
sudo kill -9 $(sudo lsof -t -i:8000)
```

#### **Permission Issues**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh
```

#### **Database Connection Issues**
```bash
# Check database status
docker-compose exec db pg_isready -U worldbuilding_user

# Reset database
docker-compose down -v
docker-compose up -d db
docker-compose exec backend python manage.py migrate
```

#### **Frontend Build Issues**
```bash
# Clear node modules and rebuild
docker-compose exec frontend rm -rf node_modules package-lock.json
docker-compose exec frontend npm install
docker-compose restart frontend
```

### **Debug Mode**
```bash
# Run with debug output
DEBUG=True docker-compose up

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 📋 **Maintenance Tasks**

### **Daily**
```bash
# Check service health
docker-compose ps
docker-compose logs --tail=50 backend | grep ERROR
```

### **Weekly**
```bash
# Update images
docker-compose pull
docker-compose up -d

# Database backup
docker-compose exec db pg_dump -U worldbuilding_user worldbuilding > "backup_$(date +%Y%m%d).sql"

# Clean up old images
docker image prune -f
```

### **Monthly**
```bash
# Full system cleanup
docker system prune -f

# Update SSL certificates (if using Let's Encrypt)
sudo certbot renew

# Database maintenance
docker-compose exec backend python manage.py cleanup_old_content --force
```

## 🎯 **Next Steps**

After successful deployment:
1. Set up monitoring (Prometheus/Grafana)
2. Configure automated backups
3. Set up CI/CD pipeline
4. Configure log aggregation
5. Set up health checks
6. Configure auto-scaling

This Docker setup provides a robust, scalable foundation for your collaborative worldbuilding platform! 🚀