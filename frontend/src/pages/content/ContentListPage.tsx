import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Plus, FileText, User, BookOpen, Image, Scroll } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { contentAPI, worldsAPI } from '@/lib/api'
import Button from '@/components/ui/Button'
import type { ContentType } from '@/types'

const ContentListPage: React.FC = () => {
  const { worldId, contentType } = useParams<{ worldId: string; contentType: string }>()
  
  // Fetch world data
  const { data: world } = useQuery({
    queryKey: ['world', worldId],
    queryFn: () => worldsAPI.get(parseInt(worldId!)),
    enabled: !!worldId,
  })

  // Fetch content data
  const { data: content = [], isLoading, error } = useQuery({
    queryKey: ['world-content', worldId, contentType],
    queryFn: async () => {
      console.log('ContentListPage: Fetching content for world', worldId, 'type', contentType)
      const result = await contentAPI.list(parseInt(worldId!), contentType as ContentType, { ordering: '-created_at' })
      console.log('ContentListPage: Content fetched:', result)
      return result
    },
    enabled: !!worldId && !!contentType,
  })

  // Debug logging
  React.useEffect(() => {
    console.log('ContentListPage: worldId =', worldId, 'contentType =', contentType)
    console.log('ContentListPage: content =', content)
    console.log('ContentListPage: isLoading =', isLoading)
    console.log('ContentListPage: error =', error)
  }, [worldId, contentType, content, isLoading, error])

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

  const Icon = getContentIcon(contentType || '')
  const singularType = contentType?.slice(0, -1) // Remove 's' from plural

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-2 text-gray-600">Loading {contentType}...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <Button
          variant="ghost"
          asChild
          className="mb-4"
        >
          <Link to={`/worlds/${worldId}`}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to {world?.title || 'World'}
          </Link>
        </Button>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Icon className="h-6 w-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 capitalize">
                {contentType}
              </h1>
              <p className="text-gray-600">
                {content.length} {content.length === 1 ? singularType : contentType} in {world?.title}
              </p>
            </div>
          </div>
          <Button asChild>
            <Link to={`/worlds/${worldId}/create/${singularType}`}>
              <Plus className="h-4 w-4 mr-2" />
              Create {singularType?.charAt(0).toUpperCase()}{singularType?.slice(1)}
            </Link>
          </Button>
        </div>
      </div>

      {/* Content List */}
      {content.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {content.map((item) => (
            <Link
              key={item.id}
              to={`/worlds/${worldId}/content/${singularType}/${item.id}`}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start space-x-3 mb-4">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <Icon className="h-4 w-4 text-primary-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">
                    {item.title}
                  </h3>
                  <p className="text-sm text-gray-600">
                    by {item.author.first_name || item.author.username}
                  </p>
                </div>
              </div>
              
              <p className="text-gray-700 text-sm line-clamp-3 mb-4">
                {item.content.substring(0, 150)}...
              </p>
              
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{new Date(item.created_at).toLocaleDateString()}</span>
                <div className="flex items-center space-x-2">
                  {item.tags && item.tags.length > 0 && (
                    <span>{item.tags.length} tags</span>
                  )}
                  {item.collaboration_info && (
                    <span>{item.collaboration_info.links_to_count} links</span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Icon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No {contentType} yet
          </h3>
          <p className="text-gray-600 mb-6">
            Create your first {singularType} to get started with this world.
          </p>
          <Button asChild>
            <Link to={`/worlds/${worldId}/create/${singularType}`}>
              <Plus className="h-4 w-4 mr-2" />
              Create {singularType?.charAt(0).toUpperCase()}{singularType?.slice(1)}
            </Link>
          </Button>
        </div>
      )}
    </div>
  )
}

export default ContentListPage