import React, { useState } from 'react'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Textarea from '@/components/ui/Textarea'
import type { CreateEssayData } from '@/types'

interface CreateEssayFormProps {
  onSubmit: (data: CreateEssayData) => void
  isLoading: boolean
  onCancel: () => void
}

const CreateEssayForm: React.FC<CreateEssayFormProps> = ({ onSubmit, isLoading, onCancel }) => {
  const [formData, setFormData] = useState<CreateEssayData>({
    title: '',
    content: '',
    abstract: '',
    thesis_statement: '',
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

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.title.trim()) {
      newErrors.title = 'Essay title is required'
    } else if (formData.title.length < 5) {
      newErrors.title = 'Title must be at least 5 characters'
    }

    if (!formData.content.trim()) {
      newErrors.content = 'Essay content is required'
    } else if (formData.content.length < 100) {
      newErrors.content = 'Essay content must be at least 100 characters'
    }

    if (formData.abstract && formData.abstract.length > 500) {
      newErrors.abstract = 'Abstract must be less than 500 characters'
    }

    if (formData.thesis_statement && formData.thesis_statement.length > 300) {
      newErrors.thesis_statement = 'Thesis statement must be less than 300 characters'
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
        label="Essay Title"
        name="title"
        type="text"
        required
        value={formData.title}
        onChange={handleChange}
        error={errors.title}
        placeholder="Enter a clear, informative title for your essay"
        helperText="A descriptive title that summarizes your essay's main topic"
      />

      <Textarea
        label="Abstract (Optional)"
        name="abstract"
        rows={4}
        value={formData.abstract || ''}
        onChange={handleChange}
        error={errors.abstract}
        placeholder="Write a brief summary of your essay's main points and conclusions..."
        helperText="A concise overview of your essay (max 500 characters)"
      />

      <Textarea
        label="Thesis Statement (Optional)"
        name="thesis_statement"
        rows={3}
        value={formData.thesis_statement || ''}
        onChange={handleChange}
        error={errors.thesis_statement}
        placeholder="State your main argument or central claim..."
        helperText="The central argument or point you're making in this essay (max 300 characters)"
      />

      <Textarea
        label="Essay Content"
        name="content"
        rows={20}
        required
        value={formData.content}
        onChange={handleChange}
        error={errors.content}
        placeholder="Write your essay here. Develop your arguments, provide evidence, analyze concepts, and draw conclusions about your world..."
        helperText="The full content of your essay with detailed analysis and arguments (minimum 100 characters)"
      />

      {/* Tags Section */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Tags (Optional)
        </label>
        
        <div className="flex space-x-2">
          <Input
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
            placeholder="Add a tag (e.g., analysis, theory, history)"
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
          Tags help categorize your essay by topic, theme, or analytical approach
        </p>
      </div>

      {/* Character Count */}
      <div className="text-sm text-gray-500 text-right space-y-1">
        <div>Content: {formData.content.length} characters</div>
        {formData.abstract && (
          <div>Abstract: {formData.abstract.length}/500 characters</div>
        )}
        {formData.thesis_statement && (
          <div>Thesis: {formData.thesis_statement.length}/300 characters</div>
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
          {isLoading ? 'Creating Essay...' : 'Create Essay'}
        </Button>
      </div>
    </form>
  )
}

export default CreateEssayForm