import React from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, Github, Heart } from 'lucide-react'

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and description */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <BookOpen className="h-6 w-6 text-primary-600" />
              <span className="text-lg font-bold text-gray-900">
                Collaborative Worldbuilding
              </span>
            </div>
            <p className="text-gray-600 text-sm leading-relaxed">
              A platform for collaborative storytelling and worldbuilding with immutable content, 
              comprehensive attribution, and rich content relationships.
            </p>
            <div className="flex items-center space-x-4 mt-4">
              <a
                href="https://github.com/yourusername/collaborative-worldbuilding"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Github className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Quick links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Platform</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/worlds" className="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                  Browse Worlds
                </Link>
              </li>
              <li>
                <Link to="/worlds/create" className="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                  Create World
                </Link>
              </li>
              <li>
                <a href="/docs/api_documentation.md" className="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                  API Documentation
                </a>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Support</h3>
            <ul className="space-y-2">
              <li>
                <a href="/docs/README.md" className="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                  Documentation
                </a>
              </li>
              <li>
                <a href="https://github.com/yourusername/collaborative-worldbuilding/issues" className="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                  Report Issues
                </a>
              </li>
              <li>
                <a href="https://github.com/yourusername/collaborative-worldbuilding/discussions" className="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                  Community
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom section */}
        <div className="mt-8 pt-8 border-t border-gray-200 flex flex-col sm:flex-row justify-between items-center">
          <p className="text-sm text-gray-500">
            © 2025 Collaborative Worldbuilding Platform. Open source under MIT License.
          </p>
          <div className="flex items-center space-x-1 text-sm text-gray-500 mt-4 sm:mt-0">
            <span>Built with</span>
            <Heart className="h-4 w-4 text-red-500" />
            <span>for collaborative storytelling</span>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer