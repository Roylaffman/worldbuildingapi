# Documentation - Collaborative Worldbuilding Platform

## Overview

This directory contains comprehensive documentation for the Collaborative Worldbuilding Platform, including API documentation, testing guides, and development resources.

## Documentation Index

### 📚 Core Documentation

#### [API Documentation](api_documentation.md)
Complete API reference with endpoints, request/response formats, authentication, and examples.

**Contents:**
- Authentication endpoints (JWT)
- World management API
- Content creation and management (Pages, Characters, Stories, Essays, Images)
- Tagging and linking systems
- Search and discovery features
- Error handling and status codes
- Rate limiting and pagination

#### [Testing Guide](testing_guide.md)
Comprehensive guide to the testing strategy, test suite structure, and testing best practices.

**Contents:**
- Test suite organization and structure
- Running tests and generating coverage reports
- Test patterns and best practices
- Debugging and maintenance guidelines
- Contributing to the test suite

#### [Test Report](test_report.md)
Detailed analysis of current test suite performance, coverage, and recommendations.

**Contents:**
- Test execution results and metrics
- Issue analysis and prioritization
- Coverage analysis and gaps
- Performance metrics
- Recommendations for improvement

### 🚀 Getting Started

#### [Frontend Setup Guide](../frontend_setup.md)
Instructions for setting up and testing the frontend interface.

**Contents:**
- Quick start instructions
- Frontend test interface usage
- API endpoint testing
- Development notes and next steps

#### [Progress Summary](../PROGRESS_SUMMARY.md)
Complete overview of project status, completed features, and technical architecture.

**Contents:**
- Project overview and status
- Completed features checklist
- Technical architecture details
- API endpoints summary
- Known issues and next steps

### 🔧 Development Resources

#### Test Scripts
Standalone testing scripts for API validation:
- [`test_api_endpoints.py`](../test_api_endpoints.py) - Basic API functionality testing
- [`test_tagging_linking.py`](../test_tagging_linking.py) - Tagging and linking features
- [`test_urls.py`](../test_urls.py) - URL routing and availability testing

#### Frontend Testing
- [`simple_frontend_test.html`](../simple_frontend_test.html) - Browser-based API testing interface

## Quick Reference

### API Base URL
```
http://localhost:8000/api/
```

### Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Use token
curl -H "Authorization: Bearer your_jwt_token" \
  http://localhost:8000/api/worlds/
