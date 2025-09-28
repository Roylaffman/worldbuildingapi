# PostgreSQL Setup Guide

This guide explains how to configure PostgreSQL for the Collaborative Worldbuilding application.

## Development Setup

The application is configured to use SQLite by default for development cause its easy. To switch to PostgreSQL:

1. **Install PostgreSQL** on your system, I have done this
2. **Create a database** for the application:
   ```sql
   CREATE DATABASE worldbuilding;
   CREATE USER worldbuilding_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE worldbuilding TO worldbuilding_user;
   ```

3. **Set environment variables** in your `.env` file:
   ```env
   USE_POSTGRESQL=True
   DB_NAME=worldbuilding
   DB_USER=worldbuilding_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Install psycopg2** (PostgreSQL adapter):
   ```bash
   pip install psycopg2-binary
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

## Production Configuration

For production, ensure these PostgreSQL settings are optimized:

### Database Settings
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'worldbuilding_prod',
        'USER': 'worldbuilding_user',
        'PASSWORD': 'secure_password',
        'HOST': 'your_db_host',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'sslmode': 'require',  # For secure connections
        },
    }
}
```

### PostgreSQL Configuration
Add these settings to your `postgresql.conf`:

```conf
# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connection settings
max_connections = 100

# Performance settings
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_statement = 'all'
log_duration = on
log_min_duration_statement = 1000
```

## Database Optimizations Applied

The application includes several database optimizations:

### Indexes Created
- **World indexes**: Creator, public status, creation date
- **Content indexes**: World association, chronological ordering, author filtering
- **Tag indexes**: World-scoped tag names, content associations
- **Link indexes**: Bidirectional content relationships
- **Full-text search indexes**: Content search across all text fields

### Constraints (PostgreSQL only)
- **Data validation**: Non-empty titles and content
- **Numeric constraints**: Non-negative counts and file sizes
- **Referential integrity**: Foreign key relationships

### Performance Features
- **Connection pooling**: Reuse database connections
- **Query optimization**: Indexes for common query patterns
- **Full-text search**: PostgreSQL's native text search capabilities

## Monitoring and Maintenance

### Query Performance
Monitor slow queries using PostgreSQL's logging:
```sql
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

### Index Usage
Check index effectiveness:
```sql
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### Database Size
Monitor database growth:
```sql
SELECT pg_size_pretty(pg_database_size('worldbuilding')) as database_size;
```

## Backup and Recovery

### Regular Backups
```bash
# Full database backup
pg_dump -h localhost -U worldbuilding_user worldbuilding > backup.sql

# Compressed backup
pg_dump -h localhost -U worldbuilding_user worldbuilding | gzip > backup.sql.gz
```

### Restore from Backup
```bash
# Restore from backup
psql -h localhost -U worldbuilding_user worldbuilding < backup.sql
```

## Troubleshooting

### Common Issues

1. **Connection refused**: Check PostgreSQL service is running
2. **Authentication failed**: Verify user credentials and pg_hba.conf
3. **Slow queries**: Check if indexes are being used with EXPLAIN ANALYZE
4. **Disk space**: Monitor database size and implement log rotation

### Performance Tuning

1. **Analyze query patterns** using pg_stat_statements
2. **Update table statistics** regularly with ANALYZE
3. **Vacuum tables** to reclaim space and update statistics
4. **Monitor connection usage** and adjust max_connections if needed