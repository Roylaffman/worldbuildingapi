import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Tag, Hash } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { tagsAPI, worldsAPI } from '@/lib/api'
import Button from '@/components/ui/Button'

const TagsPage: React.FC = () => {
  const { worldId } = useParams<{ worldId: string }>()

  // Fetch world data
  const { data: world } = useQuery({
    queryKey: ['world', worldId],
    queryFn: () => worldsAPI.get(parseInt(worldId!)),
    enabled: !!worldId,
  })

  // Fetch tags data
  const { data: tags = [], isLoading, error } = useQuery({
    queryKey: ['world-tags', worldId],
    queryFn: () => tagsAPI.list(parseInt(worldId!)),
    enabled: !!worldId,
  })

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-2 text-gray-600">Loading tags...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error loading tags</h2>
          <p className="text-gray-600 mb-4">Could not load tags for this world.</p>
          <Button asChild>
            <Link to={`/worlds/${worldId}`}>Back to World</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Navigation */}
      <Button
        variant="ghost"
        asChild
        className="mb-6"
      >
        <Link to={`/worlds/${worldId}`}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to {world?.title || 'World'}
        </Link>
      </Button>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-3 bg-primary-100 rounded-lg">
            <Hash className="h-6 w-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Tags</h1>
            <p className="text-gray-600">Explore content by tags in {world?.title}</p>
          </div>
        </div>
      </div>

      {/* Tags Grid */}
      {tags.length === 0 ? (
        <div className="text-center py-12">
          <Tag className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No tags yet</h3>
          <p className="text-gray-600 mb-4">
            Tags will appear here as content is tagged in this world.
          </p>
          <Button asChild>
            <Link to={`/worlds/${worldId}`}>Explore Content</Link>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {tags.map((tag) => (
            <Link
              key={tag.id}
              to={`/worlds/${worldId}/tags/${tag.name}`}
              className="block p-6 bg-white rounded-lg border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all duration-200"
            >
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <Tag className="h-5 w-5 text-primary-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{tag.name}</h3>
                  <p className="text-sm text-gray-600">
                    Created {new Date(tag.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Stats */}
      {tags.length > 0 && (
        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600 text-center">
            {tags.length} tag{tags.length !== 1 ? 's' : ''} in this world
          </p>
        </div>
      )}
    </div>
  )
}

export default TagsPage