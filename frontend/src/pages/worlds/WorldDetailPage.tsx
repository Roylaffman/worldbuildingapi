import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { Globe, Users, Calendar, Plus, FileText, User, BookOpen, Image, Scroll } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { worldsAPI, contentAPI } from '@/lib/api'
import { useToast } from '@/components/ui/Toaster'
import Button from '@/components/ui/Button'
import type { World, Content } from '@/types'

const WorldDetailPage: React.FC = () => {
  const { worldId } = useParams<{ worldId: string }>()
  const { addToast } = useToast()
  
  // Fetch world data
  const { data: world, isLoading: worldLoading, error: worldError } = useQuery({
    queryKey: ['world', worldId],
    queryFn: () => worldsAPI.get(parseInt(worldId!)),
    enabled: !!worldId,
  })

  // Fetch recent content for this world (with error handling)
  const { data: recentPagesData } = useQuery({
    queryKey: ['world-pages', worldId],
    queryFn: () => contentAPI.list(parseInt(worldId!), 'page', { ordering: '-created_at' }),
    enabled: !!worldId,
    retry: false, // Don't retry on 404s
  })

  const { data: recentCharactersData } = useQuery({
    queryKey: ['world-characters', worldId],
    queryFn: () => contentAPI.list(parseInt(worldId!), 'character', { ordering: '-created_at' }),
    enabled: !!worldId,
    retry: false,
  })

  const { data: recentStoriesData } = useQuery({
    queryKey: ['world-stories', worldId],
    queryFn: () => contentAPI.list(parseInt(worldId!), 'story', { ordering: '-created_at' }),
    enabled: !!worldId,
    retry: false,
  })

  const { data: recentEssaysData } = useQuery({
    queryKey: ['world-essays', worldId],
    queryFn: () => contentAPI.list(parseInt(worldId!), 'essay', { ordering: '-created_at' }),
    enabled: !!worldId,
    retry: false,
  })

  // Ensure we always have arrays
  const recentPages = Array.isArray(recentPagesData) ? recentPagesData : []
  const recentCharacters = Array.isArray(recentCharactersData) ? recentCharactersData : []
  const recentStories = Array.isArray(recentStoriesData) ? recentStoriesData : []
  const recentEssays = Array.isArray(recentEssaysData) ? recentEssaysData : []

  if (worldLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-2 text-gray-600">Loading world...</span>
        </div>
      </div>
    )
  }

  if (worldError || !world) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">World not found</h2>
          <p className="text-gray-600 mb-4">The world you're looking for doesn't exist or you don't have access to it.</p>
          <Button asChild>
            <Link to="/worlds">Back to Worlds</Link>
          </Button>
        </div>
      </div>
    )
  }

  const mockWorld = {
    id: parseInt(worldId || '1'),
    title: 'Aethermoor',
    description: 'A mystical realm where magic flows through crystalline formations and ancient forests. The world is divided into several kingdoms, each with their own unique relationship to the magical energies that permeate the land.',
    creator: { username: 'worldbuilder1', first_name: 'Alice', last_name: 'Smith' },
    is_public: true,
    created_at: '2025-01-15T10:30:00Z',
    content_counts: { pages: 12, essays: 3, characters: 8, stories: 5, images: 2 },
    contributor_count: 4,
  }

  const getContentIcon = (type: string) => {
    switch (type) {
      case 'pages': return FileText
      case 'characters': return User
      case 'stories': return BookOpen
      case 'essays': return Scroll
      case 'images': return Image
      default: return FileText
    }
  }

  const allRecentContent = [
    ...recentPages.slice(0, 3).map(item => ({ ...item, type: 'page' })),
    ...recentCharacters.slice(0, 3).map(item => ({ ...item, type: 'character' })),
    ...recentStories.slice(0, 3).map(item => ({ ...item, type: 'story' })),
    ...recentEssays.slice(0, 3).map(item => ({ ...item, type: 'essay' })),
  ].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()).slice(0, 10)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-primary-100 rounded-lg">
              <Globe className="h-8 w-8 text-primary-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {world.title}
              </h1>
              <p className="text-gray-600 mb-4 max-w-3xl">
                {world.description}
              </p>
              <div className="flex items-center space-x-6 text-sm text-gray-500">
                <div className="flex items-center space-x-1">
                  <Users className="h-4 w-4" />
                  <span>{world.contributor_count} contributors</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Calendar className="h-4 w-4" />
                  <span>Created {new Date(world.created_at).toLocaleDateString()}</span>
                </div>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  world.is_public 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {world.is_public ? 'Public' : 'Private'}
                </span>
              </div>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" asChild>
              <Link to={`/worlds/${worldId}/create/page`}>
                <Plus className="h-4 w-4 mr-2" />
                Add Page
              </Link>
            </Button>
            <Button asChild>
              <Link to={`/worlds/${worldId}/create/character`}>
                <Plus className="h-4 w-4 mr-2" />
                Add Character
              </Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Content Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {Object.entries(world.content_counts).map(([type, count]) => {
          const Icon = getContentIcon(type)
          return (
            <Link
              key={type}
              to={`/worlds/${worldId}/${type}`}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className="flex items-center space-x-3">
                <Icon className="h-5 w-5 text-primary-600" />
                <div>
                  <div className="text-2xl font-bold text-gray-900">{count}</div>
                  <div className="text-sm text-gray-600 capitalize">{type}</div>
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      {/* Recent Content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Content</h2>
        {allRecentContent.length > 0 ? (
          <div className="space-y-4">
            {allRecentContent.map((content) => {
              const Icon = getContentIcon(content.type + 's')
              return (
                <Link
                  key={`${content.type}-${content.id}`}
                  to={`/worlds/${worldId}/content/${content.type}/${content.id}`}
                  className="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="p-2 bg-primary-100 rounded-lg">
                    <Icon className="h-4 w-4 text-primary-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{content.title}</h3>
                    <p className="text-sm text-gray-600">
                      {content.type.charAt(0).toUpperCase() + content.type.slice(1)} • 
                      Created {new Date(content.created_at).toLocaleDateString()} • 
                      by {content.author.first_name || content.author.username}
                    </p>
                  </div>
                </Link>
              )
            })}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>No content yet</p>
            <p className="text-sm mt-2">Start by creating your first page or character!</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default WorldDetailPage