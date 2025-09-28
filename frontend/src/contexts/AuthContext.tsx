import React, { createContext, useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '@/lib/api'
import type { User, UserProfile, LoginCredentials, RegisterData } from '@/types'

interface AuthContextType {
  user: User | null
  profile: UserProfile | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  refreshProfile: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  const isAuthenticated = !!user

  // Check for existing token on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const data = await authAPI.getProfile()
          setUser(data.user)
          setProfile(data.profile)
        } catch (error) {
          // Token is invalid, remove it
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      }
      setIsLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (credentials: LoginCredentials) => {
    try {
      const data = await authAPI.login(credentials)
      
      // Store tokens
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      
      // Set user data
      setUser(data.user)
      
      // Get full profile
      const profileData = await authAPI.getProfile()
      setProfile(profileData.profile)
      
      // Redirect to worlds page
      navigate('/worlds')
    } catch (error: any) {
      // Re-throw error to be handled by the component
      throw new Error(error.response?.data?.error?.message || 'Login failed')
    }
  }

  const register = async (data: RegisterData) => {
    try {
      const response = await authAPI.register(data)
      
      // Auto-login after registration
      await login({
        username: data.username,
        password: data.password,
      })
    } catch (error: any) {
      // Re-throw error to be handled by the component
      throw new Error(error.response?.data?.error?.message || 'Registration failed')
    }
  }

  const logout = () => {
    // Clear tokens
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    
    // Clear user data
    setUser(null)
    setProfile(null)
    
    // Call logout endpoint (fire and forget)
    authAPI.logout().catch(() => {
      // Ignore errors on logout
    })
    
    // Redirect to home
    navigate('/')
  }

  const refreshProfile = async () => {
    try {
      const data = await authAPI.getProfile()
      setUser(data.user)
      setProfile(data.profile)
    } catch (error) {
      console.error('Failed to refresh profile:', error)
    }
  }

  const value: AuthContextType = {
    user,
    profile,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshProfile,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}