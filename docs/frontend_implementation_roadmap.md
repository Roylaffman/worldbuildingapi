# Frontend Implementation Roadmap

## Quick Start Guide

### Prerequisites
- Node.js 18+ installed
- Google Cloud CLI installed and configured
- Docker installed for containerization
- Git repository set up

### Initial Setup Commands
```bash
# 1. Create Next.js project
npx create-next-app@latest worldbuilding-frontend --typescript --tailwind --eslint --app --src-dir

# 2. Navigate to project
cd worldbuilding-frontend

# 3. Install additional dependencies
npm install @tanstack/react-query zustand @hookform/react-hook-form zod @radix-ui/react-* class-variance-authority clsx tailwind-merge lucide-react

# 4. Install development dependencies
npm install -D @types/node @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom

# 5. Initialize Google Cloud
gcloud init
gcloud config set project YOUR_PROJECT_ID
```

## Phase 1: Foundation Setup (Week 1)

### Day 1-2: Project Initialization
- [ ] **Create Next.js project** with TypeScript and Tailwind
- [ ] **Set up project structure** according to plan
- [ ] **Configure ESLint and Prettier** for code quality
- [ ] **Set up Shadcn/ui** component library
- [ ] **Create basic layout components**

### Day 3-4: Authentication System
- [ ] **Implement JWT token management**
- [ ] **Create login/register forms** with validation
- [ ] **Set up protected route wrapper**
- [ ] **Create authentication context/store**
- [ ] **Add password reset functionality**

### Day 5-7: API Integration
- [ ] **Set up Axios client** with interceptors
- [ ] **Configure React Query** for API state management
- [ ] **Create TypeScript types** for API responses
- [ ] **Implement error handling** and retry logic
- [ ] **Add loading states** and error boundaries

## Phase 2: Core Features (Week 2)

### Day 8-10: Dashboard & Navigation
- [ ] **Create main dashboard** layout
- [ ] **Implement navigation** with active states
- [ ] **Build user profile** management
- [ ] **Add responsive design** for mobile
- [ ] **Create world overview** cards

### Day 11-14: World Management
- [ ] **Build world creation** wizard/form
- [ ] **Implement world listing** with search/filter
- [ ] **Create world detail** pages
- [ ] **Add world settings** for creators
- [ ] **Implement contributor** management

## Phase 3: Content Creation (Week 3)

### Day 15-17: Content Forms
- [ ] **Create rich text editor** for content
- [ ] **Build page creation** forms
- [ ] **Implement character** profile forms
- [ ] **Create story writing** interface
- [ ] **Add form validation** with Zod schemas

### Day 18-21: Content Display
- [ ] **Build content viewing** components
- [ ] **Implement content** detail pages
- [ ] **Create content cards** for listings
- [ ] **Add content search** and filtering
- [ ] **Implement pagination** for content lists

## Phase 4: Collaboration Features (Week 4)

### Day 22-24: Tagging & Linking
- [ ] **Create tag management** interface
- [ ] **Implement content tagging** system
- [ ] **Build content linking** interface
- [ ] **Add tag-based** content discovery
- [ ] **Create related content** suggestions

### Day 25-28: Timeline & Attribution
- [ ] **Build world timeline** view
- [ ] **Implement chronological** filtering
- [ ] **Create attribution** displays
- [ ] **Add collaboration** statistics
- [ ] **Build activity** feed components

## Google Cloud Deployment Setup

### Step 1: Google Cloud Project Setup
```bash
# Create new project
gcloud projects create worldbuilding-app --name="Worldbuilding Platform"

# Set project
gcloud config set project worldbuilding-app

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable sql-component.googleapis.com
```

### Step 2: Container Registry Setup
```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Build and push initial image
docker build -t gcr.io/worldbuilding-app/frontend .
docker push gcr.io/worldbuilding-app/frontend
```

### Step 3: Cloud Run Deployment
```bash
# Deploy to Cloud Run
gcloud run deploy worldbuilding-frontend \
  --image gcr.io/worldbuilding-app/frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 3000 \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10
```

### Step 4: Domain Configuration
```bash
# Map custom domain
gcloud run domain-mappings create \
  --service worldbuilding-frontend \
  --domain worldbuilding.app \
  --region us-central1
```

## Key Implementation Files

### 1. API Client Configuration
```typescript
// src/lib/api/client.ts
import axios from 'axios'
import { getAuthToken, refreshAuthToken } from '@/lib/auth'

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth token
apiClient.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        await refreshAuthToken()
        return apiClient.request(error.config)
      } catch (refreshError) {
        // Redirect to login
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)
```

### 2. Authentication Store
```typescript
// src/stores/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  username: string
  email: string
  first_name: string
  last_name: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (credentials) => {
        const response = await apiClient.post('/auth/login/', credentials)
        const { user, access } = response.data
        
        set({ 
          user, 
          token: access, 
          isAuthenticated: true 
        })
      },

      logout: () => {
        set({ 
          user: null, 
          token: null, 
          isAuthenticated: false 
        })
      },

      updateUser: (userData) => {
        const currentUser = get().user
        if (currentUser) {
          set({ user: { ...currentUser, ...userData } })
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user, 
        token: state.token, 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
)
```

