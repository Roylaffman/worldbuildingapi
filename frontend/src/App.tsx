import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from '@/contexts/AuthContext'
import { ToastProvider } from '@/components/ui/Toaster'
import Layout from '@/components/layout/Layout'
import HomePage from '@/pages/HomePage'
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import WorldsPage from '@/pages/worlds/WorldsPage'
import WorldDetailPage from '@/pages/worlds/WorldDetailPage'
import CreateWorldPage from '@/pages/worlds/CreateWorldPage'
import ContentPage from '@/pages/content/ContentPage'
import ContentListPage from '@/pages/content/ContentListPage'
import CreateContentPage from '@/pages/content/CreateContentPage'
import ProfilePage from '@/pages/profile/ProfilePage'
import TestAuthPage from '@/pages/TestAuthPage'
import TagsPage from '@/pages/tags/TagsPage'
import TagPage from '@/pages/tags/TagPage'
import DocsPage from '@/pages/docs/DocsPage'
import NotFoundPage from '@/pages/NotFoundPage'
import ProtectedRoute from '@/components/auth/ProtectedRoute'

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route path="login" element={<LoginPage />} />
              <Route path="register" element={<RegisterPage />} />
              <Route path="test-auth" element={<TestAuthPage />} />
              <Route path="docs" element={<DocsPage />} />
              <Route path="docs/:section" element={<DocsPage />} />
              
              {/* Protected routes */}
              <Route path="worlds" element={<ProtectedRoute />}>
                <Route index element={<WorldsPage />} />
                <Route path="create" element={<CreateWorldPage />} />
                <Route path=":worldId" element={<WorldDetailPage />} />
                <Route path=":worldId/:contentType" element={<ContentListPage />} />
                <Route path=":worldId/content/:contentType/:contentId" element={<ContentPage />} />
                <Route path=":worldId/create/:contentType" element={<CreateContentPage />} />
                <Route path=":worldId/tags" element={<TagsPage />} />
                <Route path=":worldId/tags/:tagName" element={<TagPage />} />
              </Route>
              
              <Route path="profile" element={<ProtectedRoute />}>
                <Route index element={<ProfilePage />} />
              </Route>
              
              {/* 404 page */}
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </div>
      </AuthProvider>
    </ToastProvider>
  )
}

export default App