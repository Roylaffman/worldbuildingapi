# API Documentation - Collaborative Worldbuilding Platform

## Overview

The Collaborative Worldbuilding Platform provides a RESTful API for creating and managing collaborative worldbuilding content. The API supports immutable content creation, tagging, linking, and comprehensive attribution tracking.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. All protected endpoints require a valid JWT token in the Authorization header.

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register/
```

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "password_confirm": "string",
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "preferred_content_types": ["page", "character", "story", "essay", "image"]
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string"
  },
  "profile": {
    "bio": "string",
    "preferred_content_types": ["page"],
    "contribution_count": 0,
    "worlds_created": 0
  }
}
```

#### Login
```http
POST /api/auth/login/
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string"
  }
}
```

#### Refresh Token
```http
POST /api/auth/refresh/
```

**Request Body:**
```json
{
  "refresh": "jwt_refresh_token"
}
```

**Response (200 OK):**
```json
{
  "access": "new_jwt_access_token"
}
```

#### User Profile
```http
GET /api/auth/user/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "date_joined": "2025-09-27T20:00:00Z"
  },
  "profile": {
    "bio": "string",
    "preferred_content_types": ["page"],
    "contribution_count": 5,
    "worlds_created": 2,
    "created_at": "2025-09-27T20:00:00Z",
    "updated_at": "2025-09-27T20:00:00Z"
  }
}
```

## World Management

### List Worlds
```http
GET /api/worlds/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Query Parameters:**
- `search` (string): Search worlds by title or description
- `creator` (string): Filter by creator username
- `is_public` (boolean): Filter by public/private status

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Fantasy Realm",
    "description": "A magical world of adventure",
    "creator": {
      "id": 1,
      "username": "creator",
      "first_name": "John",
      "last_name": "Doe"
    },
    "is_public": true,
    "created_at": "2025-09-27T20:00:00Z",
    "updated_at": "2025-09-27T20:00:00Z",
    "content_counts": {
      "pages": 5,
      "essays": 2,
      "characters": 8,
      "stories": 3,
      "images": 1
    },
    "contributor_count": 3,
    "collaboration_stats": {
      "total_collaborations": 12,
      "cross_author_collaborations": 8,
      "collaboration_percentage": 66.7
    },
    "top_contributors": [
      {
        "user": {
          "id": 1,
          "username": "creator",
          "first_name": "John",
          "last_name": "Doe"
        },
        "contribution_count": 10,
        "content_types": ["page", "character"]
      }
    ]
  }
]
```

### Create World
```http
POST /api/worlds/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "is_public": true
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "creator": {
    "id": 1,
    "username": "creator"
  },
  "is_public": true,
  "created_at": "2025-09-27T20:00:00Z",
  "updated_at": "2025-09-27T20:00:00Z",
  "content_counts": {
    "pages": 0,
    "essays": 0,
    "characters": 0,
    "stories": 0,
    "images": 0
  },
  "contributor_count": 0
}
```

### Get World Details
```http
GET /api/worlds/{world_id}/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Fantasy Realm",
  "description": "A magical world of adventure",
  "creator": {
    "id": 1,
    "username": "creator",
    "first_name": "John",
    "last_name": "Doe"
  },
  "is_public": true,
  "created_at": "2025-09-27T20:00:00Z",
  "updated_at": "2025-09-27T20:00:00Z",
  "content_counts": {
    "pages": 5,
    "essays": 2,
    "characters": 8,
    "stories": 3,
    "images": 1
  },
  "contributor_count": 3,
  "collaboration_stats": {
    "total_collaborations": 12,
    "cross_author_collaborations": 8,
    "collaboration_percentage": 66.7,
    "collaboration_network": {
      "nodes": 3,
      "edges": 8,
      "density": 0.67
    }
  },
  "top_contributors": [
    {
      "user": {
        "id": 1,
        "username": "creator",
        "first_name": "John",
        "last_name": "Doe"
      },
      "contribution_count": 10,
      "content_types": ["page", "character"],
      "collaboration_score": 8.5
    }
  ]
}
```

