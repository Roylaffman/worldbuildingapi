import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { worldsAPI } from '@/lib/api'
import { useToast } from '@/components/ui/Toaster'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Textarea from '@/components/ui/Textarea'
import { ArrowLeft, Globe } from 'lucide-react'
import type { CreateWorldData } from '@/types'

const CreateWorldPage: React.FC = () => {
  const navigate = useNavigate()
  const { addToast } = useToast()
  const queryClient = useQueryClient()
  
  // Create world mutation
  const createWorldMutation = useMutation({
    mutationFn: (data: CreateWorldData) => worldsAPI.create(data),
    onSuccess: (world) => {
      // Invalidate all world-related queries to refresh the list
      queryClient.invalidateQueries({ queryKey: ['worlds'] })
      queryClient.invalidateQueries({ queryKey: ['user-worlds'] })
      
      addToast({
        type: 'success',
        title: 'World created!',
        message: `${world.title} has been created successfully.`,
      })
      
      // Navigate to the new world
      navigate(`/worlds/${world.id}`)
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        title: 'Failed to create world',
        message: error.response?.data?.message || error.message || 'Please try again.',
      })
    },
  })
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    is_public: true,
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target
    const checked = (e.target as HTMLInputElement).checked

    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.title.trim()) {
      newErrors.title = 'World title is required'
    } else if (formData.title.length < 3) {
      newErrors.title = 'Title must be at least 3 characters'
    } else if (formData.title.length > 200) {
      newErrors.title = 'Title must be less than 200 characters'
    }

    if (!formData.description.trim()) {
      newErrors.description = 'World description is required'
    } else if (formData.description.length < 10) {
      newErrors.description = 'Description must be at least 10 characters'
    } else if (formData.description.length > 1000) {
      newErrors.description = 'Description must be less than 1000 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    createWorldMutation.mutate(formData)
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <Button
          variant="ghost"
          onClick={() => navigate('/worlds')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Worlds
        </Button>

        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-primary-100 rounded-lg">
            <Globe className="h-6 w-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create New World</h1>
            <p className="text-gray-600">
              Start building your collaborative worldbuilding project
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            label="World Title"
            name="title"
            type="text"
            required
            value={formData.title}
            onChange={handleChange}
            error={errors.title}
            placeholder="Enter your world's name"
            helperText="Choose a memorable name for your world (3-200 characters)"
          />

          <Textarea
            label="Description"
            name="description"
            rows={4}
            required
            value={formData.description}
            onChange={handleChange}
            error={errors.description}
            placeholder="Describe your world's setting, themes, and what makes it unique..."
            helperText="Provide an overview that will help collaborators understand your world (10-1000 characters)"
          />

          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">
              Visibility
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="is_public"
                  value="true"
                  checked={formData.is_public === true}
                  onChange={(e) => setFormData(prev => ({ ...prev, is_public: true }))}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                />
                <span className="ml-3 text-sm text-gray-700">
                  <span className="font-medium">Public</span> - Anyone can view and contribute to this world
                </span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="is_public"
                  value="false"
                  checked={formData.is_public === false}
                  onChange={(e) => setFormData(prev => ({ ...prev, is_public: false }))}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                />
                <span className="ml-3 text-sm text-gray-700">
                  <span className="font-medium">Private</span> - Only you and invited collaborators can access
                </span>
              </label>
            </div>
          </div>

          <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/worlds')}
              disabled={createWorldMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              isLoading={createWorldMutation.isPending}
              disabled={createWorldMutation.isPending}
            >
              {createWorldMutation.isPending ? 'Creating World...' : 'Create World'}
            </Button>
          </div>
        </form>
      </div>

      {/* Tips */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-2">
          Tips for creating a great world:
        </h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Choose a descriptive title that captures your world's essence</li>
          <li>• Include key themes, settings, or unique elements in the description</li>
          <li>• Consider starting with public visibility to attract collaborators</li>
          <li>• You can always change these settings later</li>
        </ul>
      </div>
    </div>
  )
}

export default CreateWorldPage