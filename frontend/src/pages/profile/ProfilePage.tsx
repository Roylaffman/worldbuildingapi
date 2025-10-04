import React from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { User, Mail, Calendar, BookOpen, Users } from 'lucide-react'

const ProfilePage: React.FC = () => {
  const { user, profile } = useAuth()

  if (!user || !profile) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">Loading profile...</div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {/* Profile Header */}
        <div className="flex items-start space-x-6 mb-8">
          <div className="h-20 w-20 bg-primary-100 rounded-full flex items-center justify-center">
            <User className="h-10 w-10 text-primary-600" />
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">
              {user.first_name && user.last_name 
                ? `${user.first_name} ${user.last_name}`
                : user.username
              }
            </h1>
            <p className="text-gray-600 text-lg">@{user.username}</p>
            {profile.bio && (
              <p className="text-gray-700 mt-2">{profile.bio}</p>
            )}
          </div>
        </div>

        {/* Profile Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <BookOpen className="h-8 w-8 text-primary-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{profile.worlds_created}</div>
            <div className="text-sm text-gray-600">Worlds Created</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <Users className="h-8 w-8 text-primary-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{profile.contribution_count}</div>
            <div className="text-sm text-gray-600">Contributions</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <Calendar className="h-8 w-8 text-primary-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">
              {new Date(user.date_joined).toLocaleDateString()}
            </div>
            <div className="text-sm text-gray-600">Member Since</div>
          </div>
        </div>

        {/* Profile Details */}
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Profile Information</h2>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <Mail className="h-5 w-5 text-gray-400" />
                <span className="text-gray-700">{user.email}</span>
              </div>
              <div className="flex items-center space-x-3">
                <Calendar className="h-5 w-5 text-gray-400" />
                <span className="text-gray-700">
                  Joined {new Date(user.date_joined).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
              </div>
            </div>
          </div>

          {profile.preferred_content_types && profile.preferred_content_types.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Preferred Content Types</h2>
              <div className="flex flex-wrap gap-2">
                {profile.preferred_content_types.map((type) => (
                  <span
                    key={type}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800"
                  >
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="text-center py-8 text-gray-500">
            <p>Recent activity and contributions will be displayed here</p>
            <p className="text-sm mt-2">This feature is coming soon!</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage