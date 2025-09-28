import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { BookOpen, Users, Link as LinkIcon, Clock, Shield, Zap } from 'lucide-react'
import Button from '@/components/ui/Button'

const HomePage: React.FC = () => {
  const { isAuthenticated } = useAuth()

  const features = [
    {
      icon: Shield,
      title: 'Immutable Content',
      description: 'Content is preserved forever with proper attribution, ensuring creative integrity and collaboration history.',
    },
    {
      icon: Users,
      title: 'Collaborative Attribution',
      description: 'Comprehensive tracking and display of all contributions, giving credit where credit is due.',
    },
    {
      icon: LinkIcon,
      title: 'Rich Relationships',
      description: 'Bidirectional linking and flexible tagging create interconnected worlds of content.',
    },
    {
      icon: Clock,
      title: 'Chronological Timeline',
      description: 'Explore content creation over time with powerful filtering and search capabilities.',
    },
    {
      icon: Zap,
      title: 'RESTful API',
      description: 'Complete API with comprehensive documentation for building custom tools and integrations.',
    },
    {
      icon: BookOpen,
      title: 'Multiple Content Types',
      description: 'Pages, essays, characters, stories, and images - all with specialized fields and validation.',
    },
  ]

  return (
    <div className="bg-white">
      {/* Hero section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Collaborative
              <span className="text-primary-600 block">Worldbuilding</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
              Create immutable, interconnected worlds with comprehensive attribution. 
              Build stories, characters, and lore collaboratively while preserving every contribution.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {isAuthenticated ? (
                <>
                  <Button size="lg" asChild>
                    <Link to="/worlds">View My Worlds</Link>
                  </Button>
                  <Button variant="outline" size="lg" asChild>
                    <Link to="/worlds/create">Create New World</Link>
                  </Button>
                </>
              ) : (
                <>
                  <Button size="lg" asChild>
                    <Link to="/register">Get Started</Link>
                  </Button>
                  <Button variant="outline" size="lg" asChild>
                    <Link to="/login">Sign In</Link>
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
        
        {/* Background decoration */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-40 -right-32 w-96 h-96 bg-primary-100 rounded-full opacity-20 blur-3xl" />
          <div className="absolute -bottom-40 -left-32 w-96 h-96 bg-secondary-100 rounded-full opacity-20 blur-3xl" />
        </div>
      </div>

      {/* Features section */}
      <div className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Built for Collaborative Storytelling
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Every feature is designed to foster collaboration while maintaining content integrity and proper attribution.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                <div className="flex items-center mb-4">
                  <div className="p-2 bg-primary-100 rounded-lg">
                    <feature.icon className="h-6 w-6 text-primary-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 ml-3">
                    {feature.title}
                  </h3>
                </div>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* How it works section */}
      <div className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Simple steps to start building collaborative worlds with proper attribution and content relationships.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary-600">1</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Create a World</h3>
              <p className="text-gray-600">
                Start by creating a world - your collaborative space for building interconnected content.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary-600">2</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Add Content</h3>
              <p className="text-gray-600">
                Create pages, characters, stories, essays, and images. Each piece is immutable and properly attributed.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary-600">3</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Connect & Collaborate</h3>
              <p className="text-gray-600">
                Link content together, add tags, and collaborate with others while maintaining full attribution history.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA section */}
      {!isAuthenticated && (
        <div className="bg-primary-600">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-white mb-4">
                Ready to Start Building?
              </h2>
              <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
                Join the community of collaborative worldbuilders and start creating immutable, interconnected content today.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button variant="secondary" size="lg" asChild>
                  <Link to="/register">Create Account</Link>
                </Button>
                <Button variant="outline" size="lg" className="border-white text-white hover:bg-white hover:text-primary-600" asChild>
                  <Link to="/docs/api_documentation.md">View Documentation</Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default HomePage