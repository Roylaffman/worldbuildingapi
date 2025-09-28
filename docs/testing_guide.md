# Testing Guide for Collaborative Worldbuilding Platform

## Overview

This document provides comprehensive information about the testing strategy, test suite structure, and how to run and maintain tests for the collaborative worldbuilding platform.

## Test Suite Structure

### Test Organization

The test suite is organized into several focused test modules:

#### Core Test Files

1. **`collab/tests.py`** - Main test file with comprehensive API and integration tests
2. **`collab/test_models.py`** - Model validation and business logic tests
3. **`collab/test_serializers.py`** - Serializer validation and data transformation tests
4. **`collab/test_viewsets.py`** - API endpoint and ViewSet functionality tests
5. **`collab/test_auth_permissions.py`** - Authentication and permission system tests
6. **`collab/test_immutability.py`** - Immutability enforcement tests
7. **`collab/test_unit_comprehensive.py`** - Comprehensive unit tests covering all aspects

#### Standalone Test Scripts

1. **`test_api_endpoints.py`** - Standalone API endpoint testing script
2. **`test_tagging_linking.py`** - Tagging and linking functionality testing script
3. **`test_urls.py`** - URL routing and endpoint availability testing script

### Test Categories

#### 1. Model Tests
- **Purpose**: Test model validation, constraints, and business logic
- **Coverage**: All models (World, Page, Essay, Character, Story, Image, Tag, UserProfile)
- **Key Areas**:
  - Field validation
  - Model constraints
  - Custom model methods
  - Relationship handling
  - Immutability enforcement

#### 2. Serializer Tests
- **Purpose**: Test data serialization, validation, and transformation
- **Coverage**: All serializers for models and authentication
- **Key Areas**:
  - Data validation
  - Field transformation
  - Read-only field enforcement
  - Custom serializer methods
  - Context handling

#### 3. ViewSet/API Tests
- **Purpose**: Test API endpoints, permissions, and HTTP responses
- **Coverage**: All API endpoints and ViewSets
- **Key Areas**:
  - CRUD operations
  - Authentication requirements
  - Permission enforcement
  - Error handling
  - Response formatting

#### 4. Authentication & Permission Tests
- **Purpose**: Test security, authentication, and authorization
- **Coverage**: JWT authentication, custom permissions, security features
- **Key Areas**:
  - User registration and login
  - Token management
  - Permission classes
  - Security vulnerabilities
  - Access control

#### 5. Immutability Tests
- **Purpose**: Test content immutability enforcement
- **Coverage**: All content types and immutability mechanisms
- **Key Areas**:
  - Model-level immutability
  - API-level immutability
  - Force update bypass
  - Error handling

#### 6. Integration Tests
- **Purpose**: Test complete workflows and feature interactions
- **Coverage**: End-to-end scenarios and complex workflows
- **Key Areas**:
  - Content creation workflows
  - Tagging and linking
  - Collaboration features
  - Chronological viewing

## Running Tests

### Basic Test Execution

```bash
# Run all tests
python manage.py test

# Run tests with verbose output
python manage.py test --verbosity=2

# Run specific test module
python manage.py test collab.test_models

# Run specific test class
python manage.py test collab.test_models.WorldModelTest

# Run specific test method
python manage.py test collab.test_models.WorldModelTest.test_world_creation
```

### Test Coverage

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test collab

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

### Standalone Test Scripts

```bash
# Test API endpoints (requires running server)
python test_api_endpoints.py

# Test tagging and linking
python test_tagging_linking.py

# Test URL routing
python test_urls.py
```

## Test Data and Fixtures

### Test Data Creation

Tests use Django's built-in test database and create test data in `setUp()` methods:

```python
def setUp(self):
    """Set up test data."""
    self.user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    self.world = World.objects.create(
        title='Test World',
        description='A test world',
        creator=self.user
    )
```

### Test Database

- Tests use an in-memory SQLite database by default
- Database is created and destroyed for each test run
- Transactions are rolled back after each test

## Test Patterns and Best Practices

### Test Structure

Each test follows the Arrange-Act-Assert pattern:

```python
def test_example(self):
    """Test description."""
    # Arrange - Set up test data
    user = User.objects.create_user(username='test', email='test@example.com')
    
    # Act - Perform the action being tested
    world = World.objects.create(title='Test', creator=user)
    
    # Assert - Verify the results
    self.assertEqual(world.title, 'Test')
    self.assertEqual(world.creator, user)
```

