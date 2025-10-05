import React, { useState } from 'react'
import { Link as LinkIcon, Plus, X, Search } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { contentAPI } from '@/lib/api'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import type { ContentType, Content } from '@/types'

interface ContentLinkerProps {
  worldId: number
  currentContentId: number
  currentContentType: ContentType
  existingLinks?: Array<{
    id: number
    title: string
    type: ContentType
    author: { username: string; first_name?: string }
  }>
  onAddLink: (contentType: ContentType, contentId: number) => void
  onRemoveLink?: (linkId: number) => void
}

const ContentLinker: React.FC<ContentLinkerProps> = ({
  worldId,
  currentContentId,
  currentContentType,
  existingLinks = [],
  onAddLink,
  onRemoveLink,
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedContentType, setSelectedContentType] = useState<ContentType>('page')

  // Fetch available content to link
  const { data: availableContent = [], isLoading } = useQuery({
    queryKey: ['linkable-content', worldId, selectedContentType, searchTerm],
    queryFn: () => contentAPI.list(worldId, selectedContentType, { 
      search: searchTerm || undefined,
      ordering: '-created_at' 
    }),
    enabled: isOpen,
  })

  const contentTypes: { value: ContentType; label: string }[] = [
    { value: 'page', label: 'Pages' },
    { value: 'character', label: 'Characters' },
    { value: 'story', label: 'Stories' },
    { value: 'essay', label: 'Essays' },
    { value: 'image', label: 'Images' },
  ]

  const getContentIcon = (type: ContentType) => {
    switch (type) {
      case 'character': return '👤'
      case 'story': return '📖'
      case 'essay': return '📝'
      case 'image': return '🖼️'
      default: return '📄'
    }
  }

  const handleAddLink = (content: Content) => {
    onAddLink(selectedContentType, content.id)
    setIsOpen(false)
    setSearchTerm('')
  }

  const filteredContent = availableContent.filter(
    content => content.id !== currentContentId || selectedContentType !== currentContentType
  )

  const isAlreadyLinked = (contentId: number, contentType: ContentType) => {
    return existingLinks.some(link => link.id === contentId && link.type === contentType)
  }

  return (
    <div className="space-y-4">
      {/* Existing Links */}
      {existingLinks.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Linked Content</h4>
          <div className="space-y-2">
            {existingLinks.map((link) => (
              <div
                key={`${link.type}-${link.id}`}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-lg">{getContentIcon(link.type)}</span>
                  <div>
                    <p className="font-medium text-gray-900">{link.title}</p>
                    <p className="text-sm text-gray-600">
                      {link.type} • by {link.author.first_name || link.author.username}
                    </p>
                  </div>
                </div>
                {onRemoveLink && (
                  <button
                    onClick={() => onRemoveLink(link.id)}
                    className="text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add Link Button */}
      {!isOpen && (
        <Button
          variant="outline"
          onClick={() => setIsOpen(true)}
          className="w-full"
        >
          <Plus className="h-4 w-4 mr-2" />
          Link to Other Content
        </Button>
      )}

      {/* Link Selection Interface */}
      {isOpen && (
        <div className="border border-gray-200 rounded-lg p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-gray-900">Link to Content</h4>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Content Type Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content Type
            </label>
            <select
              value={selectedContentType}
              onChange={(e) => setSelectedContentType(e.target.value as ContentType)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              {contentTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder={`Search ${contentTypes.find(t => t.value === selectedContentType)?.label.toLowerCase()}...`}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Available Content */}
          <div className="max-h-60 overflow-y-auto space-y-2">
            {isLoading ? (
              <div className="text-center py-4 text-gray-500">
                Loading content...
              </div>
            ) : filteredContent.length === 0 ? (
              <div className="text-center py-4 text-gray-500">
                No {contentTypes.find(t => t.value === selectedContentType)?.label.toLowerCase()} found
              </div>
            ) : (
              filteredContent.map((content) => {
                const alreadyLinked = isAlreadyLinked(content.id, selectedContentType)
                return (
                  <div
                    key={content.id}
                    className={`flex items-center justify-between p-3 rounded-lg border ${
                      alreadyLinked
                        ? 'bg-gray-100 border-gray-200'
                        : 'bg-white border-gray-200 hover:border-primary-300 cursor-pointer'
                    }`}
                    onClick={() => !alreadyLinked && handleAddLink(content)}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-lg">{getContentIcon(selectedContentType)}</span>
                      <div>
                        <p className="font-medium text-gray-900">{content.title}</p>
                        <p className="text-sm text-gray-600">
                          by {content.author.first_name || content.author.username}
                        </p>
                      </div>
                    </div>
                    {alreadyLinked ? (
                      <span className="text-sm text-gray-500">Already linked</span>
                    ) : (
                      <LinkIcon className="h-4 w-4 text-gray-400" />
                    )}
                  </div>
                )
              })
            )}
          </div>

          {/* Cancel Button */}
          <Button
            variant="outline"
            onClick={() => setIsOpen(false)}
            className="w-full"
          >
            Cancel
          </Button>
        </div>
      )}
    </div>
  )
}

export default ContentLinker