### Update World
```http
PATCH /api/worlds/{world_id}/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "is_public": true
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Updated Title",
  "description": "Updated description",
  "creator": {
    "id": 1,
    "username": "creator"
  },
  "is_public": true,
  "updated_at": "2025-09-27T21:00:00Z"
}
```

### World Contributors
```http
GET /api/worlds/{world_id}/contributors/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response (200 OK):**
```json
{
  "total_contributors": 3,
  "contributors": [
    {
      "user": {
        "id": 1,
        "username": "creator",
        "first_name": "John",
        "last_name": "Doe"
      },
      "contribution_count": 10,
      "content_types": ["page", "character", "story"],
      "first_contribution": "2025-09-20T10:00:00Z",
      "last_contribution": "2025-09-27T15:00:00Z",
      "collaboration_metrics": {
        "links_created": 5,
        "links_received": 8,
        "collaboration_score": 8.5,
        "cross_author_links": 3
      }
    }
  ],
  "collaboration_summary": {
    "total_cross_author_links": 12,
    "collaboration_health": "high",
    "most_collaborative_pair": {
      "user1": "creator",
      "user2": "collaborator",
      "link_count": 5
    }
  }
}
```

### World Timeline
```http
GET /api/worlds/{world_id}/timeline/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Query Parameters:**
- `content_type` (string): Filter by content type (page, essay, character, story, image)
- `author` (string): Filter by author username
- `tags` (string): Filter by tag names (comma-separated)
- `search` (string): Search content
- `page` (integer): Page number for pagination
- `page_size` (integer): Number of items per page

**Response (200 OK):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/worlds/1/timeline/?page=2",
  "previous": null,
  "timeline": [
    {
      "id": 1,
      "title": "Magic System",
      "content_type": "page",
      "author": {
        "id": 1,
        "username": "creator",
        "first_name": "John",
        "last_name": "Doe"
      },
      "created_at": "2025-09-27T20:00:00Z",
      "summary": "Overview of the magic system",
      "tags": ["magic", "system"],
      "link_count": 3,
      "attribution": "Created by creator on September 27, 2025 at 08:00 PM"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "page_size": 10,
    "total_items": 25
  }
}
```

### World Attribution Report
```http
GET /api/worlds/{world_id}/attribution_report/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response (200 OK):**
```json
{
  "world": {
    "id": 1,
    "title": "Fantasy Realm"
  },
  "attribution_network": {
    "total_content": 19,
    "total_links": 25,
    "collaboration_density": 0.68,
    "attribution_graph": {
      "nodes": [
        {
          "id": "user_1",
          "username": "creator",
          "content_count": 10,
          "centrality_score": 0.85
        }
      ],
      "edges": [
        {
          "source": "user_1",
          "target": "user_2",
          "weight": 5,
          "link_type": "references"
        }
      ]
    }
  },
  "collaboration_health": {
    "score": 8.5,
    "status": "excellent",
    "metrics": {
      "cross_author_collaboration": 0.75,
      "content_interconnectedness": 0.68,
      "contributor_diversity": 0.82
    }
  },
  "attribution_suggestions": [
    {
      "type": "missing_attribution",
      "content_id": 5,
      "suggestion": "Consider linking to related character profiles"
    }
  ]
}
```

## Content Management

### Pages

#### List Pages
```http
GET /api/worlds/{world_id}/pages/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Query Parameters:**
- `search` (string): Search pages by title or content
- `author` (string): Filter by author username
- `tags` (string): Filter by tag names (comma-separated)
- `ordering` (string): Order by field (created_at, title, author)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Magic System Overview",
    "content": "The magic system in this world is based on...",
    "summary": "Overview of the magic system",
    "author": {
      "id": 1,
      "username": "creator",
      "first_name": "John",
      "last_name": "Doe"
    },
    "world": 1,
    "created_at": "2025-09-27T20:00:00Z",
    "attribution": "Created by creator on September 27, 2025 at 08:00 PM",
    "collaboration_info": {
      "links_to_count": 3,
      "linked_from_count": 5,
      "tags_count": 2,
      "is_collaborative": true,
      "collaboration_score": 7.5
    },
    "tags": [
      {
        "id": 1,
        "name": "magic",
        "usage_count": 5
      }
    ],
    "linked_content": [
      {
        "id": 2,
        "title": "Fire Magic",
        "type": "page",
        "author": {
          "id": 2,
          "username": "collaborator"
        },
        "attribution": "Created by collaborator on September 26, 2025"
      }
    ]
  }
]
```

#### Create Page
```http
POST /api/worlds/{world_id}/pages/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "string",
  "content": "string",
  "summary": "string",
  "tags": ["tag1", "tag2"]
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "string",
  "content": "string",
  "summary": "string",
  "author": {
    "id": 1,
    "username": "creator",
    "first_name": "John",
    "last_name": "Doe"
  },
  "world": 1,
  "created_at": "2025-09-27T20:00:00Z",
  "attribution": "Created by creator on September 27, 2025 at 08:00 PM",
  "collaboration_info": {
    "links_to_count": 0,
    "linked_from_count": 0,
    "tags_count": 2,
    "is_collaborative": false,
    "collaboration_score": 0.0
  },
  "tags": [
    {
      "id": 1,
      "name": "tag1",
      "usage_count": 1
    }
  ],
  "linked_content": []
}
```

#### Get Page Details
```http
GET /api/worlds/{world_id}/pages/{page_id}/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Magic System Overview",
  "content": "The magic system in this world is based on...",
  "summary": "Overview of the magic system",
  "author": {
    "id": 1,
    "username": "creator",
    "first_name": "John",
    "last_name": "Doe"
  },
  "world": 1,
  "created_at": "2025-09-27T20:00:00Z",
  "attribution": "Created by creator on September 27, 2025 at 08:00 PM",
  "collaboration_info": {
    "links_to_count": 3,
    "linked_from_count": 5,
    "tags_count": 2,
    "is_collaborative": true,
    "collaboration_score": 7.5
  },
  "tags": [
    {
      "id": 1,
      "name": "magic",
      "usage_count": 5
    }
  ],
  "linked_content": [
    {
      "id": 2,
      "title": "Fire Magic",
      "type": "page",
      "author": {
        "id": 2,
        "username": "collaborator",
        "first_name": "Jane",
        "last_name": "Smith"
      },
      "created_at": "2025-09-26T15:00:00Z",
      "attribution": "Created by collaborator on September 26, 2025 at 03:00 PM"
    }
  ]
}
```

#### Add Tags to Page
```http
POST /api/worlds/{world_id}/pages/{page_id}/add-tags/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
Content-Type: application/json
```

**Request Body:**
```json
{
  "tags": ["new-tag", "another-tag"]
}
```

**Response (200 OK):**
```json
{
  "added_tags": ["new-tag", "another-tag"],
  "existing_tags": [],
  "total_tags": 4
}
```

#### Add Links to Page
```http
POST /api/worlds/{world_id}/pages/{page_id}/add-links/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
Content-Type: application/json
```

**Request Body:**
```json
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
```

**Response (200 OK):**
```json
{
  "added_links": [
    {
      "target_type": "character",
      "target_id": 5,
      "target_title": "Hero Character"
    }
  ],
  "existing_links": [],
  "total_links": 3
}
```

