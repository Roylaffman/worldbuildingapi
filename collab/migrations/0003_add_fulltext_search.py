# Generated manually for full-text search optimization
from django.db import migrations, connection


def add_fulltext_search_indexes(apps, schema_editor):
    """Add full-text search indexes based on database backend."""
    db_vendor = connection.vendor
    
    if db_vendor == 'postgresql':
        # PostgreSQL full-text search indexes
        with connection.cursor() as cursor:
            # World full-text search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_world_fulltext 
                ON collab_world USING gin(to_tsvector('english', title || ' ' || description));
            """)
            
            # Page full-text search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_page_fulltext 
                ON collab_page USING gin(to_tsvector('english', title || ' ' || content || ' ' || COALESCE(summary, '')));
            """)
            
            # Essay full-text search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_essay_fulltext 
                ON collab_essay USING gin(to_tsvector('english', title || ' ' || content || ' ' || COALESCE(abstract, '')));
            """)
            
            # Character full-text search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_character_fulltext 
                ON collab_character USING gin(to_tsvector('english', 
                    title || ' ' || content || ' ' || full_name || ' ' || 
                    COALESCE(species, '') || ' ' || COALESCE(occupation, '') || ' ' || 
                    COALESCE(location, '') || ' ' || COALESCE(physical_description, '') || ' ' || 
                    COALESCE(background, '')
                ));
            """)
            
            # Story full-text search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_story_fulltext 
                ON collab_story USING gin(to_tsvector('english', 
                    title || ' ' || content || ' ' || COALESCE(genre, '') || ' ' || 
                    COALESCE(timeline_period, '') || ' ' || COALESCE(setting_location, '')
                ));
            """)
            
            # Image full-text search (title, content, caption, alt_text)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_image_fulltext 
                ON collab_image USING gin(to_tsvector('english', 
                    title || ' ' || content || ' ' || COALESCE(caption, '') || ' ' || alt_text
                ));
            """)
            
            # Tag name search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tag_name_fulltext 
                ON collab_tag USING gin(to_tsvector('english', name));
            """)
    
    elif db_vendor == 'sqlite':
        # SQLite FTS (Full-Text Search) virtual tables
        with connection.cursor() as cursor:
            # Note: SQLite FTS requires virtual tables, which are more complex
            # For now, we'll create basic text indexes that can be used for LIKE queries
            
            # World text search indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_world_title_search ON collab_world(title);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_world_description_search ON collab_world(description);")
            
            # Content text search indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_page_title_search ON collab_page(title);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_essay_title_search ON collab_essay(title);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_character_title_search ON collab_character(title);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_character_name_search ON collab_character(full_name);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_story_title_search ON collab_story(title);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_image_title_search ON collab_image(title);")
            
            # Tag name search
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tag_name_search ON collab_tag(name);")


def remove_fulltext_search_indexes(apps, schema_editor):
    """Remove full-text search indexes."""
    db_vendor = connection.vendor
    
    if db_vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("DROP INDEX IF EXISTS idx_world_fulltext;")
            cursor.execute("DROP INDEX IF EXISTS idx_page_fulltext;")
            cursor.execute("DROP INDEX IF EXISTS idx_essay_fulltext;")
            cursor.execute("DROP INDEX IF EXISTS idx_character_fulltext;")
            cursor.execute("DROP INDEX IF EXISTS idx_story_fulltext;")
            cursor.execute("DROP INDEX IF EXISTS idx_image_fulltext;")
            cursor.execute("DROP INDEX IF EXISTS idx_tag_name_fulltext;")
    
    elif db_vendor == 'sqlite':
        with connection.cursor() as cursor:
            cursor.execute("DROP INDEX IF EXISTS idx_world_title_search;")
            cursor.execute("DROP INDEX IF EXISTS idx_world_description_search;")
            cursor.execute("DROP INDEX IF EXISTS idx_page_title_search;")
            cursor.execute("DROP INDEX IF EXISTS idx_essay_title_search;")
            cursor.execute("DROP INDEX IF EXISTS idx_character_title_search;")
            cursor.execute("DROP INDEX IF EXISTS idx_character_name_search;")
            cursor.execute("DROP INDEX IF EXISTS idx_story_title_search;")
            cursor.execute("DROP INDEX IF EXISTS idx_image_title_search;")
            cursor.execute("DROP INDEX IF EXISTS idx_tag_name_search;")


class Migration(migrations.Migration):

    dependencies = [
        ('collab', '0002_add_database_indexes'),
    ]

    operations = [
        migrations.RunPython(
            add_fulltext_search_indexes,
            remove_fulltext_search_indexes
        ),
    ]