# 🐛 Login Debug Guide

## Current Status
- ✅ Backend is working (tested with curl)
- ✅ Auth endpoints return correct data
- ❌ Frontend login not working

## Steps to Debug

### 1. Restart Frontend with New Environment
```bash
# Stop the frontend (Ctrl+C)
# Then restart:
cd frontend
npm run dev
```

### 2. Test Login in Browser
1. Go to http://localhost:3000
2. Click "Sign In"
3. Enter credentials: `admin` / `admin123`
4. Open browser Developer Tools (F12)
5. Check Console tab for errors
6. Check Network tab for API requests

### 3. Expected Behavior
- Should see POST request to `http://localhost:8000/api/auth/login/`
- Should receive 200 response with tokens and user data
- Should redirect to `/worlds` page

### 4. Common Issues to Check

#### CORS Issues
- Check if request is blocked by CORS
- Look for CORS error in console

#### API URL Issues
- Verify request goes to correct URL
- Check if using environment variable

#### Response Handling
- Check if response data is parsed correctly
- Look for JavaScript errors in console

### 5. Manual Test
You can test the API directly in browser console:
```javascript
fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
})
.then(response => response.json())
.then(data => console.log('Success:', data))
.catch(error => console.error('Error:', error));
```

### 6. Check Environment Variables
In browser console, check:
```javascript
console.log('API Base URL:', import.meta.env.VITE_API_BASE_URL);
```

## What to Look For

### In Network Tab
- ✅ Request URL: `http://localhost:8000/api/auth/login/`
- ✅ Method: POST
- ✅ Status: 200
- ✅ Response contains: `access`, `refresh`, `user`

### In Console Tab
- ❌ Any JavaScript errors
- ❌ CORS errors
- ❌ Network errors
- ✅ Debug logs from AuthContext

## Next Steps
1. Restart frontend with environment variable
2. Test login and check browser dev tools
3. Report what you see in console/network tabs