# Frontend Setup Guide

## Quick Start with React + Vite

### 1. Create the Frontend Project

```bash
# Create React app with Vite
npm create vite@latest worldbuilding-frontend -- --template react
cd worldbuilding-frontend
npm install

# Install additional dependencies
npm install axios react-router-dom @headlessui/react @heroicons/react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 2. Configure Tailwind CSS

Update `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Add to `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 3. Environment Configuration

Create `.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 4. Basic Project Structure

```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.jsx
│   │   └── RegisterForm.jsx
│   ├── worlds/
│   │   ├── WorldList.jsx
│   │   ├── WorldDetail.jsx
│   │   └── CreateWorld.jsx
│   ├── content/
│   │   ├── ContentList.jsx
│   │   ├── CreatePage.jsx
│   │   └── CreateCharacter.jsx
│   └── layout/
│       ├── Header.jsx
│       └── Layout.jsx
├── services/
│   ├── api.js
│   └── auth.js
├── hooks/
│   └── useAuth.js
├── pages/
│   ├── Home.jsx
│   ├── Login.jsx
│   ├── Dashboard.jsx
│   └── WorldDetail.jsx
└── App.jsx
```

### 5. Key Features to Implement First

1. **Authentication Flow**
   - Login/Register forms
   - JWT token management
   - Protected routes

2. **World Management**
   - Create new world
   - List user's worlds
   - World detail view

3. **Content Creation**
   - Add pages to world
   - Add characters to world
   - Basic content editor

4. **Timeline View**
   - Chronological content display
   - Filter by content type
   - Search functionality

### 6. API Service Setup

Create `src/services/api.js`:
```javascript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token expiration
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 7. Start Development

```bash
# Start Django backend
python manage.py runserver

# Start frontend (in another terminal)
cd worldbuilding-frontend
npm run dev
```

## Alternative: Simple HTML + JavaScript

If you prefer to start even simpler, I can create a basic HTML page that tests your API endpoints without any build tools.

## Testing Your API First

Before building the frontend, run the API test script:

```bash
python test_api_endpoints.py
```

This will verify all your endpoints work correctly and create test data you can use for frontend development.