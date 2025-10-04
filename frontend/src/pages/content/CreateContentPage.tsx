import React from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { contentAPI, worldsAPI } from '@/lib/api'
import { useToast } from '@/components/ui/Toaster'
import Button from '@/components/ui/Button'
import { ArrowLeft, FileText, User, BookOpen, Scroll, Image as ImageIcon } from 'lucide-react'
import type { ContentType } from '@/types'

// Import individual form components
import CreatePageForm from './forms/CreatePageForm'
import CreateCharacterForm from './forms/CreateCharacterForm'
import CreateStoryForm from './forms/CreateStoryForm'
import CreateEssayForm from './forms/CreateEssayForm'

const CreateContentPage: React.FC = () => {
  const { worldId, contentType } = useParams<{ worldId: string; contentType: string }>()
  const navigate = useNavigate()
  const { addToast } = useToast()
  const queryClient = useQueryClient()

  // Fetch world data for context
  const { data: world } = useQuery({
    queryKey: ['world', worldId],
    queryFn: () => worldsAPI.get(parseInt(worldId!)),
    enabled: !!worldId,
  })

  // Create content mutation
  const createContentMutation = useMutation({
    mutationFn: (data: any) => {
      console.log('Creating content in world:', worldId, 'type:', contentType, 'data:', data)
      return contentAPI.create(parseInt(worldId!), contentType as ContentType, data)
    },
    onSuccess: (content) => {
      // Invalidate all relevant queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['world', worldId] })
      queryClient.invalidateQueries({ queryKey: ['worlds'] })
      queryClient.invalidateQueries({ queryKey: [`world-${contentType}s`, worldId] })
      queryClient.invalidateQueries({ queryKey: [`world-pages`, worldId] })
      queryClient.invalidateQueries({ queryKey: [`world-characters`, worldId] })
      queryClient.invalidateQueries({ queryKey: [`world-stories`, worldId] })
      queryClient.invalidateQueries({ queryKey: [`world-essays`, worldId] })
      
      addToast({
        type: 'success',
        title: `${contentType?.charAt(0).toUpperCase()}${contentType?.slice(1)} created!`,
        message: `"${content.title}" has been created successfully.`,
      })
      
      // Navigate back to world detail page
      navigate(`/worlds/${worldId}`)
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        title: `Failed to create ${contentType}`,
        message: error.response?.data?.message || error.message || 'Please try again.',
      })
    },
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

  const Icon = getContentIcon(contentType || '')
  const contentTitle = contentType?.charAt(0).toUpperCase() + contentType?.slice(1)

  const handleSubmit = (data: any) => {
    createContentMutation.mutate(data)
  }

  const renderForm = () => {
    const commonProps = {
      onSubmit: handleSubmit,
      isLoading: createContentMutation.isPending,
      onCancel: () => navigate(`/worlds/${worldId}`),
    }

    switch (contentType) {
      case 'page':
        return <CreatePageForm {...commonProps} />
      case 'character':
        return <CreateCharacterForm {...commonProps} />
      case 'story':
        return <CreateStoryForm {...commonProps} />
      case 'essay':
        return <CreateEssayForm {...commonProps} />
      case 'image':
        return (
          <div className="text-center py-8 text-gray-500">
            <ImageIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium mb-2">Image Upload Coming Soon!</p>
            <p className="text-sm">Image creation functionality will be available in a future update.</p>
            <Button
              variant="outline"
              onClick={() => navigate(`/worlds/${worldId}`)}
              className="mt-4"
            >
              Back to World
            </Button>
          </div>
        )
      default:
        return (
          <div className="text-center py-8 text-gray-500">
            <p>Content type "{contentType}" is not yet supported</p>
            <p className="text-sm mt-2">Please try creating a page, character, story, or essay.</p>
            <Button
              variant="outline"
              onClick={() => navigate(`/worlds/${worldId}`)}
              className="mt-4"
            >
              Back to World
            </Button>
          </div>
        )
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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

        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-100 rounded-lg">
            <Icon className="h-6 w-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Create {contentTitle}
            </h1>
            <p className="text-gray-600">
              Add a new {contentType} to {world?.title}
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {renderForm()}
      </div>

      {/* Tips */}
      {contentType !== 'image' && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-900 mb-2">
            Tips for creating great {contentType}s:
          </h3>
          <ul className="text-sm text-blue-800 space-y-1">
            {contentType === 'page' && (
              <>
                <li>• Use a clear, descriptive title</li>
                <li>• Include key information in the summary</li>
                <li>• Write detailed content to help collaborators understand</li>
                <li>• Add relevant tags to help with discovery</li>
              </>
            )}
            {contentType === 'character' && (
              <>
                <li>• Give your character a memorable full name</li>
                <li>• Define their species and occupation clearly</li>
                <li>• List personality traits that make them unique</li>
                <li>• Describe relationships with other characters</li>
              </>
            )}
            {contentType === 'story' && (
              <>
                <li>• Choose an engaging title</li>
                <li>• Specify the genre and story type</li>
                <li>• List the main characters involved</li>
                <li>• Write a compelling narrative</li>
              </>
            )}
            {contentType === 'essay' && (
              <>
                <li>• Write a clear, informative title</li>
                <li>• Include an abstract summarizing your main points</li>
                <li>• State your thesis clearly</li>
                <li>• Organize your content logically</li>
              </>
            )}
          </ul>
        </div>
      )}
    </div>
  )
}

export default CreateContentPage