### API Testing Patterns

```python
def test_api_endpoint(self):
    """Test API endpoint functionality."""
    # Authenticate
    self.client.force_authenticate(user=self.user)
    
    # Make request
    response = self.client.post('/api/endpoint/', data)
    
    # Assert response
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data['field'], 'expected_value')
```

### Error Testing Patterns

```python
def test_validation_error(self):
    """Test validation error handling."""
    with self.assertRaises(ValidationError):
        invalid_object = Model(invalid_field='')
        invalid_object.full_clean()
```

## Test Configuration

### Settings

Tests use the default Django test settings with these key configurations:

- **Database**: In-memory SQLite
- **Authentication**: JWT tokens
- **Time Zone**: UTC
- **Debug**: False during testing

### Environment Variables

Test-specific environment variables can be set in test settings:

```python
# In test settings
TESTING = True
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

## Continuous Integration

### GitHub Actions (Example)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python manage.py test --verbosity=2
```

## Test Maintenance

### Adding New Tests

When adding new features:

1. **Model Tests**: Add tests for new models or model changes
2. **Serializer Tests**: Add tests for new serializers or validation rules
3. **API Tests**: Add tests for new endpoints or API changes
4. **Integration Tests**: Add tests for new workflows or feature interactions

### Test Data Management

- Keep test data minimal and focused
- Use factories for complex object creation
- Clean up test data in `tearDown()` if needed
- Avoid dependencies between tests

### Performance Considerations

- Use `setUpClass()` for expensive setup operations
- Mock external services and APIs
- Use database transactions for faster test execution
- Profile slow tests and optimize as needed

## Debugging Tests

### Common Issues

1. **Test Isolation**: Ensure tests don't depend on each other
2. **Database State**: Check for data leakage between tests
3. **Time Dependencies**: Use fixed dates/times in tests
4. **External Dependencies**: Mock external services

### Debugging Tools

```python
# Add debugging output
import pdb; pdb.set_trace()

# Print test data
print(f"Response data: {response.data}")

# Check database state
print(f"Object count: {Model.objects.count()}")
```

## Test Metrics

### Current Test Statistics

- **Total Tests**: 223
- **Test Files**: 7 main test files + 3 standalone scripts
- **Coverage Areas**:
  - Models: 100% of models tested
  - Serializers: 100% of serializers tested
  - ViewSets: 100% of endpoints tested
  - Authentication: Complete JWT and permission testing
  - Immutability: Complete immutability enforcement testing

### Test Categories Breakdown

- **Model Tests**: 45 tests
- **Serializer Tests**: 38 tests
- **ViewSet Tests**: 52 tests
- **Authentication Tests**: 28 tests
- **Immutability Tests**: 25 tests
- **Integration Tests**: 35 tests

## Known Issues and Limitations

### Current Test Issues

1. **Character/Story Validation**: Some tests fail due to required field validation
2. **API Format Issues**: Some tests need JSON format specification
3. **Time Zone Warnings**: Naive datetime warnings in some tests

### Planned Improvements

1. Fix validation issues in character and story tests
2. Add more edge case testing
3. Improve test data factories
4. Add performance testing
5. Enhance error message testing

## Contributing to Tests

### Guidelines

1. **Write Tests First**: Follow TDD principles
2. **Test Edge Cases**: Include boundary conditions and error cases
3. **Use Descriptive Names**: Test names should clearly describe what's being tested
4. **Keep Tests Simple**: One assertion per test when possible
5. **Document Complex Tests**: Add comments for complex test logic

### Code Review Checklist

- [ ] Tests cover new functionality
- [ ] Tests include error cases
- [ ] Tests are isolated and independent
- [ ] Test names are descriptive
- [ ] Test data is minimal and relevant
- [ ] No hardcoded values that could break
- [ ] Proper assertions are used

## Resources

### Django Testing Documentation
- [Django Testing Overview](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django Test Client](https://docs.djangoproject.com/en/stable/topics/testing/tools/#the-test-client)

### Django REST Framework Testing
- [DRF Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [DRF Test Client](https://www.django-rest-framework.org/api-guide/testing/#apiclient)

### Testing Best Practices
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Test-Driven Development](https://testdriven.io/)