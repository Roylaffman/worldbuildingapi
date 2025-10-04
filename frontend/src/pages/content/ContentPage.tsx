import React from 'react'
import { useParams } from 'react-router-dom'

const ContentPage: React.FC = () => {
  const { worldId, contentType, contentId } = useParams()

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Content Detail Page
        </h1>
        <div className="space-y-2 text-gray-600">
          <p>World ID: {worldId}</p>
          <p>Content Type: {contentType}</p>
          <p>Content ID: {contentId}</p>
        </div>
        <div className="mt-8 text-center py-8 text-gray-500">
          <p>Content detail view will be implemented here</p>
          <p className="text-sm mt-2">This feature is coming soon!</p>
        </div>
      </div>
    </div>
  )
}

export default ContentPage