#### Page Attribution Details
```http
GET /api/worlds/{world_id}/pages/{page_id}/attribution_details/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response (200 OK):**
```json
{
  "content": {
    "id": 1,
    "title": "Magic System Overview",
    "author": {
      "id": 1,
      "username": "creator",
      "first_name": "John",
      "last_name": "Doe"
    },
    "created_at": "2025-09-27T20:00:00Z"
  },
  "attribution": {
    "primary_author": "creator",
    "creation_date": "2025-09-27T20:00:00Z",
    "attribution_string": "Created by creator on September 27, 2025 at 08:00 PM"
  },
  "collaboration_metrics": {
    "references_made": [
      {
        "id": 2,
        "title": "Fire Magic",
        "type": "page",
        "author": "collaborator"
      }
    ],
    "referenced_by": [
      {
        "id": 3,
        "title": "Wizard Character",
        "type": "character",
        "author": "another_user"
      }
    ],
    "collaboration_assessment": {
      "is_collaborative": true,
      "collaboration_score": 7.5,
      "cross_author_references": 2,
      "influence_score": 8.2
    }
  },
  "attribution_suggestions": [
    {
      "type": "potential_reference",
      "content_id": 7,
      "content_title": "Elemental Magic",
      "reason": "Similar content that might benefit from linking"
    }
  ]
}
```

### Characters

#### List Characters
```http
GET /api/worlds/{world_id}/characters/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Query Parameters:**
- `search` (string): Search characters by name or content
- `species` (string): Filter by species
- `occupation` (string): Filter by occupation
- `author` (string): Filter by author username

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Gandalf the Wizard",
    "content": "A powerful wizard who guides heroes...",
    "full_name": "Gandalf the Grey",
    "species": "Maiar",
    "occupation": "Wizard",
    "personality_traits": ["wise", "patient", "powerful"],
    "relationships": {
      "mentor": "Frodo Baggins",
      "ally": "Aragorn"
    },
    "author": {
      "id": 1,
      "username": "creator",
      "first_name": "John",
      "last_name": "Doe"
    },
    "world": 1,
    "created_at": "2025-09-27T20:00:00Z",
    "attribution": "Created by creator on September 27, 2025 at 08:00 PM",
    "collaboration_info": {
      "links_to_count": 2,
      "linked_from_count": 4,
      "tags_count": 3,
      "is_collaborative": true,
      "collaboration_score": 8.0
    },
    "tags": [
      {
        "id": 2,
        "name": "wizard",
        "usage_count": 3
      }
    ],
    "linked_content": []
  }
]
```

#### Create Character
```http
POST /api/worlds/{world_id}/characters/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "string",
  "content": "string",
  "full_name": "string",
  "species": "string",
  "occupation": "string",
  "personality_traits": ["trait1", "trait2"],
  "relationships": {
    "friend": "Character Name",
    "enemy": "Villain Name"
  },
  "tags": ["tag1", "tag2"]
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "string",
  "content": "string",
  "full_name": "string",
  "species": "string",
  "occupation": "string",
  "personality_traits": ["trait1", "trait2"],
  "relationships": {
    "friend": "Character Name",
    "enemy": "Villain Name"
  },
  "author": {
    "id": 1,
    "username": "creator"
  },
  "world": 1,
  "created_at": "2025-09-27T20:00:00Z",
  "attribution": "Created by creator on September 27, 2025 at 08:00 PM",
  "collaboration_info": {
    "links_to_count": 0,
    "linked_from_count": 0,
    "tags_count": 2,
    "is_collaborative": false,
    "collaboration_score": 0.0
  },
  "tags": [],
  "linked_content": []
}
```

### Stories

#### List Stories
```http
GET /api/worlds/{world_id}/stories/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Query Parameters:**
- `search` (string): Search stories by title or content
- `genre` (string): Filter by genre
- `is_canonical` (boolean): Filter by canonical status
- `min_words` (integer): Minimum word count
- `max_words` (integer): Maximum word count

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "The Hero's Journey",
    "content": "In a land far away, a young hero...",
    "genre": "Fantasy",
    "story_type": "short_story",
    "is_canonical": true,
    "word_count": 1250,
    "main_characters": ["Hero", "Mentor", "Villain"],
    "author": {
      "id": 1,
      "username": "creator"
    },
    "world": 1,
    "created_at": "2025-09-27T20:00:00Z",
    "attribution": "Created by creator on September 27, 2025 at 08:00 PM",
    "collaboration_info": {
      "links_to_count": 5,
      "linked_from_count": 2,
      "tags_count": 4,
      "is_collaborative": true,
      "collaboration_score": 9.2
    },
    "tags": [],
    "linked_content": []
  }
]
```

#### Create Story
```http
POST /api/worlds/{world_id}/stories/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "string",
  "content": "string",
  "genre": "string",
  "story_type": "short_story",
  "is_canonical": true,
  "main_characters": ["character1", "character2"],
  "tags": ["tag1", "tag2"]
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "string",
  "content": "string",
  "genre": "string",
  "story_type": "short_story",
  "is_canonical": true,
  "word_count": 125,
  "main_characters": ["character1", "character2"],
  "author": {
    "id": 1,
    "username": "creator"
  },
  "world": 1,
  "created_at": "2025-09-27T20:00:00Z",
  "attribution": "Created by creator on September 27, 2025 at 08:00 PM",
  "collaboration_info": {
    "links_to_count": 0,
    "linked_from_count": 0,
    "tags_count": 2,
    "is_collaborative": false,
    "collaboration_score": 0.0
  },
  "tags": [],
  "linked_content": []
}
```

### Essays

#### List Essays
```http
GET /api/worlds/{world_id}/essays/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Query Parameters:**
- `search` (string): Search essays by title or content
- `topic` (string): Filter by topic
- `min_words` (integer): Minimum word count
- `max_words` (integer): Maximum word count

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "The Philosophy of Magic",
    "content": "Magic in this world operates on principles...",
    "abstract": "An exploration of magical philosophy",
    "topic": "Magic Theory",
    "thesis": "Magic is fundamentally about understanding natural forces",
    "word_count": 2500,
    "author": {
      "id": 1,
      "username": "creator"
    },
    "world": 1,
    "created_at": "2025-09-27T20:00:00Z",
    "attribution": "Created by creator on September 27, 2025 at 08:00 PM",
    "collaboration_info": {
      "links_to_count": 3,
      "linked_from_count": 1,
      "tags_count": 2,
      "is_collaborative": true,
      "collaboration_score": 6.5
    },
    "tags": [],
    "linked_content": []
  }
]
```

#### Create Essay
```http
POST /api/worlds/{world_id}/essays/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "string",
  "content": "string",
  "abstract": "string",
  "topic": "string",
  "thesis": "string",
  "tags": ["tag1", "tag2"]
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "string",
  "content": "string",
  "abstract": "string",
  "topic": "string",
  "thesis": "string",
  "word_count": 150,
  "author": {
    "id": 1,
    "username": "creator"
  },
  "world": 1,
  "created_at": "2025-09-27T20:00:00Z",
  "attribution": "Created by creator on September 27, 2025 at 08:00 PM",
  "collaboration_info": {
    "links_to_count": 0,
    "linked_from_count": 0,
    "tags_count": 2,
    "is_collaborative": false,
    "collaboration_score": 0.0
  },
  "tags": [],
  "linked_content": []
}
```

### Images

#### List Images
```http
GET /api/worlds/{world_id}/images/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Castle Illustration",
    "content": "An illustration of the main castle",
    "image_url": "http://localhost:8000/media/images/castle.jpg",
    "alt_text": "A majestic castle on a hill",
    "dimensions": "1920x1080",
    "file_size": 2048576,
    "author": {
      "id": 1,
      "username": "creator"
    },
    "world": 1,
    "created_at": "2025-09-27T20:00:00Z",
    "attribution": "Created by creator on September 27, 2025 at 08:00 PM",
    "collaboration_info": {
      "links_to_count": 0,
      "linked_from_count": 3,
      "tags_count": 1,
      "is_collaborative": true,
      "collaboration_score": 5.0
    },
    "tags": [],
    "linked_content": []
  }
]
```

#### Create Image
```http
POST /api/worlds/{world_id}/images/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
title: string
content: string
alt_text: string
image_file: file
tags: ["tag1", "tag2"] (JSON string)
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "string",
  "content": "string",
  "image_url": "http://localhost:8000/media/images/filename.jpg",
  "alt_text": "string",
  "dimensions": "1920x1080",
  "file_size": 2048576,
  "author": {
    "id": 1,
    "username": "creator"
  },
  "world": 1,
  "created_at": "2025-09-27T20:00:00Z",
  "attribution": "Created by creator on September 27, 2025 at 08:00 PM",
  "collaboration_info": {
    "links_to_count": 0,
    "linked_from_count": 0,
    "tags_count": 2,
    "is_collaborative": false,
    "collaboration_score": 0.0
  },
  "tags": [],
  "linked_content": []
}
```

## Tagging System

### List Tags
```http
GET /api/worlds/{world_id}/tags/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "magic",
    "world": 1,
    "usage_count": 5,
    "created_at": "2025-09-27T20:00:00Z"
  }
]
```

### Create Tag
```http
POST /api/worlds/{world_id}/tags/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "string"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "string",
  "world": 1,
  "usage_count": 0,
  "created_at": "2025-09-27T20:00:00Z"
}
```

### Get Tag Details
```http
GET /api/worlds/{world_id}/tags/{tag_name}/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "magic",
  "world": 1,
  "usage_count": 5,
  "created_at": "2025-09-27T20:00:00Z",
  "tagged_content": [
    {
      "id": 1,
      "title": "Magic System",
      "content_type": "page",
      "author": {
        "id": 1,
        "username": "creator"
      },
      "created_at": "2025-09-27T20:00:00Z"
    }
  ]
}
```

## Linking System

### List Links
```http
GET /api/worlds/{world_id}/links/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "from_content": {
      "id": 1,
      "title": "Magic System",
      "type": "page"
    },
    "to_content": {
      "id": 2,
      "title": "Fire Magic",
      "type": "page"
    },
    "created_at": "2025-09-27T20:00:00Z"
  }
]
```

### Create Link
```http
POST /api/worlds/{world_id}/links/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
Content-Type: application/json
```

**Request Body:**
```json
{
  "from_content_type": "page",
  "from_object_id": 1,
  "to_content_type": "character",
  "to_object_id": 5
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "from_content": {
    "id": 1,
    "title": "Magic System",
    "type": "page"
  },
  "to_content": {
    "id": 5,
    "title": "Wizard Character",
    "type": "character"
  },
  "created_at": "2025-09-27T20:00:00Z"
}
```

## Search and Discovery

### Search Content
```http
GET /api/worlds/{world_id}/search/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Query Parameters:**
- `q` (string): Search query
- `content_type` (string): Filter by content type
- `author` (string): Filter by author
- `tags` (string): Filter by tags (comma-separated)

