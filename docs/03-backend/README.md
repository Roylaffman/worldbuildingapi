# ⚙️ Backend Documentation

Django REST Framework backend for the Collaborative Worldbuilding Platform.

## 📋 Quick Navigation

### API Documentation
- [API Overview](api/README.md) - REST API introduction
- [Authentication API](api/authentication.md) - User auth endpoints
- [Worlds API](api/worlds.md) - World management endpoints
- [Content API](api/content.md) - Content CRUD endpoints
- [Tagging API](api/tagging.md) - Tagging and linking endpoints
- [Complete API Reference](api/endpoints-reference.md) - All endpoints

### Data Models
- [Models Overview](models/README.md) - Django models introduction
- [Data Model Documentation](models/data-model.md) - Model structure
- [Model Relationships](models/relationships.md) - Inter-model relationships

### Testing
- [Testing Overview](testing/README.md) - Backend testing approach
- [Unit Tests](testing/unit-tests.md) - Model and view unit tests
- [Integration Tests](testing/integration-tests.md) - API integration tests
- [API Testing](testing/api-testing.md) - API endpoint testing

### Architecture
- [Backend Architecture](architecture.md) - System design and patterns

## 🛠 Technology Stack

- **Framework**: Django 4.2 with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT with Simple JWT
- **API Documentation**: DRF Spectacular (OpenAPI/Swagger)
- **Testing**: Django Test Framework + pytest
- **File Storage**: Local filesystem (development) / Cloud storage (production)

## 🏗 Architecture Overview

```
collab/                     # Main Django app
├── models.py              # Data models
├── serializers.py         # API serializers
├── views/                 # API views
│   ├── __init__.py
│   ├── world_views.py     # World management
│   ├── content_views.py   # Content CRUD
│   └── tagging_views.py   # Tagging & linking
├── permissions.py         # Custom permissions
├── validators.py          # Data validation
├── urls.py               # URL routing
├── tests.py              # Test cases
├── migrations/           # Database migrations
└── management/           # Custom management commands
    └── commands/
        ├── inspect_db.py
        ├── cleanup_old_content.py
        └── manage_deleted_content.py
```

## 🚀 Key Features

### Content Management
- **Multi-type Content**: Pages, essays, characters, stories, images
- **Soft Delete**: Content marked as deleted but preserved
- **Version Control**: Track content changes and history
- **File Upload**: Image upload with validation and storage
- **Rich Metadata**: Comprehensive content attributes

### Tagging & Linking System
- **Flexible Tagging**: Tag any content type with custom tags
- **Bidirectional Linking**: Create relationships between content
- **Tag-based Discovery**: Find content by tags
- **Link Navigation**: Navigate through content relationships
- **Usage Analytics**: Track tag and link usage

### User Management
- **JWT Authentication**: Secure token-based auth
- **User Profiles**: Extended user information
- **Permissions**: Role-based access control
- **Collaboration**: Multi-user content creation

### World Management
- **World Creation**: Users can create multiple worlds
- **World Sharing**: Public and private worlds
- **Contributor Management**: Manage world contributors
- **World Analytics**: Track world activity and statistics

## 📊 API Design Principles

### RESTful Design
- **Resource-based URLs**: `/api/v1/worlds/{id}/pages/`
- **HTTP Methods**: GET, POST, PUT, PATCH, DELETE
- **Status Codes**: Proper HTTP status code usage
- **Pagination**: Consistent pagination for list endpoints
- **Filtering**: Query parameter filtering and search

### Response Format
```json
{
  "count": 25,
  "next": "http://api/v1/worlds/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Handling
```json
{
  "timestamp": "2025-10-26T12:00:00Z",
  "path": "/api/v1/worlds/",
  "method": "POST",
  "api_version": "v1",
  "error": "Validation Error",
  "message": "Invalid data provided",
  "detail": {
    "title": ["This field is required."]
  },
  "suggestion": "Please provide a title for the world"
}
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Permission Classes**: Fine-grained access control
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: Django ORM protection
- **XSS Protection**: Built-in Django security
- **CSRF Protection**: Cross-site request forgery protection

## 📈 Performance Optimizations

- **Database Indexing**: Optimized database queries
- **Query Optimization**: Select/prefetch related objects
- **Caching**: Strategic caching for frequently accessed data
- **Pagination**: Efficient pagination for large datasets
- **Soft Delete**: Preserve data while maintaining performance

## 🧪 Testing Strategy

### Unit Tests
- **Model Tests**: Test model methods and validation
- **Serializer Tests**: Test data serialization/deserialization
- **View Tests**: Test API endpoint behavior
- **Permission Tests**: Test access control

### Integration Tests
- **API Workflow Tests**: Test complete user workflows
- **Authentication Tests**: Test auth integration
- **Multi-user Tests**: Test collaborative features
- **Performance Tests**: Test system under load

## 🔧 Development Commands

```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Database inspection
python manage.py inspect_db

# Content cleanup
python manage.py cleanup_old_content
```

## 🐛 Common Issues

- **Migration Conflicts**: Resolve with `--merge` flag
- **Permission Denied**: Check user permissions and authentication
- **Database Locks**: Restart development server
- **File Upload Issues**: Check media settings and permissions
- **API 500 Errors**: Check Django logs for detailed errors

## 🔗 Related Documentation

- [Frontend Integration](../02-frontend/implementation/api-integration.md)
- [Database Schema](../04-database/schema/README.md)
- [Deployment Guide](../05-deployment/README.md)
- [Testing Documentation](../06-testing/backend/README.md)