### 3. World Management Hook
```typescript
// src/hooks/api/useWorlds.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api/client'

export interface World {
  id: string
  title: string
  description: string
  creator: {
    id: string
    username: string
    first_name: string
    last_name: string
  }
  is_public: boolean
  created_at: string
  content_counts: {
    pages: number
    essays: number
    characters: number
    stories: number
    images: number
  }
  contributor_count: number
}

export const useWorlds = () => {
  return useQuery({
    queryKey: ['worlds'],
    queryFn: async () => {
      const response = await apiClient.get<World[]>('/worlds/')
      return response.data
    },
  })
}

export const useCreateWorld = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (data: CreateWorldData) => {
      const response = await apiClient.post<World>('/worlds/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['worlds'] })
    },
  })
}

export const useWorld = (worldId: string) => {
  return useQuery({
    queryKey: ['worlds', worldId],
    queryFn: async () => {
      const response = await apiClient.get<World>(`/worlds/${worldId}/`)
      return response.data
    },
    enabled: !!worldId,
  })
}
```

### 4. Main Layout Component
```typescript
// src/components/layout/MainLayout.tsx
import { Navigation } from './Navigation'
import { UserMenu } from './UserMenu'
import { Sidebar } from './Sidebar'

interface MainLayoutProps {
  children: React.ReactNode
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="flex">
        <Sidebar className="w-64 hidden lg:block" />
        
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
```

### 5. World Creation Form
```typescript
// src/components/forms/CreateWorldForm.tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useCreateWorld } from '@/hooks/api/useWorlds'

const createWorldSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters'),
  description: z.string().min(10, 'Description must be at least 10 characters'),
  is_public: z.boolean().default(true),
})

type CreateWorldFormData = z.infer<typeof createWorldSchema>

export const CreateWorldForm: React.FC = () => {
  const createWorld = useCreateWorld()
  
  const form = useForm<CreateWorldFormData>({
    resolver: zodResolver(createWorldSchema),
    defaultValues: {
      title: '',
      description: '',
      is_public: true,
    },
  })

  const onSubmit = async (data: CreateWorldFormData) => {
    try {
      await createWorld.mutateAsync(data)
      // Handle success (redirect, show toast, etc.)
    } catch (error) {
      // Handle error
    }
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Input
          {...form.register('title')}
          placeholder="World Title"
          error={form.formState.errors.title?.message}
        />
      </div>
      
      <div>
        <Textarea
          {...form.register('description')}
          placeholder="World Description"
          error={form.formState.errors.description?.message}
        />
      </div>
      
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          {...form.register('is_public')}
          id="is_public"
        />
        <label htmlFor="is_public">Make world public</label>
      </div>
      
      <Button 
        type="submit" 
        disabled={createWorld.isPending}
        className="w-full"
      >
        {createWorld.isPending ? 'Creating...' : 'Create World'}
      </Button>
    </form>
  )
}
```

## Deployment Automation

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Google Cloud Run

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Build application
      run: npm run build
    
    - name: Setup Google Cloud CLI
      uses: google-github-actions/setup-gcloud@v1
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ secrets.GCP_PROJECT_ID }}
    
    - name: Configure Docker
      run: gcloud auth configure-docker
    
    - name: Build and push Docker image
      run: |
        docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/worldbuilding-frontend .
        docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/worldbuilding-frontend
    
    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy worldbuilding-frontend \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/worldbuilding-frontend \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated
```

### Environment Configuration
```bash
# .env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-dev-secret

# .env.production (production)
NEXT_PUBLIC_API_URL=https://api.worldbuilding.app
NEXT_PUBLIC_WS_URL=wss://api.worldbuilding.app/ws
NEXTAUTH_URL=https://worldbuilding.app
NEXTAUTH_SECRET=your-production-secret
```

## Testing Strategy

### Unit Tests Setup
```typescript
// jest.config.js
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
}

module.exports = createJestConfig(customJestConfig)
```

### Component Tests Example
```typescript
// src/components/__tests__/WorldCard.test.tsx
import { render, screen } from '@testing-library/react'
import { WorldCard } from '../features/WorldCard'

const mockWorld = {
  id: '1',
  title: 'Test World',
  description: 'A test world',
  creator: { id: '1', username: 'testuser' },
  is_public: true,
  created_at: '2025-01-01T00:00:00Z',
  content_counts: { pages: 5, essays: 2, characters: 3, stories: 1, images: 0 },
  contributor_count: 2,
}

describe('WorldCard', () => {
  it('renders world information correctly', () => {
    render(<WorldCard world={mockWorld} />)
    
    expect(screen.getByText('Test World')).toBeInTheDocument()
    expect(screen.getByText('A test world')).toBeInTheDocument()
    expect(screen.getByText('11 items')).toBeInTheDocument()
  })
})
```

## Performance Optimization

### Next.js Configuration
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['storage.googleapis.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
```

### Bundle Analysis
```bash
# Install bundle analyzer
npm install --save-dev @next/bundle-analyzer

# Analyze bundle
npm run build && npm run analyze
```

## Monitoring & Analytics

### Error Tracking Setup
```typescript
// src/lib/monitoring.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
})

export { Sentry }
```

### Performance Monitoring
```typescript
// src/lib/analytics.ts
import { Analytics } from '@vercel/analytics/react'

export const trackEvent = (eventName: string, properties?: Record<string, any>) => {
  if (typeof window !== 'undefined') {
    // Track custom events
    gtag('event', eventName, properties)
  }
}
```

This roadmap provides a comprehensive, step-by-step approach to building and deploying the frontend on Google Cloud Console. Each phase builds upon the previous one, ensuring a solid foundation while maintaining development momentum.