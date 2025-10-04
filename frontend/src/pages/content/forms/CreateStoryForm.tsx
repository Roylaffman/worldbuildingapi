import React, { useState } from 'react'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Textarea from '@/components/ui/Textarea'
import type { CreateStoryData } from '@/types'

interface CreateStoryFormProps {
  onSubmit: (data: CreateStoryData) => void
  isLoading: boolean
  onCancel: () => void
}

const CreateStoryForm: React.FC<CreateStoryFormProps> = ({ onSubmit, isLoading, onCancel }) => {
  const [formData, setFormData] = useState<CreateStoryData>({
    title: '',
    content: '',
    genre: '',
    story_type: 'short_story',
    is_canonical: true,
    main_characters: [],
    tags: [],
  })
  const [tagInput, setTagInput] = useState('')
  const [characterInput, setCharacterInput] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    const checked = (e.target as HTMLInputElement).checked
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
    
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

  const handleAddCharacter = () => {
    const character = characterInput.trim()
    if (character && !formData.main_characters?.includes(character)) {
      setFormData(prev => ({
        ...prev,
        main_characters: [...(prev.main_characters || []), character]
      }))
      setCharacterInput('')
    }
  }

  const handleRemoveCharacter = (characterToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      main_characters: prev.main_characters?.filter(char => char !== characterToRemove) || []
    }))
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.title.trim()) {
      newErrors.title = 'Story title is required'
    } else if (formData.title.length < 3) {
      newErrors.title = 'Title must be at least 3 characters'
    }

    if (!formData.content.trim()) {
      newErrors.content = 'Story content is required'
    } else if (formData.content.length < 50) {
      newErrors.content = 'Story content must be at least 50 characters'
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
        label="Story Title"
        name="title"
        type="text"
        required
        value={formData.title}
        onChange={handleChange}
        error={errors.title}
        placeholder="Enter an engaging title for your story"
        helperText="A compelling title that captures the essence of your story"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="Genre"
          name="genre"
          type="text"
          value={formData.genre || ''}
          onChange={handleChange}
          placeholder="e.g., Fantasy, Sci-Fi, Mystery"
          helperText="What genre best describes this story?"
        />

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Story Type
          </label>
          <select
            name="story_type"
            value={formData.story_type}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="short_story">Short Story</option>
            <option value="novella">Novella</option>
            <option value="novel">Novel</option>
            <option value="epic">Epic</option>
            <option value="legend">Legend</option>
            <option value="myth">Myth</option>
            <option value="folklore">Folklore</option>
          </select>
          <p className="text-sm text-gray-500">
            Choose the type that best fits your story's length and scope
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        <input
          type="checkbox"
          id="is_canonical"
          name="is_canonical"
          checked={formData.is_canonical}
          onChange={handleChange}
          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
        />
        <label htmlFor="is_canonical" className="text-sm font-medium text-gray-700">
          This is canonical to the world
        </label>
        <p className="text-sm text-gray-500">
          (Official part of the world's lore vs. alternative/fan fiction)
        </p>
      </div>

      <Textarea
        label="Story Content"
        name="content"
        rows={15}
        required
        value={formData.content}
        onChange={handleChange}
        error={errors.content}
        placeholder="Write your story here. Tell us about the characters, plot, setting, and events that unfold in your world..."
        helperText="The full narrative of your story (minimum 50 characters)"
      />

      {/* Main Characters */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Main Characters
        </label>
        
        <div className="flex space-x-2">
          <Input
            value={characterInput}
            onChange={(e) => setCharacterInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCharacter())}
            placeholder="Character name (e.g., Aragorn, Hermione)"
            className="flex-1"
          />
          <Button
            type="button"
            variant="outline"
            onClick={handleAddCharacter}
            disabled={!characterInput.trim()}
          >
            Add Character
          </Button>
        </div>
        
        {formData.main_characters && formData.main_characters.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {formData.main_characters.map((character) => (
              <span
                key={character}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
              >
                {character}
                <button
                  type="button"
                  onClick={() => handleRemoveCharacter(character)}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
        
        <p className="text-sm text-gray-500">
          List the main characters that appear in this story
        </p>
      </div>

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
            placeholder="Add a tag (e.g., adventure, romance, war)"
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
      </div>

      {/* Character Count */}
      <div className="text-sm text-gray-500 text-right">
        Content: {formData.content.length} characters
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
          {isLoading ? 'Creating Story...' : 'Create Story'}
        </Button>
      </div>
    </form>
  )
}

export default CreateStoryForm