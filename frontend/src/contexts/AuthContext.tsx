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
      console.log('AuthContext: Attempting login with credentials:', { username: credentials.username })
      const data = await authAPI.login(credentials)
      console.log('AuthContext: Login successful, data:', data)
      
      // Store tokens
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      
      // Set user data from login response
      setUser(data.user)
      setProfile(data.user.profile)
      
      console.log('AuthContext: User and profile set, navigating to worlds')
      // Redirect to worlds page
      navigate('/worlds')
    } catch (error: any) {
      console.error('AuthContext: Login error:', error)
      console.error('AuthContext: Error response:', error.response)
      
      // Re-throw error to be handled by the component
      let errorMessage = 'Login failed'
      
      if (error.response?.data) {
        const data = error.response.data
        errorMessage = data.detail || 
                      data.message || 
                      data.error || 
                      (data.non_field_errors && data.non_field_errors[0]) ||
                      'Login failed'
      } else if (error.message) {
        errorMessage = error.message
      }
      
      throw new Error(errorMessage)
    }
  }

  const register = async (data: RegisterData) => {
    try {
      const response = await authAPI.register(data)
      
      // If registration returns tokens, use them directly
      if (response.tokens) {
        localStorage.setItem('access_token', response.tokens.access)
        localStorage.setItem('refresh_token', response.tokens.refresh)
        setUser(response.user)
        setProfile(response.user.profile)
        navigate('/worlds')
      } else {
        // Auto-login after registration if no tokens returned
        await login({
          username: data.username,
          password: data.password,
        })
      }
    } catch (error: any) {
      // Re-throw error to be handled by the component
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.response?.data?.error || 
                          error.message || 
                          'Registration failed'
      throw new Error(errorMessage)
    }
  }

  const logout = () => {
    const refreshToken = localStorage.getItem('refresh_token')
    
    // Clear tokens
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    
    // Clear user data
    setUser(null)
    setProfile(null)
    
    // Call logout endpoint (fire and forget)
    authAPI.logout(refreshToken || undefined).catch(() => {
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