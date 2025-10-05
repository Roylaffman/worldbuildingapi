import React, { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Calendar, User, Tag, Link as LinkIcon, FileText, BookOpen, Scroll, Image as ImageIcon } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { contentAPI, worldsAPI } from '@/lib/api'
import { useToast } from '@/components/ui/Toaster'
import Button from '@/components/ui/Button'
import TagManager from '@/components/content/TagManager'
import ContentLinker from '@/components/content/ContentLinker'
import type { ContentType } from '@/types'

const ContentPage: React.FC = () => {
  const { worldId, contentType, contentId } = useParams<{ 
    worldId: string
    contentType: string
    contentId: string 
  }>()
  const { addToast } = useToast()
  const queryClient = useQueryClient()
  const [isManagingTags, setIsManagingTags] = useState(false)
  const [isManagingLinks, setIsManagingLinks] = useState(false)

  // Fetch world data
  const { data: world } = useQuery({
    queryKey: ['world', worldId],
    queryFn: () => worldsAPI.get(parseInt(worldId!)),
    enabled: !!worldId,
  })

  // Fetch content data
  const { data: content, isLoading, error } = useQuery({
    queryKey: ['content', worldId, contentType, contentId],
    queryFn: () => contentAPI.get(
      parseInt(worldId!), 
      contentType as ContentType, 
      parseInt(contentId!)
    ),
    enabled: !!worldId && !!contentType && !!contentId,
  })

  // Add tag mutation
  const addTagMutation = useMutation({
    mutationFn: (tagName: string) => 
      contentAPI.addTags(
        parseInt(worldId!), 
        contentType as ContentType, 
        parseInt(contentId!), 
        [tagName]
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content', worldId, contentType, contentId] })
      addToast({
        type: 'success',
        title: 'Tag added',
        message: 'Tag has been added to this content.',
      })
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        title: 'Failed to add tag',
        message: error.message || 'Could not add tag. Please try again.',
      })
    },
  })

  // Add link mutation
  const addLinkMutation = useMutation({
    mutationFn: ({ targetContentType, targetContentId }: { targetContentType: ContentType, targetContentId: number }) =>
      contentAPI.addLinks(
        parseInt(worldId!),
        contentType as ContentType,
        parseInt(contentId!),
        [{ content_type: targetContentType, content_id: targetContentId }]
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content', worldId, contentType, contentId] })
      addToast({
        type: 'success',
        title: 'Content linked',
        message: 'Content has been linked successfully.',
      })
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        title: 'Failed to link content',
        message: error.message || 'Could not link content. Please try again.',
      })
    },
  })

  const handleAddTag = (tagName: string) => {
    addTagMutation.mutate(tagName)
  }

  const handleAddLink = (targetContentType: ContentType, targetContentId: number) => {
    addLinkMutation.mutate({ targetContentType, targetContentId })
  }

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
          <span className="ml-2 text-gray-600">Loading content...</span>
        </div>
      </div>
    )
  }

  if (error || !content) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Content not found</h2>
          <p className="text-gray-600 mb-4">The content you're looking for doesn't exist or you don't have access to it.</p>
          <Button asChild>
            <Link to={`/worlds/${worldId}`}>Back to World</Link>
          </Button>
        </div>
      </div>
    )
  }

  const Icon = getContentIcon(contentType!)

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

      {/* Content Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-primary-100 rounded-lg">
            <Icon className="h-6 w-6 text-primary-600" />
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                {getContentTypeLabel(contentType!)}
              </span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              {content.title}
            </h1>
            <div className="flex items-center space-x-6 text-sm text-gray-500">
              <div className="flex items-center space-x-1">
                <User className="h-4 w-4" />
                <span>by {content.author.first_name || content.author.username}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Calendar className="h-4 w-4" />
                <span>{new Date(content.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content Body */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="prose max-w-none">
          <div className="whitespace-pre-wrap text-gray-900 leading-relaxed">
            {content.content}
          </div>
        </div>
      </div>

      {/* Character-specific fields */}
      {contentType === 'character' && content.full_name && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Character Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <p className="text-gray-900">{content.full_name}</p>
            </div>
            {content.species && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Species</label>
                <p className="text-gray-900">{content.species}</p>
              </div>
            )}
            {content.occupation && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Occupation</label>
                <p className="text-gray-900">{content.occupation}</p>
              </div>
            )}
          </div>
          {content.personality_traits && content.personality_traits.length > 0 && (
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Personality Traits</label>
              <div className="flex flex-wrap gap-2">
                {content.personality_traits.map((trait, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    {trait}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Essay-specific fields */}
      {contentType === 'essay' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Essay Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {content.abstract && (
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Abstract</label>
                <p className="text-gray-900">{content.abstract}</p>
              </div>
            )}
            {content.topic && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Topic</label>
                <p className="text-gray-900">{content.topic}</p>
              </div>
            )}
            {content.word_count && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Word Count</label>
                <p className="text-gray-900">{content.word_count.toLocaleString()} words</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Story-specific fields */}
      {contentType === 'story' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Story Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {content.genre && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Genre</label>
                <p className="text-gray-900">{content.genre}</p>
              </div>
            )}
            {content.story_type && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Story Type</label>
                <p className="text-gray-900">{content.story_type.replace('_', ' ')}</p>
              </div>
            )}
            {content.word_count && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Word Count</label>
                <p className="text-gray-900">{content.word_count.toLocaleString()} words</p>
              </div>
            )}
            {content.is_canonical !== undefined && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Canonical</label>
                <p className="text-gray-900">{content.is_canonical ? 'Yes' : 'No'}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Image-specific fields */}
      {contentType === 'image' && (content as any).image_url && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Image</h2>
          <div className="space-y-4">
            <img
              src={(content as any).image_url}
              alt={(content as any).alt_text || content.title}
              className="w-full max-w-2xl mx-auto rounded-lg shadow-sm"
            />
            {(content as any).alt_text && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Alt Text</label>
                <p className="text-gray-900">{(content as any).alt_text}</p>
              </div>
            )}
            {(content as any).dimensions && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Dimensions</label>
                <p className="text-gray-900">{(content as any).dimensions}</p>
              </div>
            )}
            {(content as any).file_size && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">File Size</label>
                <p className="text-gray-900">{((content as any).file_size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tags */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Tag className="h-5 w-5 mr-2" />
            Tags
          </h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsManagingTags(!isManagingTags)}
          >
            {isManagingTags ? 'Done' : 'Manage Tags'}
          </Button>
        </div>
        
        {isManagingTags ? (
          <TagManager
            worldId={parseInt(worldId!)}
            existingTags={content.tags || []}
            onAddTag={handleAddTag}
            maxTags={10}
          />
        ) : (
          <div>
            {content.tags && content.tags.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {content.tags.map((tag) => (
                  <Link
                    key={tag.id}
                    to={`/worlds/${worldId}/tags/${tag.name}`}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800 hover:bg-gray-200 transition-colors"
                  >
                    {tag.name}
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No tags yet. Click "Manage Tags" to add some.</p>
            )}
          </div>
        )}
      </div>

      {/* Linked Content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <LinkIcon className="h-5 w-5 mr-2" />
            Linked Content
          </h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsManagingLinks(!isManagingLinks)}
          >
            {isManagingLinks ? 'Done' : 'Manage Links'}
          </Button>
        </div>
        
        {isManagingLinks ? (
          <ContentLinker
            worldId={parseInt(worldId!)}
            currentContentId={parseInt(contentId!)}
            currentContentType={contentType as ContentType}
            existingLinks={content.linked_content || []}
            onAddLink={handleAddLink}
          />
        ) : (
          <div>
            {content.linked_content && content.linked_content.length > 0 ? (
              <div className="space-y-3">
                {content.linked_content.map((linkedItem) => {
                  const LinkedIcon = getContentIcon(linkedItem.type)
                  return (
                    <Link
                      key={linkedItem.id}
                      to={`/worlds/${worldId}/content/${linkedItem.type}/${linkedItem.id}`}
                      className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="p-2 bg-primary-100 rounded-lg">
                        <LinkedIcon className="h-4 w-4 text-primary-600" />
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900">{linkedItem.title}</h3>
                        <p className="text-sm text-gray-600">
                          {getContentTypeLabel(linkedItem.type)} • by {linkedItem.author.first_name || linkedItem.author.username}
                        </p>
                      </div>
                    </Link>
                  )
                })}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No linked content yet. Click "Manage Links" to connect related content.</p>
            )}
          </div>
        )}
      </div>

      {/* Attribution */}
      {content.attribution && (
        <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
          <p className="font-medium mb-1">Attribution</p>
          <p>{content.attribution}</p>
        </div>
      )}
    </div>
  )
}

export default ContentPage