**Response (200 OK):**
```json
{
  "query": "magic system",
  "total_results": 5,
  "results": [
    {
      "id": 1,
      "title": "Magic System Overview",
      "content_type": "page",
      "author": {
        "id": 1,
        "username": "creator"
      },
      "created_at": "2025-09-27T20:00:00Z",
      "excerpt": "The magic system in this world is based on...",
      "relevance_score": 0.95,
      "tags": ["magic", "system"]
    }
  ],
  "facets": {
    "content_types": {
      "page": 3,
      "character": 1,
      "story": 1
    },
    "authors": {
      "creator": 4,
      "collaborator": 1
    },
    "tags": {
      "magic": 5,
      "system": 3,
      "fantasy": 2
    }
  }
}
```

### Related Content
```http
GET /api/worlds/{world_id}/{content_type}s/{content_id}/related/
```

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response (200 OK):**
```json
{
  "content": {
    "id": 1,
    "title": "Magic System Overview",
    "type": "page"
  },
  "related_content": [
    {
      "id": 2,
      "title": "Fire Magic",
      "type": "page",
      "relationship": "direct_link",
      "relevance_score": 0.9
    },
    {
      "id": 3,
      "title": "Wizard Character",
      "type": "character",
      "relationship": "tag_similarity",
      "relevance_score": 0.7
    }
  ],
  "relationship_types": {
    "direct_link": 3,
    "tag_similarity": 2,
    "author_similarity": 1
  }
}
```

