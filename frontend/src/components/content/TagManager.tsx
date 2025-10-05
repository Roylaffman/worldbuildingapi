import React, { useState } from 'react'
import { Tag, Plus, X } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { tagsAPI } from '@/lib/api'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

interface TagManagerProps {
  worldId: number
  existingTags?: Array<{ id: number; name: string }>
  onAddTag: (tagName: string) => void
  onRemoveTag?: (tagId: number) => void
  maxTags?: number
}

const TagManager: React.FC<TagManagerProps> = ({
  worldId,
  existingTags = [],
  onAddTag,
  onRemoveTag,
  maxTags = 10,
}) => {
  const [isAdding, setIsAdding] = useState(false)
  const [newTagName, setNewTagName] = useState('')
  const [suggestions, setSuggestions] = useState<string[]>([])

  // Fetch available tags for suggestions
  const { data: availableTags = [] } = useQuery({
    queryKey: ['world-tags', worldId],
    queryFn: () => tagsAPI.list(worldId),
  })

  const handleAddTag = () => {
    const tagName = newTagName.trim().toLowerCase()
    if (tagName && !existingTags.some(tag => tag.name.toLowerCase() === tagName)) {
      onAddTag(tagName)
      setNewTagName('')
      setIsAdding(false)
    }
  }

  const handleInputChange = (value: string) => {
    setNewTagName(value)
    
    // Generate suggestions
    if (value.length > 0) {
      const filtered = availableTags
        .filter(tag => 
          tag.name.toLowerCase().includes(value.toLowerCase()) &&
          !existingTags.some(existing => existing.name === tag.name)
        )
        .map(tag => tag.name)
        .slice(0, 5)
      setSuggestions(filtered)
    } else {
      setSuggestions([])
    }
  }

  const handleSuggestionClick = (tagName: string) => {
    onAddTag(tagName)
    setNewTagName('')
    setIsAdding(false)
    setSuggestions([])
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddTag()
    } else if (e.key === 'Escape') {
      setIsAdding(false)
      setNewTagName('')
      setSuggestions([])
    }
  }

  const canAddMore = existingTags.length < maxTags

  return (
    <div className="space-y-3">
      {/* Existing Tags */}
      {existingTags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {existingTags.map((tag) => (
            <span
              key={tag.id}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800"
            >
              <Tag className="h-3 w-3 mr-1" />
              {tag.name}
              {onRemoveTag && (
                <button
                  onClick={() => onRemoveTag(tag.id)}
                  className="ml-2 text-primary-600 hover:text-primary-800"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </span>
          ))}
        </div>
      )}

      {/* Add Tag Interface */}
      {canAddMore && (
        <div>
          {!isAdding ? (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsAdding(true)}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Tag
            </Button>
          ) : (
            <div className="space-y-2">
              <div className="flex space-x-2">
                <div className="flex-1 relative">
                  <Input
                    placeholder="Enter tag name..."
                    value={newTagName}
                    onChange={(e) => handleInputChange(e.target.value)}
                    onKeyDown={handleKeyPress}
                    autoFocus
                    className="text-sm"
                  />
                  
                  {/* Suggestions Dropdown */}
                  {suggestions.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg">
                      {suggestions.map((suggestion) => (
                        <button
                          key={suggestion}
                          onClick={() => handleSuggestionClick(suggestion)}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 focus:bg-gray-50 focus:outline-none"
                        >
                          <Tag className="h-3 w-3 mr-2 inline" />
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                
                <Button
                  size="sm"
                  onClick={handleAddTag}
                  disabled={!newTagName.trim()}
                >
                  Add
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setIsAdding(false)
                    setNewTagName('')
                    setSuggestions([])
                  }}
                >
                  Cancel
                </Button>
              </div>
              
              {/* Helper Text */}
              <p className="text-xs text-gray-500">
                Press Enter to add, Escape to cancel. {maxTags - existingTags.length} tags remaining.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Max Tags Reached */}
      {!canAddMore && (
        <p className="text-xs text-gray-500">
          Maximum of {maxTags} tags reached.
        </p>
      )}
    </div>
  )
}

export default TagManager