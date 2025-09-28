// User and Authentication Types
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  date_joined: string
}

export interface UserProfile {
  username: string
  email: string
  first_name: string
  last_name: string
  date_joined: string
  bio: string
  preferred_content_types: string[]
  contribution_count: number
  worlds_created: number
  created_at: string
  updated_at: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  password_confirm: string
  first_name?: string
  last_name?: string
  bio?: string
  preferred_content_types?: string[]
}

// World Types
export interface World {
  id: number
  title: string
  description: string
  creator: User
  is_public: boolean
  created_at: string
  updated_at: string
  content_counts: {
    pages: number
    essays: number
    characters: number
    stories: number
    images: number
  }
  contributor_count: number
  collaboration_stats?: {
    total_collaborations: number
    cross_author_collaborations: number
    collaboration_percentage: number
    collaboration_network?: {
      nodes: number
      edges: number
      density: number
    }
  }
  top_contributors?: Contributor[]
}

export interface Contributor {
  user: User
  contribution_count: number
  content_types: string[]
  collaboration_score?: number
  first_contribution?: string
  last_contribution?: string
  collaboration_metrics?: {
    links_created: number
    links_received: number
    collaboration_score: number
    cross_author_links: number
  }
}

export interface CreateWorldData {
  title: string
  description: string
  is_public: boolean
}

// Content Types
export interface ContentBase {
  id: number
  title: string
  content: string
  author: User
  world: number
  created_at: string
  attribution: string
  collaboration_info: {
    links_to_count: number
    linked_from_count: number
    tags_count: number
    is_collaborative: boolean
    collaboration_score: number
  }
  tags: Tag[]
  linked_content: LinkedContent[]
}

export interface Page extends ContentBase {
  summary?: string
}

export interface Essay extends ContentBase {
  abstract?: string
  topic?: string
  thesis?: string
  word_count: number
}

export interface Character extends ContentBase {
  full_name: string
  species?: string
  occupation?: string
  personality_traits: string[]
  relationships: Record<string, string>
}

export interface Story extends ContentBase {
  genre?: string
  story_type?: string
  is_canonical: boolean
  word_count: number
  main_characters: string[]
}

export interface Image extends ContentBase {
  image_url: string
  alt_text: string
  dimensions?: string
  file_size?: number
}

export interface LinkedContent {
  id: number
  title: string
  type: string
  author: User
  created_at: string
  attribution: string
}

// Tag and Link Types
export interface Tag {
  id: number
  name: string
  world: number
  usage_count: number
  created_at: string
}

export interface ContentLink {
  id: number
  from_content: {
    id: number
    title: string
    type: string
  }
  to_content: {
    id: number
    title: string
    type: string
  }
  created_at: string
}

// Timeline and Search Types
export interface TimelineItem {
  id: number
  title: string
  content_type: string
  author: User
  created_at: string
  summary?: string
  tags: string[]
  link_count: number
  attribution: string
}

export interface Timeline {
  count: number
  next: string | null
  previous: string | null
  timeline: TimelineItem[]
  pagination: {
    current_page: number
    total_pages: number
    page_size: number
    total_items: number
  }
}

export interface SearchResult {
  id: number
  title: string
  content_type: string
  author: User
  created_at: string
  excerpt: string
  relevance_score: number
  tags: string[]
}

export interface SearchResponse {
  query: string
  total_results: number
  results: SearchResult[]
  facets: {
    content_types: Record<string, number>
    authors: Record<string, number>
    tags: Record<string, number>
  }
}

// Form Types
export interface CreateContentData {
  title: string
  content: string
  tags?: string[]
}

export interface CreatePageData extends CreateContentData {
  summary?: string
}

export interface CreateEssayData extends CreateContentData {
  abstract?: string
  topic?: string
  thesis?: string
}

export interface CreateCharacterData extends CreateContentData {
  full_name: string
  species?: string
  occupation?: string
  personality_traits?: string[]
  relationships?: Record<string, string>
}

export interface CreateStoryData extends CreateContentData {
  genre?: string
  story_type?: string
  is_canonical?: boolean
  main_characters?: string[]
}

export interface CreateImageData extends CreateContentData {
  alt_text: string
  image_file: File
}

// API Response Types
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface ApiError {
  error: {
    code: string
    message: string
    details?: Record<string, string[]>
    timestamp: string
    request_id: string
  }
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// Content Type Union
export type Content = Page | Essay | Character | Story | Image
export type ContentType = 'page' | 'essay' | 'character' | 'story' | 'image'

// Filter and Query Types
export interface WorldFilters {
  search?: string
  creator?: string
  is_public?: boolean
}

export interface ContentFilters {
  search?: string
  author?: string
  tags?: string
  content_type?: ContentType
  ordering?: string
}

export interface TimelineFilters {
  content_type?: ContentType
  author?: string
  tags?: string
  search?: string
  page?: number
  page_size?: number
}

// Attribution Types
export interface AttributionDetails {
  content: {
    id: number
    title: string
    author: User
    created_at: string
  }
  attribution: {
    primary_author: string
    creation_date: string
    attribution_string: string
  }
  collaboration_metrics: {
    references_made: LinkedContent[]
    referenced_by: LinkedContent[]
    collaboration_assessment: {
      is_collaborative: boolean
      collaboration_score: number
      cross_author_references: number
      influence_score: number
    }
  }
  attribution_suggestions: Array<{
    type: string
    content_id: number
    content_title: string
    reason: string
  }>
}