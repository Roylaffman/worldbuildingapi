# Generated manually for database constraints and integrity
from django.db import migrations, connection


def add_database_constraints(apps, schema_editor):
    """Add database constraints based on database backend."""
    db_vendor = connection.vendor
    
    if db_vendor == 'postgresql':
        # PostgreSQL supports named constraints with ALTER TABLE ADD CONSTRAINT
        with connection.cursor() as cursor:
            # World constraints
            cursor.execute("ALTER TABLE collab_world ADD CONSTRAINT check_world_title_not_empty CHECK (LENGTH(TRIM(title)) > 0);")
            cursor.execute("ALTER TABLE collab_world ADD CONSTRAINT check_world_title_min_length CHECK (LENGTH(TRIM(title)) >= 3);")
            
            # Content constraints
            cursor.execute("ALTER TABLE collab_page ADD CONSTRAINT check_page_title_not_empty CHECK (LENGTH(TRIM(title)) > 0);")
            cursor.execute("ALTER TABLE collab_page ADD CONSTRAINT check_page_content_not_empty CHECK (LENGTH(TRIM(content)) > 0);")
            
            cursor.execute("ALTER TABLE collab_essay ADD CONSTRAINT check_essay_title_not_empty CHECK (LENGTH(TRIM(title)) > 0);")
            cursor.execute("ALTER TABLE collab_essay ADD CONSTRAINT check_essay_content_not_empty CHECK (LENGTH(TRIM(content)) > 0);")
            cursor.execute("ALTER TABLE collab_essay ADD CONSTRAINT check_essay_word_count_non_negative CHECK (word_count >= 0);")
            
            cursor.execute("ALTER TABLE collab_character ADD CONSTRAINT check_character_title_not_empty CHECK (LENGTH(TRIM(title)) > 0);")
            cursor.execute("ALTER TABLE collab_character ADD CONSTRAINT check_character_full_name_not_empty CHECK (LENGTH(TRIM(full_name)) > 0);")
            
            cursor.execute("ALTER TABLE collab_story ADD CONSTRAINT check_story_title_not_empty CHECK (LENGTH(TRIM(title)) > 0);")
            cursor.execute("ALTER TABLE collab_story ADD CONSTRAINT check_story_content_not_empty CHECK (LENGTH(TRIM(content)) > 0);")
            cursor.execute("ALTER TABLE collab_story ADD CONSTRAINT check_story_word_count_non_negative CHECK (word_count >= 0);")
            
            cursor.execute("ALTER TABLE collab_image ADD CONSTRAINT check_image_title_not_empty CHECK (LENGTH(TRIM(title)) > 0);")
            cursor.execute("ALTER TABLE collab_image ADD CONSTRAINT check_image_alt_text_not_empty CHECK (LENGTH(TRIM(alt_text)) > 0);")
            cursor.execute("ALTER TABLE collab_image ADD CONSTRAINT check_image_file_size_non_negative CHECK (file_size >= 0);")
            
            # Tag constraints
            cursor.execute("ALTER TABLE collab_tag ADD CONSTRAINT check_tag_name_not_empty CHECK (LENGTH(TRIM(name)) > 0);")
            
            # User profile constraints
            cursor.execute("ALTER TABLE collab_userprofile ADD CONSTRAINT check_contribution_count_non_negative CHECK (contribution_count >= 0);")
            cursor.execute("ALTER TABLE collab_userprofile ADD CONSTRAINT check_worlds_created_non_negative CHECK (worlds_created >= 0);")
    
    elif db_vendor == 'sqlite':
        # SQLite has limited support for adding constraints after table creation
        # We'll rely on model-level validation instead of database constraints
        # This is acceptable since Django's model validation will catch these issues
        pass


def remove_database_constraints(apps, schema_editor):
    """Remove database constraints."""
    db_vendor = connection.vendor
    
    if db_vendor == 'postgresql':
        with connection.cursor() as cursor:
            # Drop all constraints (PostgreSQL)
            cursor.execute("ALTER TABLE collab_world DROP CONSTRAINT IF EXISTS check_world_title_not_empty;")
            cursor.execute("ALTER TABLE collab_world DROP CONSTRAINT IF EXISTS check_world_title_min_length;")
            
            cursor.execute("ALTER TABLE collab_page DROP CONSTRAINT IF EXISTS check_page_title_not_empty;")
            cursor.execute("ALTER TABLE collab_page DROP CONSTRAINT IF EXISTS check_page_content_not_empty;")
            
            cursor.execute("ALTER TABLE collab_essay DROP CONSTRAINT IF EXISTS check_essay_title_not_empty;")
            cursor.execute("ALTER TABLE collab_essay DROP CONSTRAINT IF EXISTS check_essay_content_not_empty;")
            cursor.execute("ALTER TABLE collab_essay DROP CONSTRAINT IF EXISTS check_essay_word_count_non_negative;")
            
            cursor.execute("ALTER TABLE collab_character DROP CONSTRAINT IF EXISTS check_character_title_not_empty;")
            cursor.execute("ALTER TABLE collab_character DROP CONSTRAINT IF EXISTS check_character_full_name_not_empty;")
            
            cursor.execute("ALTER TABLE collab_story DROP CONSTRAINT IF EXISTS check_story_title_not_empty;")
            cursor.execute("ALTER TABLE collab_story DROP CONSTRAINT IF EXISTS check_story_content_not_empty;")
            cursor.execute("ALTER TABLE collab_story DROP CONSTRAINT IF EXISTS check_story_word_count_non_negative;")
            
            cursor.execute("ALTER TABLE collab_image DROP CONSTRAINT IF EXISTS check_image_title_not_empty;")
            cursor.execute("ALTER TABLE collab_image DROP CONSTRAINT IF EXISTS check_image_alt_text_not_empty;")
            cursor.execute("ALTER TABLE collab_image DROP CONSTRAINT IF EXISTS check_image_file_size_non_negative;")
            
            cursor.execute("ALTER TABLE collab_tag DROP CONSTRAINT IF EXISTS check_tag_name_not_empty;")
            
            cursor.execute("ALTER TABLE collab_userprofile DROP CONSTRAINT IF EXISTS check_contribution_count_non_negative;")
            cursor.execute("ALTER TABLE collab_userprofile DROP CONSTRAINT IF EXISTS check_worlds_created_non_negative;")


class Migration(migrations.Migration):

    dependencies = [
        ('collab', '0003_add_fulltext_search'),
    ]

    operations = [
        migrations.RunPython(
            add_database_constraints,
            remove_database_constraints
        ),
    ]