```

### Running Tests
```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test collab
coverage report
```

### Key Features

#### ✅ Implemented Features
- **JWT Authentication**: Complete user registration, login, and token management
- **World Management**: Create and manage collaborative worlds
- **Content Creation**: Immutable content types (Pages, Essays, Characters, Stories, Images)
- **Tagging System**: Flexible content organization and discovery
- **Linking System**: Bidirectional content relationships
- **Attribution System**: Comprehensive collaboration tracking and attribution
- **Chronological Viewing**: Timeline-based content exploration
- **Search & Discovery**: Full-text search and content filtering
- **Immutability Enforcement**: Content integrity and proper attribution

#### 🔄 In Progress
- **Comprehensive Testing**: 223 tests with 88.8% pass rate
- **Documentation**: Complete API and testing documentation

#### ⏳ Planned
- **Frontend Implementation**: User-friendly web interface
- **Performance Optimization**: Load testing and optimization
- **Deployment Configuration**: Production-ready setup

## Architecture Overview

### Backend Stack
- **Django 4.2+**: Web framework
- **Django REST Framework**: API framework
- **PostgreSQL**: Primary database
- **JWT Authentication**: Token-based authentication
- **Python 3.8+**: Programming language

### Key Design Principles
- **Immutable Content**: Ensures content integrity and proper attribution
- **Collaborative Attribution**: Tracks and displays all contributions
- **RESTful API**: Standard API design patterns
- **Comprehensive Testing**: High test coverage and quality assurance

### Database Design
- **Normalized Schema**: Proper relationships and constraints
- **Generic Foreign Keys**: Flexible content relationships
- **Full-text Search**: PostgreSQL search capabilities
- **Optimized Indexes**: Performance-optimized queries

## API Endpoints Summary

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh
- `GET /api/auth/user/` - User profile

### World Management
- `GET /api/worlds/` - List worlds
- `POST /api/worlds/` - Create world
- `GET /api/worlds/{id}/` - World details
- `GET /api/worlds/{id}/contributors/` - World contributors
- `GET /api/worlds/{id}/timeline/` - Content timeline
- `GET /api/worlds/{id}/attribution_report/` - Attribution analysis

### Content Management
- `GET/POST /api/worlds/{world_id}/pages/` - Page management
- `GET/POST /api/worlds/{world_id}/essays/` - Essay management
- `GET/POST /api/worlds/{world_id}/characters/` - Character management
- `GET/POST /api/worlds/{world_id}/stories/` - Story management
- `GET/POST /api/worlds/{world_id}/images/` - Image management

### Tagging & Linking
- `GET/POST /api/worlds/{world_id}/tags/` - Tag management
- `GET/POST /api/worlds/{world_id}/links/` - Link management
- `POST /api/worlds/{world_id}/{content_type}s/{id}/add-tags/` - Add tags
- `POST /api/worlds/{world_id}/{content_type}s/{id}/add-links/` - Add links

### Search & Discovery
- `GET /api/worlds/{world_id}/search/` - Content search
- `GET /api/worlds/{world_id}/{content_type}s/{id}/related/` - Related content

## Testing Overview

### Test Statistics
- **Total Tests**: 223
- **Pass Rate**: 88.8% (198 passing)
- **Test Categories**: 6 main test modules
- **Coverage Areas**: Models, Serializers, ViewSets, Authentication, Immutability, Integration

### Test Execution
```bash
# Basic test run
python manage.py test collab

# Verbose output
python manage.py test --verbosity=2

# Specific test module
python manage.py test collab.test_models

# With coverage
coverage run --source='.' manage.py test collab
coverage html
```

## Development Workflow

### Adding New Features
1. **Write Tests First**: Follow TDD principles
2. **Update Models**: Add/modify Django models
3. **Create Serializers**: Handle API data transformation
4. **Implement Views**: Create API endpoints
5. **Update URLs**: Configure routing
6. **Test Integration**: Ensure feature works end-to-end
7. **Update Documentation**: Keep docs current

### Code Quality Standards
- **Test Coverage**: Maintain >90% test coverage
- **Code Style**: Follow PEP 8 and Django conventions
- **Documentation**: Document all public APIs and complex logic
- **Security**: Follow Django security best practices
- **Performance**: Optimize database queries and API responses

## Troubleshooting

### Common Issues

#### Test Failures
- Check model validation requirements
- Ensure test data meets validation rules
- Use `format='json'` for complex API test data
- Verify authentication in protected endpoint tests

#### API Errors
- Check authentication headers
- Validate request data format
- Review error response details
- Ensure proper content types

#### Database Issues
- Run migrations: `python manage.py migrate`
- Check database connection settings
- Verify model constraints and relationships

### Getting Help

1. **Check Documentation**: Review relevant documentation sections
2. **Run Tests**: Use test suite to identify issues
3. **Check Logs**: Review Django and application logs
4. **Debug Mode**: Enable Django debug mode for development
5. **API Testing**: Use provided test scripts or frontend interface

## Contributing

### Documentation Updates
- Keep documentation current with code changes
- Follow existing documentation structure and style
- Include examples and practical usage information
- Update API documentation for endpoint changes

### Test Contributions
- Write tests for new features
- Maintain test quality and coverage
- Follow existing test patterns
- Update test documentation

### Code Contributions
- Follow established coding standards
- Include comprehensive tests
- Update relevant documentation
- Ensure backward compatibility

## Resources

### External Documentation
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Development Tools
- [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Postman](https://www.postman.com/) - API testing
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL management

---

*Last Updated: September 27, 2025*
*Documentation Version: 1.0*