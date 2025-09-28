# Frontend Deployment Plan - Google Cloud Console

## Overview

This document outlines a comprehensive plan for developing and deploying a modern frontend for the Collaborative Worldbuilding Platform on Google Cloud Console, integrated with the existing Django REST API backend.

## Architecture Overview

### Technology Stack

#### Frontend Framework
- **React 18** with TypeScript
- **Next.js 14** (App Router) for SSR/SSG capabilities
- **Tailwind CSS** for styling and responsive design
- **Shadcn/ui** component library for consistent UI
- **React Query (TanStack Query)** for API state management
- **Zustand** for client-side state management
- **React Hook Form** with Zod validation

#### Authentication & Security
- **JWT Token Management** with automatic refresh
- **NextAuth.js** for authentication flows
- **Secure HTTP-only cookies** for token storage
- **CSRF protection** and XSS prevention

#### Real-time Features
- **WebSocket connections** for live collaboration
- **Server-Sent Events** for notifications
- **Optimistic updates** for better UX

#### Development Tools
- **TypeScript** for type safety
- **ESLint + Prettier** for code quality
- **Husky** for git hooks
- **Jest + React Testing Library** for testing
- **Storybook** for component development

### Google Cloud Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Cloud Run     │    │   Cloud Run     │                │
│  │   (Frontend)    │◄──►│   (Backend)     │                │
│  │   Next.js App   │    │   Django API    │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                         │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Cloud Storage   │    │ Cloud SQL       │                │
│  │ (Static Assets) │    │ (PostgreSQL)    │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Cloud CDN       │    │ Cloud Memorystore│               │
│  │ (Global Cache)  │    │ (Redis Cache)   │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Load Balancer   │    │ Cloud Armor     │                │
│  │ (Traffic Mgmt)  │    │ (Security)      │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## Frontend Application Structure

### Project Structure
```
worldbuilding-frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/            # Authentication routes
│   │   ├── worlds/            # World management
│   │   ├── dashboard/         # User dashboard
│   │   └── layout.tsx         # Root layout
│   ├── components/            # Reusable components
│   │   ├── ui/               # Base UI components
│   │   ├── forms/            # Form components
│   │   ├── layout/           # Layout components
│   │   └── features/         # Feature-specific components
│   ├── lib/                  # Utilities and configurations
│   │   ├── api/              # API client and types
│   │   ├── auth/             # Authentication logic
│   │   ├── utils/            # Helper functions
│   │   └── validations/      # Zod schemas
│   ├── hooks/                # Custom React hooks
│   ├── stores/               # Zustand stores
│   ├── types/                # TypeScript type definitions
│   └── styles/               # Global styles
├── public/                   # Static assets
├── docs/                     # Documentation
├── tests/                    # Test files
└── deployment/               # Deployment configurations
```

### Core Features & Pages

#### 1. Authentication System
- **Login/Register Pages** with form validation
- **Password Reset** flow
- **Email Verification** (optional)
- **Profile Management** page

#### 2. Dashboard
- **Personal Dashboard** with recent activity
- **World Overview** cards
- **Quick Actions** (create world, join world)
- **Collaboration Statistics**

#### 3. World Management
- **World List** with search and filtering
- **World Creation** wizard
- **World Settings** (for creators)
- **Contributor Management**

#### 4. Content Creation & Management
- **Content Editor** with rich text support
- **Page Creation/Viewing**
- **Character Profiles** with structured data
- **Story Writing** interface
- **Image Upload** and gallery

#### 5. Collaboration Features
- **Real-time Editing** indicators
- **Content Linking** interface
- **Tag Management** system
- **Attribution Display**
- **Activity Timeline**

#### 6. Discovery & Navigation
- **Content Search** with filters
- **Tag-based Discovery**
- **Related Content** suggestions
- **World Timeline** view

## Deployment Strategy

### Google Cloud Services

#### 1. Cloud Run (Frontend Hosting)
```yaml
# Frontend Service Configuration
service: worldbuilding-frontend
region: us-central1
platform: managed
cpu: 1000m
memory: 512Mi
min-instances: 0
max-instances: 10
concurrency: 100
```

**Benefits:**
- Serverless scaling
- Pay-per-use pricing
- Automatic HTTPS
- Container-based deployment

