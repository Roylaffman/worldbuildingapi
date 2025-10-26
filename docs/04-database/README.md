# 🗄️ Database Documentation

Database schema, operations, and migration guides for the Collaborative Worldbuilding Platform.

## 📋 Quick Navigation

### Schema Documentation
- [Schema Overview](schema/README.md) - Database structure overview
- [Table Documentation](schema/tables.md) - Detailed table descriptions
- [Migration Guide](schema/migrations.md) - Database migration procedures

### Database Operations
- [Database Inspection](operations/inspection.md) - Tools for database analysis
- [Soft Delete System](operations/soft-delete.md) - Soft delete implementation
- [Hard Delete Operations](operations/hard-delete.md) - Permanent deletion procedures
- [Database Cleanup](operations/cleanup.md) - Maintenance and cleanup tasks

### PostgreSQL Migration
- [PostgreSQL Migration Guide](postgres-migration/README.md) - Complete migration guide
- [PostgreSQL Setup](postgres-migration/setup.md) - PostgreSQL installation and setup
- [Migration Steps](postgres-migration/migration-steps.md) - Step-by-step migration process

### Analysis & Reports
- [Database Analysis Reports](analysis-reports.md) - Performance and usage analysis

## 🛠 Current Database Setup

### Development
- **Engine**: SQLite 3
- **Location**: `db.sqlite3` in project root
- **Advantages**: Zero configuration, file-based, good for development
- **Limitations**: Single-user, limited concurrency

### Production (Planned)
- **Engine**: PostgreSQL 13+
- **Advantages**: Multi-user, ACID compliance, advanced features
- **Features**: Full-text search, JSON support, advanced indexing

## 📊 Database Schema Overview

### Core Models
```
User (Django built-in)
├── UserProfile (1:1)
└── World (1:many)
    ├── Page (1:many)
    ├── Essay (1:many)
    ├── Character (1:many)
    ├── Story (1:many)
    ├── Image (1:many)
    ├── Tag (1:many)
    └── ContentLink (many:many through)
```

### Key Relationships
- **Users → Worlds**: One user can create multiple worlds
- **Worlds → Content**: Each world contains multiple content items
- **Content → Tags**: Many-to-many through ContentTag model
- **Content → Links**: Many-to-many through ContentLink model
- **Users → Content**: Each content item has an author

## 🔧 Database Operations

### Inspection Commands
```bash
# Inspect database structure
python manage.py inspect_db

# Analyze content distribution
python manage.py inspect_db --content-stats

# Check for orphaned records
python manage.py inspect_db --orphans
```

### Maintenance Commands
```bash
# Clean up old soft-deleted content
python manage.py cleanup_old_content --days=30

# Manage deleted content
python manage.py manage_deleted_content --list

# Hard delete specific content
python manage.py hard_delete_content --type=page --id=123
```

### Migration Commands
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Reverse migrations
python manage.py migrate collab 0001
```

## 📈 Performance Considerations

### Indexing Strategy
- **Primary Keys**: Automatic indexing on all primary keys
- **Foreign Keys**: Indexed for join performance
- **Search Fields**: Indexed on title, content fields
- **Tag Names**: Indexed for tag-based queries
- **Timestamps**: Indexed for chronological queries

### Query Optimization
- **Select Related**: Minimize database queries
- **Prefetch Related**: Efficient many-to-many loading
- **Database Functions**: Use database-level operations
- **Pagination**: Limit result sets for large tables

### Soft Delete Implementation
- **Deleted Flag**: `is_deleted` boolean field
- **Deletion Timestamp**: `deleted_at` datetime field
- **Manager Override**: Custom manager excludes deleted items
- **Cascade Handling**: Proper handling of related objects

## 🔄 Migration to PostgreSQL

### Why PostgreSQL?
- **Concurrency**: Multiple simultaneous users
- **Performance**: Better performance for complex queries
- **Features**: Advanced features like full-text search
- **Scalability**: Better scaling for production workloads
- **Reliability**: ACID compliance and data integrity

### Migration Process
1. **Setup PostgreSQL**: Install and configure PostgreSQL
2. **Update Settings**: Configure Django for PostgreSQL
3. **Data Migration**: Transfer existing data
4. **Testing**: Verify all functionality works
5. **Deployment**: Deploy with PostgreSQL backend

### Migration Timeline
- **Phase 1**: PostgreSQL setup and configuration (1 day)
- **Phase 2**: Data migration and testing (2 days)
- **Phase 3**: Production deployment (1 day)
- **Phase 4**: Monitoring and optimization (ongoing)

## 🧪 Testing Database Operations

### Test Data Creation
```bash
# Create test data
python manage.py loaddata fixtures/test_data.json

# Create sample worlds and content
python manage.py create_sample_data
```

### Performance Testing
```bash
# Test query performance
python manage.py test_query_performance

# Load testing
python manage.py load_test --users=100 --duration=300
```

## 🐛 Common Database Issues

### SQLite Limitations
- **Database Locked**: Restart development server
- **Concurrent Access**: Use PostgreSQL for multi-user scenarios
- **Large Datasets**: Performance degrades with large amounts of data

### Migration Issues
- **Conflicting Migrations**: Use `--merge` flag to resolve
- **Data Loss**: Always backup before major migrations
- **Dependency Issues**: Check migration dependencies

### Performance Issues
- **Slow Queries**: Add appropriate indexes
- **Memory Usage**: Optimize query patterns
- **Connection Limits**: Configure connection pooling

## 🔗 Related Documentation

- [Backend Models](../03-backend/models/README.md) - Django model documentation
- [API Documentation](../03-backend/api/README.md) - Database-backed APIs
- [Deployment](../05-deployment/README.md) - Production database setup
- [Testing](../06-testing/README.md) - Database testing strategies