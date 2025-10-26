# Collaborative Worldbuilding Platform

A Django REST API platform for collaborative worldbuilding with immutable content, comprehensive attribution, and rich content relationships.

## 🌟 Features

- **Immutable Content Creation**: Pages, Essays, Characters, Stories, and Images that preserve attribution
- **Collaborative Attribution**: Comprehensive tracking and display of all contributions
- **Rich Content Relationships**: Bidirectional linking and flexible tagging systems
- **JWT Authentication**: Secure user registration, login, and token management
- **Chronological Timeline**: Time-based content exploration and filtering
- **Advanced Search**: Full-text search with filtering and faceted results
- **RESTful API**: Complete API with comprehensive documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Node.js 16+ (for frontend development)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/collaborative-worldbuilding.git
   cd collaborative-worldbuilding
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   ```bash
   # Create PostgreSQL database
   createdb worldbuilding_db
   
   # Copy environment settings
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## 📚 Documentation

- **[API Documentation](docs/api_documentation.md)** - Complete API reference
- **[Testing Guide](docs/testing_guide.md)** - Testing strategy and guidelines
- **[Frontend Setup](docs/frontend_setup.md)** - Frontend development guide
- **[Deployment Guide](docs/deployment_guide.md)** - Production deployment instructions

## 🧪 Testing

### Run Backend Tests
```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test collab
coverage report
coverage html

# Run specific test module
python manage.py test collab.test_models
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

### API Testing Scripts
```bash
# Test API endpoints
python test_api_endpoints.py

# Test tagging and linking
python test_tagging_linking.py

# Test URL routing
python test_urls.py
```

## 🏗️ Architecture

### Backend Stack
- **Django 4.2+** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL** - Primary database
- **JWT Authentication** - Token-based auth
- **Python 3.8+** - Programming language

### Frontend Stack
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing

### Key Design Principles
- **Immutable Content** - Ensures content integrity and proper attribution
- **Collaborative Attribution** - Tracks and displays all contributions
- **RESTful API** - Standard API design patterns
- **Component-Based UI** - Reusable and maintainable frontend components

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh

### World Management
- `GET /api/worlds/` - List worlds
- `POST /api/worlds/` - Create world
- `GET /api/worlds/{id}/` - World details
- `GET /api/worlds/{id}/contributors/` - World contributors
- `GET /api/worlds/{id}/timeline/` - Content timeline

### Content Management
- `GET/POST /api/worlds/{world_id}/pages/` - Page management
- `GET/POST /api/worlds/{world_id}/characters/` - Character management
- `GET/POST /api/worlds/{world_id}/stories/` - Story management
- `GET/POST /api/worlds/{world_id}/essays/` - Essay management
- `GET/POST /api/worlds/{world_id}/images/` - Image management

### Tagging & Linking
- `GET/POST /api/worlds/{world_id}/tags/` - Tag management
- `GET/POST /api/worlds/{world_id}/links/` - Link management

See [API Documentation](docs/api_documentation.md) for complete reference.

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Write tests** for your changes
4. **Commit your changes** (`git commit -m 'Add amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📈 Project Status

### ✅ Completed Features
- Core Django project structure
- Complete data models with immutability
- JWT authentication system
- RESTful API with DRF
- Comprehensive test suite (223 tests)
- Complete API documentation
- Tagging and linking systems
- Chronological viewing and filtering
- Attribution and collaboration tracking

### 🔄 In Progress
- React frontend implementation
- Advanced search and filtering UI
- Real-time collaboration features

### ⏳ Planned
- Mobile-responsive design
- Performance optimizations
- Deployment automation
- Advanced analytics dashboard

## 🐛 Known Issues

See [Test Report](docs/test_report.md) for detailed analysis of current issues and their priorities.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- React and TypeScript communities
- Contributors and testers

## 📞 Support

- **Documentation**: Check the [docs](docs/) directory
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

---

**Built with ❤️ for collaborative storytelling and worldbuilding**