#### 2. Cloud Storage (Static Assets)
- **Bucket**: `worldbuilding-static-assets`
- **CDN Integration**: Cloud CDN for global distribution
- **Asset Types**: Images, fonts, icons, build artifacts

#### 3. Cloud CDN (Content Delivery)
- **Global Edge Locations** for fast content delivery
- **Cache Policies** for static assets
- **Compression** and optimization

#### 4. Cloud Load Balancer
- **HTTPS Termination** with SSL certificates
- **Traffic Distribution** between frontend and backend
- **Health Checks** and failover

#### 5. Cloud Armor (Security)
- **DDoS Protection**
- **WAF Rules** for common attacks
- **Rate Limiting** and IP filtering

### Deployment Pipeline

#### CI/CD with Cloud Build
```yaml
# cloudbuild.yaml
steps:
  # Install dependencies
  - name: 'node:18'
    entrypoint: 'npm'
    args: ['ci']
    
  # Run tests
  - name: 'node:18'
    entrypoint: 'npm'
    args: ['run', 'test']
    
  # Build application
  - name: 'node:18'
    entrypoint: 'npm'
    args: ['run', 'build']
    
  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/worldbuilding-frontend', '.']
    
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/worldbuilding-frontend']
    
  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'worldbuilding-frontend',
           '--image', 'gcr.io/$PROJECT_ID/worldbuilding-frontend',
           '--region', 'us-central1',
           '--platform', 'managed']
```

#### Environment Configuration
```bash
# Production Environment Variables
NEXT_PUBLIC_API_URL=https://api.worldbuilding.app
NEXT_PUBLIC_WS_URL=wss://api.worldbuilding.app/ws
NEXTAUTH_URL=https://worldbuilding.app
NEXTAUTH_SECRET=your-secret-key
GOOGLE_CLOUD_PROJECT=your-project-id
```

## Development Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up Next.js project with TypeScript
- [ ] Configure Tailwind CSS and Shadcn/ui
- [ ] Implement authentication system
- [ ] Create basic layout and navigation
- [ ] Set up API client with React Query

### Phase 2: Core Features (Weeks 3-4)
- [ ] Build dashboard and world management
- [ ] Implement content creation forms
- [ ] Add basic content viewing
- [ ] Create user profile management
- [ ] Implement responsive design

### Phase 3: Collaboration (Weeks 5-6)
- [ ] Add tagging and linking interfaces
- [ ] Implement content search and discovery
- [ ] Build timeline and activity views
- [ ] Add real-time collaboration features
- [ ] Create attribution displays

### Phase 4: Polish & Deploy (Weeks 7-8)
- [ ] Add comprehensive error handling
- [ ] Implement loading states and optimizations
- [ ] Write tests and documentation
- [ ] Set up Google Cloud deployment
- [ ] Performance optimization and monitoring

## Technical Implementation Details

### API Integration

#### API Client Setup
```typescript
// lib/api/client.ts
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 3,
    },
  },
})

// API base configuration
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
})

// JWT token interceptor
apiClient.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

#### Type-Safe API Hooks
```typescript
// hooks/api/useWorlds.ts
export const useWorlds = () => {
  return useQuery({
    queryKey: ['worlds'],
    queryFn: () => apiClient.get<World[]>('/worlds/').then(res => res.data),
  })
}

export const useCreateWorld = () => {
  return useMutation({
    mutationFn: (data: CreateWorldData) => 
      apiClient.post<World>('/worlds/', data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['worlds'] })
    },
  })
}
```

### State Management

#### Authentication Store
```typescript
// stores/authStore.ts
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  
  login: async (credentials) => {
    const response = await apiClient.post('/auth/login/', credentials)
    const { user, access, refresh } = response.data
    
    set({ user, token: access, isAuthenticated: true })
    setTokens(access, refresh)
  },
  
  logout: () => {
    set({ user: null, token: null, isAuthenticated: false })
    clearTokens()
  },
}))
```

### Component Architecture

#### Feature-Based Components
```typescript
// components/features/WorldCard.tsx
interface WorldCardProps {
  world: World
  onEdit?: (world: World) => void
  onDelete?: (worldId: string) => void
}

