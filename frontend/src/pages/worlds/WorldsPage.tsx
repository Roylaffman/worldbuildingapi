import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Globe, Users, Calendar } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { worldsAPI } from '@/lib/api'
import { useToast } from '@/components/ui/Toaster'
import Button from '@/components/ui/Button'
import type { World } from '@/types'

const WorldsPage: React.FC = () => {
  const { addToast } = useToast()
  
  // Fetch worlds from API
  const { data: worlds = [], isLoading, error, refetch } = useQuery({
    queryKey: ['worlds'],
    queryFn: () => worldsAPI.list(),
  })

  // Show error if API call fails
  useEffect(() => {
    if (error) {
      addToast({
        type: 'error',
        title: 'Failed to load worlds',
        message: 'Please try refreshing the page.',
      })
    }
  }, [error, addToast])

  // Loading state
  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-2 text-gray-600">Loading worlds...</span>
        </div>
      </div>
    )
  }

  const mockWorlds = [
    {
      id: 1,
      title: 'Aethermoor',
      description: 'A mystical realm where magic flows through crystalline formations and ancient forests.',
      creator: { username: 'worldbuilder1', first_name: 'Alice', last_name: 'Smith' },
      is_public: true,
      created_at: '2025-01-15T10:30:00Z',
      content_counts: { pages: 12, essays: 3, characters: 8, stories: 5, images: 2 },
      contributor_count: 4,
    },
    {
      id: 2,
      title: 'Neon Dystopia 2087',
      description: 'A cyberpunk future where corporations rule and hackers fight for freedom.',
      creator: { username: 'cyberpunk_fan', first_name: 'Bob', last_name: 'Johnson' },
      is_public: false,
      created_at: '2025-01-10T14:20:00Z',
      content_counts: { pages: 8, essays: 1, characters: 15, stories: 3, images: 7 },
      contributor_count: 2,
    },
  ]

  const getTotalContent = (counts: any) => {
    return Object.values(counts).reduce((sum: number, count: any) => sum + count, 0)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Worlds</h1>
          <p className="text-gray-600 mt-2">
            Manage your collaborative worldbuilding projects
          </p>
        </div>
        <Button asChild>
          <Link to="/worlds/create">
            <Plus className="h-4 w-4 mr-2" />
            Create World
          </Link>
        </Button>
      </div>

      {/* Worlds Grid */}
      {worlds.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {worlds.map((world) => (
            <div
              key={world.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <Globe className="h-5 w-5 text-primary-600" />
                    <h3 className="text-lg font-semibold text-gray-900">
                      {world.title}
                    </h3>
                  </div>
                  <div className="flex items-center space-x-1">
                    {world.is_public ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Public
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        Private
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {world.description}
                </p>

                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center space-x-1">
                      <Users className="h-4 w-4" />
                      <span>{world.contributor_count} contributors</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Calendar className="h-4 w-4" />
                      <span>{new Date(world.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="text-sm text-gray-600">
                    <span className="font-medium">{getTotalContent(world.content_counts)}</span> total items
                    <span className="text-gray-400 mx-1">•</span>
                    <span>{world.content_counts.pages} pages</span>
                    <span className="text-gray-400 mx-1">•</span>
                    <span>{world.content_counts.characters} characters</span>
                  </div>
                </div>

                <div className="mt-6 flex space-x-3">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    asChild
                  >
                    <Link to={`/worlds/${world.id}`}>
                      View World
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Globe className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No worlds yet
          </h3>
          <p className="text-gray-600 mb-6">
            Create your first world to start collaborative worldbuilding
          </p>
          <Button asChild>
            <Link to="/worlds/create">
              <Plus className="h-4 w-4 mr-2" />
              Create Your First World
            </Link>
          </Button>
        </div>
      )}
    </div>
  )
}

export default WorldsPage