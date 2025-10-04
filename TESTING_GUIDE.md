# 🧪 Local Testing Guide

## Quick Start Commands

### Option 1: Manual Setup (Recommended for Development)

#### 1. Backend Setup (Django on port 8000)
```bash
# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up database (SQLite for quick testing)
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Start Django development server
python manage.py runserver
```
**Backend will be available at: http://localhost:8000**

#### 2. Frontend Setup (React on port 3000)
```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
**Frontend will be available at: http://localhost:3000**

### Option 2: Docker Setup (Full Environment)
```bash
# Start all services with Docker
docker-compose up

# This will start:
# - PostgreSQL database on port 5432
# - Django backend on port 8000
# - React frontend on port 3000
```

---

## 🔧 Environment Configuration

### Backend Environment (.env)
Create a `.env` file in the root directory:
```env
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DB_NAME=worldbuilding_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend Environment (frontend/.env)
Create a `.env` file in the frontend directory:
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Collaborative Worldbuilding
```

---

## 🧪 Testing Steps

### 1. Test Backend API (http://localhost:8000)

#### Check API Health
```bash
curl http://localhost:8000/api/
```

#### Test Authentication Endpoints
```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

#### Test with Authentication Token
```bash
# Save the access token from login response, then:
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/worlds/
```

### 2. Test Frontend (http://localhost:3000)

#### Manual Testing Checklist
- [ ] **Home Page**: Visit http://localhost:3000
- [ ] **Registration**: Click "Get Started" → Fill form → Submit
- [ ] **Login**: Click "Sign In" → Enter credentials → Submit
- [ ] **Worlds Page**: After login, should redirect to worlds list
- [ ] **Create World**: Click "Create World" → Fill form → Submit
- [ ] **Profile**: Click user menu → Profile
- [ ] **Logout**: Click user menu → Sign out

### 3. Test Integration

#### Frontend-Backend Connection
1. **Register a new user** on frontend
2. **Check Django admin** at http://localhost:8000/admin (if superuser created)
3. **Verify user appears** in database
4. **Test login/logout** flow
5. **Check JWT tokens** in browser dev tools (localStorage)

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### Backend Issues

**Port 8000 already in use:**
```bash
# Kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

**Database connection errors:**
```bash
# For SQLite (default), just run:
python manage.py migrate

# For PostgreSQL, ensure it's running:
# Windows: Start PostgreSQL service
# Mac: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

**CORS errors:**
- Check `CORS_ALLOWED_ORIGINS` in settings
- Ensure frontend URL is included

#### Frontend Issues

**Port 3000 already in use:**
```bash
# Kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9
```

**API connection errors:**
- Check backend is running on port 8000
- Verify `VITE_API_BASE_URL` in frontend/.env
- Check browser network tab for failed requests

**Module not found errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Docker Issues

**Docker not starting:**
```bash
# Check Docker is running
docker --version
docker-compose --version

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up
```

**Database connection in Docker:**
- Ensure PostgreSQL container is healthy
- Check environment variables in docker-compose.yml

---

## 📊 Verification Checklist

### Backend Verification
- [ ] Django server starts without errors
- [ ] API root accessible at http://localhost:8000/api/
- [ ] User registration works via curl/Postman
- [ ] JWT login returns access/refresh tokens
- [ ] Protected endpoints require authentication
- [ ] Database migrations applied successfully

### Frontend Verification
- [ ] React app loads at http://localhost:3000
- [ ] No console errors in browser dev tools
- [ ] Navigation works (home, login, register)
- [ ] Forms submit without JavaScript errors
- [ ] Responsive design works on mobile/desktop
- [ ] Toast notifications appear for actions

### Integration Verification
- [ ] Frontend can register users via backend API
- [ ] Login flow works end-to-end
- [ ] JWT tokens stored in localStorage
- [ ] Protected routes redirect to login when not authenticated
- [ ] User data displays correctly after login
- [ ] Logout clears tokens and redirects

---

## 🔍 Debugging Tools

### Backend Debugging
```bash
# Run with verbose output
python manage.py runserver --verbosity=2

# Check logs
tail -f logs/django.log

# Run specific tests
python manage.py test collab.test_auth_permissions

# Django shell for debugging
python manage.py shell
```

### Frontend Debugging
```bash
# Run with debug info
npm run dev -- --debug

# Check bundle analysis
npm run build
npm run preview

# TypeScript checking
npx tsc --noEmit
```

### Browser Debugging
- **F12 Developer Tools**
- **Network Tab**: Check API requests/responses
- **Console Tab**: Check for JavaScript errors
- **Application Tab**: Check localStorage for JWT tokens
- **Sources Tab**: Set breakpoints in code

---

## 🚀 Quick Test Script

Save this as `test_setup.py` and run it to verify everything works:

```python
#!/usr/bin/env python3
import requests
import json
import time

def test_backend():
    print("🧪 Testing Backend...")
    
    # Test API root
    try:
        response = requests.get('http://localhost:8000/api/')
        print(f"✅ API Root: {response.status_code}")
    except:
        print("❌ Backend not running on port 8000")
        return False
    
    # Test registration
    try:
        user_data = {
            "username": "testuser123",
            "email": "test123@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123"
        }
        response = requests.post('http://localhost:8000/api/auth/register/', json=user_data)
        print(f"✅ Registration: {response.status_code}")
        
        # Test login
        login_data = {"username": "testuser123", "password": "testpass123"}
        response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
        if response.status_code == 200:
            token = response.json()['access']
            print(f"✅ Login: {response.status_code}")
            
            # Test protected endpoint
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get('http://localhost:8000/api/worlds/', headers=headers)
            print(f"✅ Protected Endpoint: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_frontend():
    print("\n🧪 Testing Frontend...")
    
    try:
        response = requests.get('http://localhost:3000')
        print(f"✅ Frontend: {response.status_code}")
        return True
    except:
        print("❌ Frontend not running on port 3000")
        return False

if __name__ == "__main__":
    print("🚀 Testing Local Setup...\n")
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    if backend_ok and frontend_ok:
        print("\n🎉 All tests passed! Ready for development.")
    else:
        print("\n⚠️  Some tests failed. Check the setup above.")
```

Run with: `python test_setup.py`

---

## 📝 Next Steps After Testing

Once everything is working:

1. **Initialize Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Full-stack worldbuilding platform"
   ```

2. **Create GitHub Repository** and push

3. **Start Development**
   - Connect frontend forms to backend API
   - Implement world creation functionality
   - Add content management features

4. **Run Tests**
   ```bash
   # Backend tests
   python manage.py test
   
   # Frontend tests (when implemented)
   cd frontend && npm test
   ```

Happy testing! 🎉