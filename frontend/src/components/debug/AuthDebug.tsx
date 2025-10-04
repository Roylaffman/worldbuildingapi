import React from 'react'
import { useAuth } from '@/contexts/AuthContext'

const AuthDebug: React.FC = () => {
  const { user, profile, isAuthenticated, isLoading } = useAuth()
  
  if (process.env.NODE_ENV !== 'development') {
    return null
  }

  return (
    <div className="fixed bottom-4 right-4 bg-black text-white p-4 rounded-lg text-xs max-w-sm z-50">
      <div className="font-bold mb-2">Auth Debug</div>
      <div>Loading: {isLoading ? '✅' : '❌'}</div>
      <div>Authenticated: {isAuthenticated ? '✅' : '❌'}</div>
      <div>User: {user ? `${user.username} (${user.email})` : 'None'}</div>
      <div>Profile: {profile ? `${profile.contribution_count} contributions` : 'None'}</div>
      <div>Access Token: {localStorage.getItem('access_token') ? '✅' : '❌'}</div>
      <div>Refresh Token: {localStorage.getItem('refresh_token') ? '✅' : '❌'}</div>
    </div>
  )
}

export default AuthDebug