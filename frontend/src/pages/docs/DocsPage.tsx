import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, BookOpen, FileText, Code, Users, Tag, Link as LinkIcon } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import Button from '@/components/ui/Button'

// Import CSS for syntax highlighting
import 'highlight.js/styles/github.css'

interface DocSection {
  id: string
  title: string
  description: string
  icon: React.ComponentType<any>
  content: string
}

const DocsPage: React.FC = () => {
  const { section } = useParams<{ section?: string }>()
  const [currentDoc, setCurrentDoc] = useState<DocSection | null>(null)
  const [loading, setLoading] = useState(false)

  const docSections: DocSection[] = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      description: 'Quick start guide and basic concepts',
      icon: BookOpen,
      content: `# Getting Started with Collaborative Worldbuilding

## Welcome to Collaborative Worldbuilding!

This platform enables teams to create rich, interconnected worlds with proper attribution and content relationships.

## Quick Start

### 1. Create Your First World
- Click "Create New World" from your dashboard
- Give it a descriptive title and description
- Choose whether to make it public or private

### 2. Add Content
The platform supports five content types:

**📄 Pages** - Landing pads for organizing story elements
- Use pages to group related content by theme, location, or time period
- Perfect for creating organizational hubs for your world

**📝 Essays** - Deep analysis and worldbuilding documentation
- Detailed explorations of concepts, systems, and lore
- Academic-style content with abstracts and thesis statements

**👤 Characters** - People, entities, and personalities
- Character profiles with relationships and traits
- Link characters to stories, images, and other content

**📖 Stories** - Narratives, plots, and sequences
- Short stories, plot outlines, and narrative content
- Connect stories to characters and world elements

**🖼️ Images** - Visual content, storyboards, and references
- Upload concept art, character designs, and storyboards
- Tag images with scene types, characters, and locations

### 3. Connect Content with Tags and Links

**🏷️ Tagging System:**
- Add descriptive tags to organize content
- Use autocomplete to discover existing tags
- Create collaborative tagging vocabularies

**🔗 Linking System:**
- Link related content together
- Build complex relationship networks
- Create circular references and content webs

## Core Concepts

### Immutable Content
All content is immutable - once created, it cannot be edited or deleted. This ensures:
- Complete attribution history
- Content integrity
- Collaboration transparency

### Collaborative Attribution
Every piece of content tracks:
- Original author
- Creation timestamp
- Relationship to other content
- Collaboration metrics

### Content Relationships
Build rich worlds through:
- **Tags** - Flexible content organization
- **Links** - Direct content relationships
- **Attribution** - Collaboration tracking

## Best Practices

### For Storyboarding Teams
1. **Upload storyboard images** with descriptive titles
2. **Tag images** with scene types, characters, locations
3. **Link storyboards** to story content and character profiles
4. **Use Pages** as landing pads for organizing sequences

### For Worldbuilding Teams
1. **Start with Pages** to create organizational structure
2. **Add Essays** for detailed world systems and lore
3. **Create Characters** and link them to relevant content
4. **Use consistent tagging** for easy content discovery

### For Collaborative Writing
1. **Link characters** to stories they appear in
2. **Tag content** by themes, genres, and story arcs
3. **Use Essays** to document world rules and systems
4. **Create Pages** to organize story timelines and locations

## Next Steps
- Explore the [API Documentation](#api-reference) for technical details
- Learn about [Tagging and Linking](#tagging-linking) for content organization
- Check out [Collaboration Features](#collaboration) for team workflows`
    },
    {
      id: 'api-reference',
      title: 'API Reference',
      description: 'Complete API documentation and examples',
      icon: Code,
      content: `# API Reference

## Base URL
\`\`\`
http://localhost:8000/api/
\`\`\`

## Authentication

All API requests require JWT authentication. Include the token in the Authorization header:

\`\`\`bash
Authorization: Bearer your_jwt_token
\`\`\`

### Login
\`\`\`http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
\`\`\`

**Response:**
\`\`\`json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "user@example.com"
  }
}
\`\`\`

## World Management

### List Worlds
\`\`\`http
GET /api/worlds/
Authorization: Bearer jwt_token
\`\`\`

### Create World
\`\`\`http
POST /api/worlds/
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "title": "My Fantasy World",
  "description": "A magical realm of adventure",
  "is_public": true
}
\`\`\`

### Get World Details
\`\`\`http
GET /api/worlds/{world_id}/
Authorization: Bearer jwt_token
\`\`\`

## Content Management

### Content Types
- **Pages** (\`/api/worlds/{world_id}/pages/\`)
- **Essays** (\`/api/worlds/{world_id}/essays/\`)
- **Characters** (\`/api/worlds/{world_id}/characters/\`)
- **Stories** (\`/api/worlds/{world_id}/stories/\`)
- **Images** (\`/api/worlds/{world_id}/images/\`)

### Create Content
\`\`\`http
POST /api/worlds/{world_id}/{content_type}/
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "title": "Content Title",
  "content": "Content body text",
  "tags": ["tag1", "tag2"]
}
\`\`\`

### Get Content
\`\`\`http
GET /api/worlds/{world_id}/{content_type}/{content_id}/
Authorization: Bearer jwt_token
\`\`\`

## Tagging System

### List Tags
\`\`\`http
GET /api/worlds/{world_id}/tags/
Authorization: Bearer jwt_token
\`\`\`

### Add Tags to Content
\`\`\`http
POST /api/worlds/{world_id}/{content_type}/{content_id}/add-tags/
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "tags": ["new-tag", "another-tag"]
}
\`\`\`

### Get Tag Details
\`\`\`http
GET /api/worlds/{world_id}/tags/{tag_name}/
Authorization: Bearer jwt_token
\`\`\`

## Linking System

### List Links
\`\`\`http
GET /api/worlds/{world_id}/links/
Authorization: Bearer jwt_token
\`\`\`

### Add Links to Content
\`\`\`http
POST /api/worlds/{world_id}/{content_type}/{content_id}/add-links/
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "links": [
    {
      "content_type": "character",
      "content_id": 5
    },
    {
      "content_type": "story", 
      "content_id": 3
    }
  ]
}
\`\`\`

## Search and Discovery

### Search Content
\`\`\`http
GET /api/worlds/{world_id}/search/?q=search_term
Authorization: Bearer jwt_token
\`\`\`

### Get Related Content
\`\`\`http
GET /api/worlds/{world_id}/{content_type}/{content_id}/related/
Authorization: Bearer jwt_token
\`\`\`

## Error Responses

All errors follow this format:
\`\`\`json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": ["Specific field error message"]
    }
  }
}
\`\`\`

## Status Codes
- **200 OK** - Request successful
- **201 Created** - Resource created
- **400 Bad Request** - Invalid request data
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Permission denied
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Validation error

## Rate Limiting
- **100 requests per minute** per user
- **1000 requests per hour** per user
- Rate limit headers included in responses

## Examples

### Complete Workflow Example
\`\`\`bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \\
  -H "Content-Type: application/json" \\
  -d '{"username": "admin", "password": "admin123"}'

# 2. Create a world
curl -X POST http://localhost:8000/api/worlds/ \\
  -H "Authorization: Bearer your_token" \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Test World", "description": "A test world"}'

# 3. Create a character
curl -X POST http://localhost:8000/api/worlds/1/characters/ \\
  -H "Authorization: Bearer your_token" \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Hero", "content": "A brave hero", "tags": ["protagonist"]}'

# 4. Create a story and link to character
curl -X POST http://localhost:8000/api/worlds/1/stories/ \\
  -H "Authorization: Bearer your_token" \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Adventure", "content": "An epic adventure"}'

curl -X POST http://localhost:8000/api/worlds/1/stories/1/add-links/ \\
  -H "Authorization: Bearer your_token" \\
  -H "Content-Type: application/json" \\
  -d '{"links": [{"content_type": "character", "content_id": 1}]}'
\`\`\``
    },
    {
      id: 'tagging-linking',
      title: 'Tagging & Linking',
      description: 'Content organization and relationship management',
      icon: Tag,
      content: `# Tagging & Linking System

## Overview

The tagging and linking system enables sophisticated content organization and relationship management for collaborative worldbuilding.

## 🏷️ Tagging System

### What are Tags?
Tags are flexible labels that help organize and categorize content. They enable:
- **Content Discovery** - Find related content across your world
- **Collaborative Organization** - Shared vocabularies for teams
- **Thematic Grouping** - Organize by themes, locations, time periods
- **Cross-Content Relationships** - Connect different content types

### Using Tags

#### Adding Tags
1. **During Creation** - Add tags when creating new content
2. **Manage Tags Button** - Use the "Manage Tags" interface on content pages
3. **Autocomplete** - Get suggestions from existing world tags
4. **Bulk Tagging** - Add multiple tags at once

#### Tag Best Practices

**For Storyboarding:**
- \`scene-type-action\`, \`scene-type-dialogue\`, \`scene-type-establishing\`
- \`character-hero\`, \`character-villain\`, \`character-supporting\`
- \`location-interior\`, \`location-exterior\`, \`location-fantasy\`
- \`mood-dramatic\`, \`mood-comedic\`, \`mood-suspenseful\`

**For Worldbuilding:**
- \`magic-system\`, \`political-system\`, \`economic-system\`
- \`culture-elven\`, \`culture-human\`, \`culture-dwarven\`
- \`timeline-ancient\`, \`timeline-medieval\`, \`timeline-modern\`
- \`geography-mountains\`, \`geography-forests\`, \`geography-cities\`

**For Character Development:**
- \`personality-brave\`, \`personality-cunning\`, \`personality-wise\`
- \`role-protagonist\`, \`role-antagonist\`, \`role-mentor\`
- \`arc-growth\`, \`arc-fall\`, \`arc-redemption\`

### Tag Management Features

#### Autocomplete & Suggestions
- Real-time suggestions from existing world tags
- Prevents duplicate tags with similar names
- Shows tag usage statistics

#### Tag Limits
- Default maximum of 10 tags per content item
- Configurable limits for different content types
- User feedback when approaching limits

#### Tag Discovery
- Browse all tags in a world at \`/worlds/{id}/tags\`
- View all content tagged with specific tags
- See tag usage statistics and creation dates

## 🔗 Linking System

### What are Links?
Links create direct relationships between content items, enabling:
- **Content Networks** - Build complex webs of related content
- **Narrative Connections** - Link characters to stories, images to essays
- **Reference Systems** - Create citation and reference networks
- **Collaborative Relationships** - Connect content from different authors

### Types of Content Links

#### Cross-Content Type Linking
- **Essay → Character** - Essays analyzing characters
- **Character → Image** - Character portraits and references
- **Image → Story** - Storyboards for narrative sequences
- **Story → Page** - Stories organized on landing pages
- **Page → Essay** - Pages referencing detailed analysis

#### Same-Content Type Linking
- **Character → Character** - Character relationships
- **Story → Story** - Story sequences and series
- **Page → Page** - Hierarchical page organization
- **Essay → Essay** - Academic references and citations

### Using Links

#### Adding Links
1. **Manage Links Button** - Use the "Manage Links" interface
2. **Search & Filter** - Find content by type and search terms
3. **Content Type Selection** - Choose what type of content to link to
4. **Duplicate Prevention** - System prevents duplicate links

#### Link Management Features

#### Content Search
- Search by content title
- Filter by content type (pages, characters, stories, essays, images)
- Real-time search results
- Content metadata display

#### Relationship Networks
- Bidirectional linking support
- Circular reference handling
- Complex relationship networks
- Link discovery and traversal

#### Visual Indicators
- Content type icons
- Author attribution
- Creation dates
- Link relationship types

## 🎨 Collaborative Workflows

### Pages as Landing Pads
Use Pages to create organizational hubs:

\`\`\`
Page: "The Western Kingdoms"
├── Essay: "Political Structure of the West"
├── Character: "King Aldric of Westmarch"
├── Story: "The Battle of Westmarch"
├── Image: "Map of Western Kingdoms"
└── Page: "Western Kingdom Timeline"
\`\`\`

### Character-Centric Organization
Build character networks:

\`\`\`
Character: "Hero Protagonist"
├── Story: "Hero's Origin Story"
├── Image: "Character Design Sheet"
├── Essay: "Character Development Analysis"
└── Character: "Mentor Figure" (relationship link)
\`\`\`

### Thematic Tagging Strategy
Create consistent tagging vocabularies:

\`\`\`
Magic System Content:
- Tag: "magic-system"
  ├── Essay: "Fundamentals of Magic"
  ├── Character: "Archmage Merlin"
  ├── Story: "The First Spell"
  └── Page: "Magic System Overview"
\`\`\`

## 🔧 Technical Implementation

### Frontend Components

#### TagManager Component
- Interactive tag addition/removal
- Autocomplete with existing tags
- Keyboard navigation (Enter/Escape)
- Tag limit enforcement
- Real-time suggestions

#### ContentLinker Component
- Content search and filtering
- Content type selection
- Duplicate link prevention
- Existing link display
- Relationship management

### Backend API Integration

#### Tag Endpoints
- \`GET /worlds/{id}/tags/\` - List all tags
- \`GET /worlds/{id}/tags/{name}/\` - Tag details with tagged content
- \`POST /worlds/{id}/{type}/{id}/add-tags/\` - Add tags to content

#### Link Endpoints
- \`GET /worlds/{id}/links/\` - List all links
- \`POST /worlds/{id}/{type}/{id}/add-links/\` - Add links to content
- Bidirectional relationship creation

## 📊 Analytics & Insights

### Tag Analytics
- Most popular tags in world
- Tag usage trends over time
- Collaborative tagging patterns
- Tag-based content discovery metrics

### Link Analytics
- Content relationship networks
- Most connected content items
- Collaboration patterns through links
- Content influence and centrality scores

## 🎯 Best Practices Summary

### Tagging Strategy
1. **Consistent Vocabulary** - Establish team tagging conventions
2. **Hierarchical Tags** - Use prefixes for organization (\`location-\`, \`character-\`)
3. **Collaborative Tagging** - Multiple team members can tag the same content
4. **Tag Discovery** - Regularly browse tags to discover related content

### Linking Strategy
1. **Meaningful Relationships** - Only link truly related content
2. **Bidirectional Thinking** - Consider how content relates in both directions
3. **Network Building** - Create rich webs of interconnected content
4. **Landing Pad Organization** - Use Pages as organizational hubs

### Collaboration Tips
1. **Shared Vocabularies** - Develop team conventions for tags and organization
2. **Attribution Respect** - Link to others' content to show collaboration
3. **Content Discovery** - Use tags and links to explore team members' work
4. **Organizational Hubs** - Create Pages that serve as team landing pads

The tagging and linking system transforms individual content into collaborative knowledge networks, perfect for worldbuilding teams and creative collaborations!`
    },
    {
      id: 'collaboration',
      title: 'Collaboration Features',
      description: 'Multi-user workflows and team features',
      icon: Users,
      content: `# Collaboration Features

## Overview

The Collaborative Worldbuilding Platform is designed from the ground up for team-based creative work, with comprehensive attribution, content relationships, and collaborative workflows.

## 🤝 Multi-User Collaboration

### World Sharing
- **Public Worlds** - Discoverable by all users
- **Private Worlds** - Invitation-only collaboration
- **Contributor Management** - Control who can add content
- **Permission Levels** - Different access levels for team members

### Content Attribution
Every piece of content includes:
- **Original Author** - Who created the content
- **Creation Timestamp** - When it was created
- **Attribution String** - Human-readable attribution
- **Collaboration Metrics** - How content connects to others' work

### Immutable Content Model
- **No Editing** - Content cannot be modified after creation
- **No Deletion** - Content is preserved forever
- **Complete History** - Full audit trail of all contributions
- **Attribution Integrity** - Ensures proper credit for all work

## 🔗 Collaborative Content Networks

### Cross-Author Linking
- Link your content to others' work
- Build on teammates' ideas and concepts
- Create collaborative narrative networks
- Maintain attribution for all connections

### Collaborative Tagging
- Multiple users can tag the same content
- Shared tagging vocabularies develop naturally
- Tag-based content discovery across all contributors
- Collaborative organization emerges organically

### Content Relationships
Build rich collaborative networks:

\`\`\`
Author A: Creates "Magic System Essay"
Author B: Creates "Wizard Character" → Links to Magic System
Author C: Creates "Magic Academy Story" → Links to both
Author A: Creates "Advanced Magic Page" → Links to all three
\`\`\`

## 📊 Collaboration Analytics

### World Collaboration Metrics
- **Total Contributors** - Number of active contributors
- **Cross-Author Links** - Links between different authors' content
- **Collaboration Density** - How interconnected the content is
- **Collaboration Health Score** - Overall collaboration assessment

### Individual Contribution Tracking
- **Content Count** - Number of items contributed
- **Link Creation** - Links made to others' content
- **Link Reception** - Links received from others
- **Collaboration Score** - Individual collaboration rating

### Team Insights
- **Most Collaborative Pairs** - Which users collaborate most
- **Content Influence** - Which content is most referenced
- **Collaboration Trends** - How collaboration changes over time
- **Network Centrality** - Who are the key connectors in the team

## 🎨 Collaborative Workflows

### Storyboarding Teams

#### Workflow Example:
1. **Art Director** creates "Storyboard Sequence" Page
2. **Storyboard Artist** uploads sequence images, links to Page
3. **Writer** creates Story content, links to storyboard images
4. **Character Designer** uploads character sheets, links to Story
5. **Director** creates "Scene Notes" Essay, links to all content

#### Best Practices:
- Use **Pages as landing pads** for organizing sequences
- **Tag images** with scene types, characters, locations
- **Link storyboards** to narrative content
- **Cross-reference** character designs with story content

### Worldbuilding Teams

#### Workflow Example:
1. **World Creator** establishes "World Overview" Page
2. **Lore Writer** creates Essays on world systems, links to Overview
3. **Character Creator** develops Characters, links to relevant Essays
4. **Story Writer** creates Stories featuring Characters
5. **Artist** uploads concept art, links to Characters and Locations

#### Best Practices:
- Create **hierarchical Page structures** for organization
- Use **consistent tagging** for world elements
- **Link Characters** to Stories they appear in
- **Reference Essays** for world system documentation

### Writing Collaboratives

#### Workflow Example:
1. **Lead Writer** creates "Story Arc" Page
2. **Character Writers** create Character profiles
3. **Scene Writers** create Story segments, link to Characters
4. **Editor** creates "Style Guide" Essay, links to all content
5. **Continuity Manager** creates "Timeline" Page, links to all Stories

#### Best Practices:
- Use **Story → Character links** for cast tracking
- **Tag content** by story arcs and themes
- Create **reference Essays** for world rules and style
- Use **Pages** for timeline and continuity organization

## 🛡️ Attribution & Credit

### Automatic Attribution
Every content item automatically includes:
- Author name and profile information
- Creation date and time
- Unique content identifier
- Link to author's other contributions

### Attribution Display
Attribution appears in multiple contexts:
- **Content Detail Pages** - Full attribution information
- **Content Lists** - Author and date summary
- **Link References** - Attribution in relationship context
- **Search Results** - Author information in results

### Collaboration Recognition
The system recognizes and displays:
- **Cross-Author References** - When you link to others' work
- **Influence Metrics** - How much your content is referenced
- **Collaboration Patterns** - Your collaboration relationships
- **Team Contributions** - Your role in collaborative networks

## 🔍 Content Discovery

### Collaborative Discovery Features
- **Browse by Author** - Explore specific contributors' work
- **Tag-Based Discovery** - Find content through collaborative tags
- **Link Networks** - Follow content relationships
- **Related Content** - Discover connected work

### Team Content Exploration
- **World Timeline** - Chronological view of all contributions
- **Contributor Profiles** - See each team member's contributions
- **Collaboration Networks** - Visualize team relationships
- **Popular Content** - Most linked and referenced items

## 🎯 Collaboration Best Practices

### Building Collaborative Culture
1. **Link Generously** - Reference others' work when relevant
2. **Tag Consistently** - Develop shared vocabularies
3. **Attribute Properly** - The system handles this automatically
4. **Explore Actively** - Discover and build on teammates' work

### Effective Team Organization
1. **Establish Conventions** - Agree on tagging and organization patterns
2. **Create Landing Pads** - Use Pages for team organization
3. **Regular Discovery** - Browse tags and links to find collaboration opportunities
4. **Respect Attribution** - Build on others' work while maintaining proper credit

### Managing Large Teams
1. **Role-Based Organization** - Different team members focus on different content types
2. **Hierarchical Structure** - Use Pages to create organizational hierarchies
3. **Consistent Tagging** - Establish team-wide tagging conventions
4. **Regular Coordination** - Use collaboration metrics to track team health

## 📈 Measuring Collaboration Success

### Healthy Collaboration Indicators
- **High Cross-Author Link Density** - Team members reference each other's work
- **Diverse Content Networks** - Multiple content types interconnected
- **Active Tag Usage** - Shared vocabularies developing
- **Balanced Contributions** - All team members actively participating

### Collaboration Health Metrics
- **Collaboration Score** - Overall team collaboration rating
- **Network Density** - How interconnected the content is
- **Contributor Diversity** - How evenly distributed contributions are
- **Cross-Author Activity** - Amount of inter-team member collaboration

### Improving Team Collaboration
1. **Encourage Linking** - Actively reference teammates' work
2. **Develop Shared Tags** - Create collaborative vocabularies
3. **Create Hub Pages** - Establish organizational landing pads
4. **Regular Team Reviews** - Use collaboration metrics to guide team development

## 🚀 Advanced Collaboration Features

### Attribution Networks
- **Influence Graphs** - Visualize who influences whom
- **Collaboration Clusters** - Identify close collaboration groups
- **Content Centrality** - Find the most important content in your world
- **Team Dynamics** - Understand collaboration patterns

### Collaborative Intelligence
- **Content Suggestions** - Discover content that might benefit from linking
- **Collaboration Opportunities** - Find teammates to collaborate with
- **Tag Recommendations** - Suggested tags based on team patterns
- **Attribution Insights** - Understand your collaboration impact

The collaboration features transform individual creativity into powerful team-based worldbuilding, ensuring everyone gets proper credit while building amazing collaborative worlds together!`
    }
  ]

  useEffect(() => {
    const sectionId = section || 'getting-started'
    const doc = docSections.find(d => d.id === sectionId)
    if (doc) {
      setCurrentDoc(doc)
    }
  }, [section])

  if (!currentDoc) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Documentation not found</h2>
          <p className="text-gray-600 mb-4">The requested documentation section doesn't exist.</p>
          <Button asChild>
            <Link to="/docs">Back to Documentation</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Navigation */}
      <Button
        variant="ghost"
        asChild
        className="mb-6"
      >
        <Link to="/">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Home
        </Link>
      </Button>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Documentation</h3>
            <nav className="space-y-2">
              {docSections.map((doc) => {
                const Icon = doc.icon
                const isActive = currentDoc.id === doc.id
                return (
                  <Link
                    key={doc.id}
                    to={`/docs/${doc.id}`}
                    className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary-100 text-primary-800 border border-primary-200'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <div>
                      <div className="font-medium">{doc.title}</div>
                      <div className="text-xs text-gray-500">{doc.description}</div>
                    </div>
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <div className="prose prose-lg max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
                components={{
                  // Custom components for better styling
                  h1: ({ children }) => (
                    <h1 className="text-3xl font-bold text-gray-900 mb-6 pb-3 border-b border-gray-200">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">
                      {children}
                    </h3>
                  ),
                  code: ({ inline, children, ...props }) => (
                    inline ? (
                      <code className="bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-sm font-mono" {...props}>
                        {children}
                      </code>
                    ) : (
                      <code className="block bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono" {...props}>
                        {children}
                      </code>
                    )
                  ),
                  pre: ({ children }) => (
                    <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4">
                      {children}
                    </pre>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-4 border-primary-200 bg-primary-50 p-4 my-4 italic">
                      {children}
                    </blockquote>
                  ),
                  a: ({ href, children }) => (
                    <a
                      href={href}
                      className="text-primary-600 hover:text-primary-800 underline"
                      target={href?.startsWith('http') ? '_blank' : undefined}
                      rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
                    >
                      {children}
                    </a>
                  ),
                }}
              >
                {currentDoc.content}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DocsPage