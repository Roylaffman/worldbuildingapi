import React, { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { authAPI, worldsAPI } from '@/lib/api'
import Button from '@/components/ui/Button'

const TestAuthPage: React.FC = () => {
  const { user, profile, isAuthenticated, login, logout } = useAuth()
  const [testResults, setTestResults] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const addResult = (message: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`])
  }

  const testLogin = async () => {
    setIsLoading(true)
    try {
      addResult('Testing login...')
      await login({ username: 'admin', password: 'admin123' })
      addResult('✅ Login successful!')
    } catch (error: any) {
      addResult(`❌ Login failed: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const testAPICall = async () => {
    setIsLoading(true)
    try {
      addResult('Testing API call...')
      const worlds = await worldsAPI.list()
      addResult(`✅ API call successful! Found ${worlds.length} worlds`)
    } catch (error: any) {
      addResult(`❌ API call failed: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const testTokenRefresh = async () => {
    setIsLoading(true)
    try {
      addResult('Testing token refresh...')
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        throw new Error('No refresh token found')
      }
      const result = await authAPI.refresh(refreshToken)
      localStorage.setItem('access_token', result.access)
      addResult('✅ Token refresh successful!')
    } catch (error: any) {
      addResult(`❌ Token refresh failed: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const clearResults = () => {
    setTestResults([])
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow rounded-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Authentication Test Page</h1>
          
          {/* Authentication Status */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Authentication Status</h2>
            <p><strong>Authenticated:</strong> {isAuthenticated ? '✅ Yes' : '❌ No'}</p>
            {user && (
              <>
                <p><strong>Username:</strong> {user.username}</p>
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Name:</strong> {user.first_name} {user.last_name}</p>
              </>
            )}
            {profile && (
              <>
                <p><strong>Contribution Count:</strong> {profile.contribution_count}</p>
                <p><strong>Worlds Created:</strong> {profile.worlds_created}</p>
              </>
            )}
          </div>

          {/* Test Buttons */}
          <div className="mb-6 space-x-4">
            <Button 
              onClick={testLogin} 
              disabled={isLoading || isAuthenticated}
              className="mb-2"
            >
              Test Login
            </Button>
            <Button 
              onClick={testAPICall} 
              disabled={isLoading || !isAuthenticated}
              className="mb-2"
            >
              Test API Call
            </Button>
            <Button 
              onClick={testTokenRefresh} 
              disabled={isLoading || !isAuthenticated}
              className="mb-2"
            >
              Test Token Refresh
            </Button>
            <Button 
              onClick={logout} 
              disabled={isLoading || !isAuthenticated}
              variant="secondary"
              className="mb-2"
            >
              Logout
            </Button>
            <Button 
              onClick={clearResults} 
              variant="outline"
              className="mb-2"
            >
              Clear Results
            </Button>
          </div>

          {/* Test Results */}
          <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm">
            <h3 className="text-white font-semibold mb-2">Test Results:</h3>
            {testResults.length === 0 ? (
              <p className="text-gray-400">No tests run yet...</p>
            ) : (
              <div className="space-y-1">
                {testResults.map((result, index) => (
                  <div key={index}>{result}</div>
                ))}
              </div>
            )}
          </div>

          {/* Token Information */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Token Information</h3>
            <p><strong>Access Token:</strong> {localStorage.getItem('access_token') ? '✅ Present' : '❌ Missing'}</p>
            <p><strong>Refresh Token:</strong> {localStorage.getItem('refresh_token') ? '✅ Present' : '❌ Missing'}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TestAuthPage