import React, { useState } from 'react'
import { Upload, X, Image as ImageIcon } from 'lucide-react'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Textarea from '@/components/ui/Textarea'

interface CreateImageFormProps {
  onSubmit: (data: FormData) => void
  isLoading: boolean
  onCancel: () => void
}

const CreateImageForm: React.FC<CreateImageFormProps> = ({
  onSubmit,
  isLoading,
  onCancel,
}) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    alt_text: '',
    tags: '',
  })
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setErrors(prev => ({ ...prev, image_file: 'Please select a valid image file' }))
        return
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setErrors(prev => ({ ...prev, image_file: 'Image file must be less than 10MB' }))
        return
      }

      setSelectedFile(file)
      setErrors(prev => ({ ...prev, image_file: '' }))

      // Create preview URL
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
    }
  }

  const removeFile = () => {
    setSelectedFile(null)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    }

    if (!formData.content.trim()) {
      newErrors.content = 'Description is required'
    }

    if (!formData.alt_text.trim()) {
      newErrors.alt_text = 'Alt text is required for accessibility'
    }

    if (!selectedFile) {
      newErrors.image_file = 'Please select an image file'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    // Create FormData for file upload
    const submitData = new FormData()
    submitData.append('title', formData.title.trim())
    submitData.append('content', formData.content.trim())
    submitData.append('alt_text', formData.alt_text.trim())
    
    if (selectedFile) {
      submitData.append('image_file', selectedFile)
    }

    // Handle tags
    if (formData.tags.trim()) {
      const tagList = formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      tagList.forEach(tag => {
        submitData.append('tags', tag)
      })
    }

    onSubmit(submitData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Title */}
      <Input
        label="Title"
        name="title"
        value={formData.title}
        onChange={handleInputChange}
        error={errors.title}
        placeholder="e.g., Character Design Sketches, Plot Storyboard, World Map"
        required
      />

      {/* Image Upload */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Image File *
        </label>
        
        {!selectedFile ? (
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
              id="image-upload"
            />
            <label
              htmlFor="image-upload"
              className="cursor-pointer flex flex-col items-center space-y-2"
            >
              <Upload className="h-8 w-8 text-gray-400" />
              <div className="text-sm text-gray-600">
                <span className="font-medium text-primary-600 hover:text-primary-500">
                  Click to upload
                </span>{' '}
                or drag and drop
              </div>
              <div className="text-xs text-gray-500">
                PNG, JPG, GIF up to 10MB
              </div>
            </label>
          </div>
        ) : (
          <div className="relative">
            <div className="border border-gray-300 rounded-lg p-4">
              <div className="flex items-start space-x-4">
                {previewUrl && (
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="w-20 h-20 object-cover rounded-lg"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {selectedFile.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <button
                  type="button"
                  onClick={removeFile}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        )}
        
        {errors.image_file && (
          <p className="text-sm text-red-600">{errors.image_file}</p>
        )}
      </div>

      {/* Alt Text */}
      <Input
        label="Alt Text"
        name="alt_text"
        value={formData.alt_text}
        onChange={handleInputChange}
        error={errors.alt_text}
        placeholder="Describe the image for accessibility (e.g., A detailed sketch of the main character in medieval armor)"
        helperText="This helps screen readers and improves accessibility"
        required
      />

      {/* Description */}
      <Textarea
        label="Description"
        name="content"
        value={formData.content}
        onChange={handleInputChange}
        error={errors.content}
        placeholder="Describe this image and its role in your world. What does it show? How does it relate to your story or characters?"
        rows={4}
        required
      />

      {/* Tags */}
      <Input
        label="Tags (Optional)"
        name="tags"
        value={formData.tags}
        onChange={handleInputChange}
        placeholder="storyboard, character-design, concept-art, map (separate with commas)"
        helperText="Add tags to help organize and find your images"
      />

      {/* Form Actions */}
      <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
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
          {isLoading ? 'Uploading...' : 'Upload Image'}
        </Button>
      </div>
    </form>
  )
}

export default CreateImageForm