## Error Responses

### Standard Error Format

All API errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": ["Specific field error message"]
    },
    "timestamp": "2025-09-27T20:00:00Z",
    "request_id": "uuid-string"
  }
}
```

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **405 Method Not Allowed**: HTTP method not allowed (immutability)
- **409 Conflict**: Resource conflict (duplicate title, etc.)
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Validation Errors

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Content validation failed",
    "details": {
      "title": ["This field may not be blank."],
      "content": ["Content body must be at least 10 characters long."]
    },
    "timestamp": "2025-09-27T20:00:00Z",
    "request_id": "uuid-string"
  }
}
```

### Authentication Errors

```json
{
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Authentication credentials were not provided.",
    "details": {},
    "timestamp": "2025-09-27T20:00:00Z",
    "request_id": "uuid-string"
  }
}
```

### Permission Errors

```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You do not have permission to perform this action.",
    "details": {
      "required_permission": "world.change_world",
      "user_permissions": ["world.view_world"]
    },
    "timestamp": "2025-09-27T20:00:00Z",
    "request_id": "uuid-string"
  }
}
```

### Immutability Errors

```json
{
  "error": {
    "code": "IMMUTABILITY_VIOLATION",
    "message": "Content cannot be modified after creation due to immutability constraints.",
    "details": {
      "content_type": "page",
      "content_id": 1,
      "attempted_operation": "update"
    },
    "timestamp": "2025-09-27T20:00:00Z",
    "request_id": "uuid-string"
  }
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Unauthenticated users**: 100 requests per hour

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1632758400
```