export const WorldCard: React.FC<WorldCardProps> = ({ 
  world, 
  onEdit, 
  onDelete 
}) => {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle>{world.title}</CardTitle>
        <CardDescription>{world.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-center">
          <Badge variant="secondary">
            {world.content_counts.total} items
          </Badge>
          <div className="flex gap-2">
            {onEdit && (
              <Button variant="outline" size="sm" onClick={() => onEdit(world)}>
                Edit
              </Button>
            )}
            {onDelete && (
              <Button 
                variant="destructive" 
                size="sm" 
                onClick={() => onDelete(world.id)}
              >
                Delete
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
```

## Google Cloud Deployment Configuration

### Dockerfile
```dockerfile
# Frontend Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

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

### Cloud Run Service Configuration
```yaml
# service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: worldbuilding-frontend
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      containers:
      - image: gcr.io/PROJECT_ID/worldbuilding-frontend
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.worldbuilding.app"
        resources:
          limits:
            cpu: 1000m
            memory: 512Mi
```

### Terraform Infrastructure
```hcl
# main.tf
resource "google_cloud_run_service" "frontend" {
  name     = "worldbuilding-frontend"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/worldbuilding-frontend"
        
        ports {
          container_port = 3000
        }
        
        env {
          name  = "NEXT_PUBLIC_API_URL"
          value = google_cloud_run_service.backend.status[0].url
        }
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }
  }
}

resource "google_cloud_run_domain_mapping" "frontend" {
  location = var.region
  name     = "worldbuilding.app"

  spec {
    route_name = google_cloud_run_service.frontend.name
  }
}
```

## Security Considerations

### Authentication Security
- **JWT tokens** stored in HTTP-only cookies
- **CSRF protection** with double-submit cookies
- **XSS prevention** with Content Security Policy
- **Secure headers** (HSTS, X-Frame-Options, etc.)

### API Security
- **CORS configuration** for frontend domain
- **Rate limiting** on API endpoints
- **Input validation** on all forms
- **SQL injection prevention** (handled by backend)

### Cloud Security
- **IAM roles** with least privilege principle
- **VPC networking** for internal communication
- **Cloud Armor** for DDoS protection
- **SSL/TLS encryption** for all traffic

## Performance Optimization

### Frontend Performance
- **Code splitting** with Next.js dynamic imports
- **Image optimization** with Next.js Image component
- **Bundle analysis** and tree shaking
- **Service Worker** for offline functionality

### Caching Strategy
- **Static assets** cached at CDN level
- **API responses** cached with React Query
- **Page-level caching** with Next.js ISR
- **Database query caching** with Redis

### Monitoring & Analytics
- **Google Analytics** for user behavior
- **Cloud Monitoring** for performance metrics
- **Error tracking** with Sentry
- **Real User Monitoring** (RUM) data

## Cost Estimation

### Monthly Cost Breakdown (Estimated)
- **Cloud Run Frontend**: $20-50 (based on traffic)
- **Cloud Run Backend**: $30-70 (based on usage)
- **Cloud SQL**: $50-100 (db-f1-micro instance)
- **Cloud Storage**: $5-15 (static assets)
- **Cloud CDN**: $10-30 (bandwidth)
- **Load Balancer**: $18 (fixed cost)
- **Total Estimated**: $133-283/month

### Cost Optimization
- **Serverless scaling** reduces idle costs
- **CDN caching** reduces bandwidth costs
- **Efficient queries** reduce database costs
- **Image optimization** reduces storage costs

## Next Steps

### Immediate Actions
1. **Set up Google Cloud Project** and enable required APIs
2. **Create GitHub repository** for frontend code
3. **Set up development environment** with Next.js
4. **Configure CI/CD pipeline** with Cloud Build
5. **Begin Phase 1 development** (Foundation)

### Success Metrics
- **Page Load Time**: < 2 seconds
- **Time to Interactive**: < 3 seconds
- **Lighthouse Score**: > 90
- **Uptime**: > 99.9%
- **User Satisfaction**: > 4.5/5

This comprehensive plan provides a solid foundation for building and deploying a modern, scalable frontend for the Collaborative Worldbuilding Platform on Google Cloud Console.