import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { Menu, X, User, LogOut, Settings, BookOpen, Plus } from 'lucide-react'
import Button from '@/components/ui/Button'

const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    setIsUserMenuOpen(false)
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and main navigation */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <BookOpen className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">
                Worldbuilding
              </span>
            </Link>

            {/* Desktop navigation */}
            {isAuthenticated && (
              <nav className="hidden md:ml-8 md:flex md:space-x-8">
                <Link
                  to="/worlds"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
                >
                  My Worlds
                </Link>
                <Link
                  to="/worlds/create"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
                >
                  Create World
                </Link>
              </nav>
            )}
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                {/* Create button */}
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => navigate('/worlds/create')}
                  className="hidden sm:flex"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Create
                </Button>

                {/* User menu */}
                <div className="relative">
                  <button
                    onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                    className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 transition-colors"
                  >
                    <div className="h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <User className="h-5 w-5 text-primary-600" />
                    </div>
                    <span className="hidden sm:block text-sm font-medium">
                      {user?.first_name || user?.username}
                    </span>
                  </button>

                  {/* User dropdown */}
                  {isUserMenuOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-50">
                      <div className="py-1">
                        <div className="px-4 py-2 text-sm text-gray-500 border-b border-gray-100">
                          {user?.email}
                        </div>
                        <Link
                          to="/profile"
                          className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                          onClick={() => setIsUserMenuOpen(false)}
                        >
                          <Settings className="h-4 w-4 mr-2" />
                          Profile
                        </Link>
                        <button
                          onClick={handleLogout}
                          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        >
                          <LogOut className="h-4 w-4 mr-2" />
                          Sign out
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-primary-600 text-sm font-medium transition-colors"
                >
                  Sign in
                </Link>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => navigate('/register')}
                >
                  Get started
                </Button>
              </div>
            )}

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 text-gray-700 hover:text-primary-600 transition-colors"
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 py-4">
            {isAuthenticated ? (
              <div className="space-y-2">
                <Link
                  to="/worlds"
                  className="block px-3 py-2 text-gray-700 hover:text-primary-600 text-sm font-medium"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  My Worlds
                </Link>
                <Link
                  to="/worlds/create"
                  className="block px-3 py-2 text-gray-700 hover:text-primary-600 text-sm font-medium"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Create World
                </Link>
                <Link
                  to="/profile"
                  className="block px-3 py-2 text-gray-700 hover:text-primary-600 text-sm font-medium"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Profile
                </Link>
                <button
                  onClick={() => {
                    handleLogout()
                    setIsMobileMenuOpen(false)
                  }}
                  className="block w-full text-left px-3 py-2 text-gray-700 hover:text-primary-600 text-sm font-medium"
                >
                  Sign out
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <Link
                  to="/login"
                  className="block px-3 py-2 text-gray-700 hover:text-primary-600 text-sm font-medium"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Sign in
                </Link>
                <Link
                  to="/register"
                  className="block px-3 py-2 text-gray-700 hover:text-primary-600 text-sm font-medium"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Get started
                </Link>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Click outside to close menus */}
      {(isMobileMenuOpen || isUserMenuOpen) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setIsMobileMenuOpen(false)
            setIsUserMenuOpen(false)
          }}
        />
      )}
    </header>
  )
}

export default Header