## Pagination

List endpoints support pagination using cursor-based pagination:

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `page_size` (integer): Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/worlds/1/pages/?page=2",
  "previous": null,
  "results": []
}
```

## Versioning

The API uses URL versioning:

- Current version: `v1` (default)
- Future versions: `v2`, `v3`, etc.

**Example:**
```
GET /api/v1/worlds/
GET /api/v2/worlds/
```

## CORS

Cross-Origin Resource Sharing (CORS) is configured to allow requests from approved domains. For development, localhost origins are allowed.

## Content Types

The API supports these content types:

- **Request**: `application/json`, `multipart/form-data` (for file uploads)
- **Response**: `application/json`

## Timestamps

All timestamps are in ISO 8601 format with UTC timezone:

```
2025-09-27T20:00:00Z
```

## Field Validation

### Common Validation Rules

- **Title fields**: 3-300 characters, no leading/trailing whitespace
- **Content fields**: 10-10000 characters minimum
- **Tag names**: lowercase, hyphens allowed, no spaces or underscores
- **Usernames**: 3-150 characters, alphanumeric and underscores only
- **Email addresses**: Valid email format required

### Content-Specific Validation

- **Character full_name**: Required, 1-200 characters
- **Story main_characters**: Required list, at least one character
- **Essay abstract**: Optional, max 1000 characters
- **Image alt_text**: Required for accessibility, max 500 characters

## Immutability Rules

Content immutability is enforced at multiple levels:

1. **Model Level**: Content models prevent updates after creation
2. **API Level**: PUT/PATCH/DELETE methods return 405 Method Not Allowed
3. **Middleware Level**: Additional protection against modification attempts

**Exceptions:**
- Administrative force updates (with `force_update=True`)
- Relationship operations (tagging, linking) don't modify content directly

## Attribution System

All content includes comprehensive attribution information:

- **Primary Attribution**: Original author and creation timestamp
- **Collaboration Metrics**: Links, references, and collaboration scores
- **Attribution Strings**: Human-readable attribution text
- **Network Analysis**: Collaboration graphs and influence metrics

The attribution system ensures proper credit for all contributors while maintaining content immutability and fostering collaborative worldbuilding.