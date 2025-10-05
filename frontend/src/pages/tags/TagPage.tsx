import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Tag, FileText, User, BookOpen, Scroll, Image as ImageIcon } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { tagsAPI, worldsAPI } from '@/lib/api'
import Button from '@/components/ui/Button'

const TagPage: React.FC = () => {
  const { worldId, tagName } = useParams<{ worldId: string; tagName: string }>()

  // Fetch world data
  const { data: world } = useQuery({
    queryKey: ['world', worldId],
    queryFn: () => worldsAPI.get(parseInt(worldId!)),
    enabled: !!worldId,
  })

  // Fetch tag data with tagged content
  const { data: tagData, isLoading, error } = useQuery({
    queryKey: ['tag-detail', worldId, tagName],
    queryFn: () => tagsAPI.get(parseInt(worldId!), tagName!),
    enabled: !!worldId && !!tagName,
  })

  const getContentIcon = (type: string) => {
    switch (type) {
      case 'page': return FileText
      case 'character': return User
      case 'story': return BookOpen
      case 'essay': return Scroll
      case 'image': return ImageIcon
      default: return FileText
    }
  }

  const getContentTypeLabel = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1)
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-2 text-gray-600">Loading tag...</span>
        </div>
      </div>
    )
  }

  if (error || !tagData) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Tag not found</h2>
          <p className="text-gray-600 mb-4">The tag "{tagName}" doesn't exist in this world.</p>
          <Button asChild>
            <Link to={`/worlds/${worldId}/tags`}>View All Tags</Link>
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
        <Link to={`/worlds/${worldId}/tags`}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Tags
        </Link>
      </Button>

      {/* Tag Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-primary-100 rounded-lg">
            <Tag className="h-6 w-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">#{tagData.name}</h1>
            <p className="text-gray-600">
              Tag in {world?.title} • Created {new Date(tagData.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>

      {/* Tagged Content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Content tagged with "{tagData.name}"
        </h2>

        {!tagData.tagged_content || tagData.tagged_content.length === 0 ? (
          <div className="text-center py-8">
            <Tag className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No content with this tag</h3>
            <p className="text-gray-600 mb-4">
              No content has been tagged with "{tagData.name}" yet.
            </p>
            <Button asChild>
              <Link to={`/worlds/${worldId}`}>Explore Content</Link>
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {tagData.tagged_content.map((content: any) => {
              const Icon = getContentIcon(content.content_type)
              return (
                <Link
                  key={`${content.content_type}-${content.object_id}`}
                  to={`/worlds/${worldId}/content/${content.content_type}/${content.object_id}`}
                  className="flex items-center space-x-4 p-4 rounded-lg hover:bg-gray-50 transition-colors border border-gray-100"
                >
                  <div className="p-2 bg-primary-100 rounded-lg">
                    <Icon className="h-5 w-5 text-primary-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{content.title}</h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {getContentTypeLabel(content.content_type)}
                      </span>
                      <span>by {content.author_name}</span>
                      <span>{new Date(content.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        )}

        {/* Content Count */}
        {tagData.tagged_content && tagData.tagged_content.length > 0 && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600 text-center">
              {tagData.tagged_content.length} item{tagData.tagged_content.length !== 1 ? 's' : ''} tagged with "{tagData.name}"
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default TagPage