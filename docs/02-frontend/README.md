# 🎨 Frontend Documentation

React-based frontend for the Collaborative Worldbuilding Platform.

## 📋 Quick Navigation

### Setup & Configuration
- [Frontend Setup](setup.md) - Development environment setup
- [API Integration](implementation/api-integration.md) - Backend API integration

### Components
- [Tagging System](components/tagging-system.md) - TagManager and ContentLinker
- [Content Management](components/content-management.md) - Content forms and pages
- [UI Components](components/ui-components.md) - Reusable UI components

### Implementation Guides
- [Content Pages](implementation/content-pages.md) - Content detail pages
- [Authentication](implementation/authentication.md) - User authentication
- [API Integration](implementation/api-integration.md) - Frontend-backend communication

### Troubleshooting
- [Common Issues](troubleshooting/common-issues.md) - Frequent frontend problems
- [Debugging Guide](troubleshooting/debugging-guide.md) - Debug techniques
- [Content List Issues](troubleshooting/content-list-issues.md) - Content display problems

## 🛠 Technology Stack

- **Framework**: React 18 with TypeScript
- **Routing**: React Router v6
- **State Management**: React Query (TanStack Query)
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Icons**: Lucide React

## 🏗 Architecture Overview

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── ui/             # Basic UI components
│   │   ├── layout/         # Layout components
│   │   └── content/        # Content-specific components
│   ├── pages/              # Page components
│   │   ├── auth/           # Authentication pages
│   │   ├── worlds/         # World management pages
│   │   ├── content/        # Content pages
│   │   └── tags/           # Tag pages
│   ├── contexts/           # React contexts
│   ├── lib/                # Utilities and API
│   └── types/              # TypeScript types
└── public/                 # Static assets
```

## 🚀 Key Features

### Content Management
- Create and edit pages, essays, characters, stories, images
- Rich text editing and form validation
- File upload for images
- Content organization and navigation

### Tagging & Linking
- Add tags to organize content
- Create bidirectional links between content
- Tag-based content discovery
- Visual tag and link management

### User Experience
- Responsive design for all devices
- Intuitive navigation and UI
- Real-time updates with React Query
- Loading states and error handling

## 📱 Responsive Design

The frontend is fully responsive and works on:
- **Desktop**: 1920x1080 and larger
- **Tablet**: 768x1024 (iPad)
- **Mobile**: 375x667 and larger
- **Mobile Landscape**: Optimized layouts

## 🔧 Development Workflow

1. **Start Development Server**: `npm run dev`
2. **Build for Production**: `npm run build`
3. **Preview Production Build**: `npm run preview`
4. **Type Checking**: `npm run type-check`
5. **Linting**: `npm run lint`

## 📊 Performance Considerations

- **Code Splitting**: Automatic route-based splitting
- **Lazy Loading**: Components loaded on demand
- **Image Optimization**: Responsive images with proper sizing
- **API Caching**: React Query for efficient data fetching
- **Bundle Analysis**: Monitor bundle size and dependencies

## 🧪 Testing

- **Component Testing**: Test individual components
- **Integration Testing**: Test component interactions
- **E2E Testing**: Test complete user workflows
- **API Testing**: Test frontend-backend integration

See [Frontend Testing](../06-testing/frontend/README.md) for detailed testing guides.

## 🐛 Common Issues

- **API Connection**: Check backend server is running on :8000
- **Authentication**: Verify JWT tokens in localStorage
- **Routing**: Ensure React Router configuration is correct
- **Styling**: Check Tailwind CSS compilation
- **State Management**: Verify React Query cache behavior

## 🔗 Related Documentation

- [Backend API](../03-backend/api/README.md) - API endpoints and usage
- [Database Schema](../04-database/schema/README.md) - Data structure
- [Deployment](../05-deployment/README.md) - Production deployment
- [Testing](../06-testing/frontend/README.md) - Frontend testing guides