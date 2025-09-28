# Generated manually for database optimization
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collab', '0001_initial'),
    ]

    operations = [
        # Add indexes for frequently queried fields
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_world_creator_public ON collab_world(creator_id, is_public);",
            reverse_sql="DROP INDEX IF EXISTS idx_world_creator_public;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_world_created_at ON collab_world(created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_world_created_at;"
        ),
        
        # Content indexes for chronological ordering and world filtering
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_page_world_created ON collab_page(world_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_page_world_created;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_essay_world_created ON collab_essay(world_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_essay_world_created;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_character_world_created ON collab_character(world_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_character_world_created;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_story_world_created ON collab_story(world_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_story_world_created;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_image_world_created ON collab_image(world_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_image_world_created;"
        ),
        
        # Author indexes for content filtering
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_page_author ON collab_page(author_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_page_author;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_essay_author ON collab_essay(author_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_essay_author;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_character_author ON collab_character(author_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_character_author;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_story_author ON collab_story(author_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_story_author;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_image_author ON collab_image(author_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_image_author;"
        ),
        
        # Tag system indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_tag_world_name ON collab_tag(world_id, name);",
            reverse_sql="DROP INDEX IF EXISTS idx_tag_world_name;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_contenttag_tag ON collab_contenttag(tag_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_contenttag_tag;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_contenttag_content ON collab_contenttag(content_type_id, object_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_contenttag_content;"
        ),
        
        # Content linking indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_contentlink_from ON collab_contentlink(from_content_type_id, from_object_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_contentlink_from;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_contentlink_to ON collab_contentlink(to_content_type_id, to_object_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_contentlink_to;"
        ),
        
        # User profile indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_userprofile_contribution_count ON collab_userprofile(contribution_count DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_userprofile_contribution_count;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_userprofile_worlds_created ON collab_userprofile(worlds_created DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_userprofile_worlds_created;"
        ),
    ]