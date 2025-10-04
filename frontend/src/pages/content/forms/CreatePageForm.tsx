import React, { useState } from 'react'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Textarea from '@/components/ui/Textarea'
import type { CreatePageData } from '@/types'

interface CreatePageFormProps {
  onSubmit: (data: CreatePageData) => void
  isLoading: boolean
  onCancel: () => void
}

const CreatePageForm: React.FC<CreatePageFormProps> = ({ onSubmit, isLoading, onCancel }) => {
  const [formData, setFormData] = useState<CreatePageData>({
    title: '',
    content: '',
    summary: '',
    tags: [],
  })
  const [tagInput, setTagInput] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const handleAddTag = () => {
    const tag = tagInput.trim().toLowerCase().replace(/\s+/g, '-')
    if (tag && !formData.tags?.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...(prev.tags || []), tag]
      }))
      setTagInput('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags?.filter(tag => tag !== tagToRemove) || []
    }))
  }

  const handleTagInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddTag()
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    } else if (formData.title.length < 3) {
      newErrors.title = 'Title must be at least 3 characters'
    } else if (formData.title.length > 200) {
      newErrors.title = 'Title must be less than 200 characters'
    }

    if (!formData.content.trim()) {
      newErrors.content = 'Content is required'
    } else if (formData.content.length < 10) {
      newErrors.content = 'Content must be at least 10 characters'
    } else if (formData.content.length > 10000) {
      newErrors.content = 'Content must be less than 10,000 characters'
    }

    if (formData.summary && formData.summary.length > 500) {
      newErrors.summary = 'Summary must be less than 500 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Input
        label="Page Title"
        name="title"
        type="text"
        required
        value={formData.title}
        onChange={handleChange}
        error={errors.title}
        placeholder="Enter a descriptive title for your page"
        helperText="A clear, concise title that describes what this page is about (3-200 characters)"
      />

      <Input
        label="Summary (Optional)"
        name="summary"
        type="text"
        value={formData.summary || ''}
        onChange={handleChange}
        error={errors.summary}
        placeholder="Brief summary of the page content"
        helperText="A short summary that appears in lists and search results (max 500 characters)"
      />

      <Textarea
        label="Content"
        name="content"
        rows={12}
        required
        value={formData.content}
        onChange={handleChange}
        error={errors.content}
        placeholder="Write your page content here. You can describe locations, concepts, history, or any other information relevant to your world..."
        helperText="The main content of your page. Be detailed and informative to help collaborators understand (10-10,000 characters)"
      />

      {/* Tags Section */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Tags (Optional)
        </label>
        
        {/* Tag Input */}
        <div className="flex space-x-2">
          <Input
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyPress={handleTagInputKeyPress}
            placeholder="Add a tag (e.g., magic, location, history)"
            className="flex-1"
          />
          <Button
            type="button"
            variant="outline"
            onClick={handleAddTag}
            disabled={!tagInput.trim()}
          >
            Add Tag
          </Button>
        </div>
        
        {/* Tag Display */}
        {formData.tags && formData.tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {formData.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="ml-2 text-primary-600 hover:text-primary-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
        
        <p className="text-sm text-gray-500">
          Tags help others discover your content. Use lowercase letters and hyphens (e.g., "magic-system", "ancient-history")
        </p>
      </div>

      {/* Character Count */}
      <div className="text-sm text-gray-500 text-right">
        Content: {formData.content.length}/10,000 characters
        {formData.summary && (
          <span className="ml-4">Summary: {formData.summary.length}/500 characters</span>
        )}
      </div>

      {/* Form Actions */}
      <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          isLoading={isLoading}
          disabled={isLoading}
        >
          {isLoading ? 'Creating Page...' : 'Create Page'}
        </Button>
      </div>
    </form>
  )
}

export default CreatePageForm