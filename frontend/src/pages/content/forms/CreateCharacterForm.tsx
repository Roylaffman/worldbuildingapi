import React, { useState } from 'react'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Textarea from '@/components/ui/Textarea'
import type { CreateCharacterData } from '@/types'

interface CreateCharacterFormProps {
  onSubmit: (data: CreateCharacterData) => void
  isLoading: boolean
  onCancel: () => void
}

const CreateCharacterForm: React.FC<CreateCharacterFormProps> = ({ onSubmit, isLoading, onCancel }) => {
  const [formData, setFormData] = useState<CreateCharacterData>({
    title: '',
    content: '',
    full_name: '',
    species: '',
    occupation: '',
    personality_traits: [],
    relationships: {},
    tags: [],
  })
  const [tagInput, setTagInput] = useState('')
  const [traitInput, setTraitInput] = useState('')
  const [relationshipKey, setRelationshipKey] = useState('')
  const [relationshipValue, setRelationshipValue] = useState('')
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

  const handleAddTrait = () => {
    const trait = traitInput.trim()
    if (trait && !formData.personality_traits?.includes(trait)) {
      setFormData(prev => ({
        ...prev,
        personality_traits: [...(prev.personality_traits || []), trait]
      }))
      setTraitInput('')
    }
  }

  const handleRemoveTrait = (traitToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      personality_traits: prev.personality_traits?.filter(trait => trait !== traitToRemove) || []
    }))
  }

  const handleAddRelationship = () => {
    const key = relationshipKey.trim()
    const value = relationshipValue.trim()
    if (key && value) {
      setFormData(prev => ({
        ...prev,
        relationships: {
          ...prev.relationships,
          [key]: value
        }
      }))
      setRelationshipKey('')
      setRelationshipValue('')
    }
  }

  const handleRemoveRelationship = (keyToRemove: string) => {
    setFormData(prev => {
      const newRelationships = { ...prev.relationships }
      delete newRelationships[keyToRemove]
      return {
        ...prev,
        relationships: newRelationships
      }
    })
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.title.trim()) {
      newErrors.title = 'Character name is required'
    } else if (formData.title.length < 2) {
      newErrors.title = 'Character name must be at least 2 characters'
    }

    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required'
    }

    if (!formData.content.trim()) {
      newErrors.content = 'Character description is required'
    } else if (formData.content.length < 10) {
      newErrors.content = 'Description must be at least 10 characters'
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="Character Name"
          name="title"
          type="text"
          required
          value={formData.title}
          onChange={handleChange}
          error={errors.title}
          placeholder="e.g., Gandalf, Hermione"
          helperText="The name this character is commonly known by"
        />

        <Input
          label="Full Name"
          name="full_name"
          type="text"
          required
          value={formData.full_name}
          onChange={handleChange}
          error={errors.full_name}
          placeholder="e.g., Gandalf the Grey, Hermione Granger"
          helperText="The character's complete, formal name"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="Species"
          name="species"
          type="text"
          value={formData.species || ''}
          onChange={handleChange}
          placeholder="e.g., Human, Elf, Dragon"
          helperText="What species or race is this character?"
        />

        <Input
          label="Occupation"
          name="occupation"
          type="text"
          value={formData.occupation || ''}
          onChange={handleChange}
          placeholder="e.g., Wizard, Student, Warrior"
          helperText="What does this character do for a living?"
        />
      </div>

      <Textarea
        label="Character Description"
        name="content"
        rows={8}
        required
        value={formData.content}
        onChange={handleChange}
        error={errors.content}
        placeholder="Describe this character's appearance, background, motivations, and role in your world..."
        helperText="A detailed description of the character (minimum 10 characters)"
      />

      {/* Personality Traits */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Personality Traits
        </label>
        
        <div className="flex space-x-2">
          <Input
            value={traitInput}
            onChange={(e) => setTraitInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTrait())}
            placeholder="e.g., brave, curious, stubborn"
            className="flex-1"
          />
          <Button
            type="button"
            variant="outline"
            onClick={handleAddTrait}
            disabled={!traitInput.trim()}
          >
            Add Trait
          </Button>
        </div>
        
        {formData.personality_traits && formData.personality_traits.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {formData.personality_traits.map((trait) => (
              <span
                key={trait}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800"
              >
                {trait}
                <button
                  type="button"
                  onClick={() => handleRemoveTrait(trait)}
                  className="ml-2 text-green-600 hover:text-green-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Relationships */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Relationships
        </label>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
          <Input
            value={relationshipKey}
            onChange={(e) => setRelationshipKey(e.target.value)}
            placeholder="Relationship type (e.g., friend, enemy)"
          />
          <Input
            value={relationshipValue}
            onChange={(e) => setRelationshipValue(e.target.value)}
            placeholder="Character name"
          />
          <Button
            type="button"
            variant="outline"
            onClick={handleAddRelationship}
            disabled={!relationshipKey.trim() || !relationshipValue.trim()}
          >
            Add Relationship
          </Button>
        </div>
        
        {formData.relationships && Object.keys(formData.relationships).length > 0 && (
          <div className="space-y-2">
            {Object.entries(formData.relationships).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded">
                <span className="text-sm">
                  <span className="font-medium capitalize">{key}:</span> {value}
                </span>
                <button
                  type="button"
                  onClick={() => handleRemoveRelationship(key)}
                  className="text-red-600 hover:text-red-800"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
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
            placeholder="Add a tag (e.g., protagonist, villain, npc)"
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
          {isLoading ? 'Creating Character...' : 'Create Character'}
        </Button>
      </div>
    </form>
  )
}

export default CreateCharacterForm