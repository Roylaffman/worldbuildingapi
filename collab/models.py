from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default."""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def with_deleted(self):
        """Include soft-deleted objects in queryset."""
        return super().get_queryset()
    
    def deleted_only(self):
        """Return only soft-deleted objects."""
        return super().get_queryset().filter(is_deleted=True)


class SoftDeleteMixin(models.Model):
    """
    Mixin to add soft delete functionality.
    Objects are marked as deleted but not actually removed from database.
    """
    is_deleted = models.BooleanField(default=False, help_text="Soft delete flag")
    deleted_at = models.DateTimeField(null=True, blank=True, help_text="When this object was soft deleted")
    deleted_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name="%(class)s_deleted_set",
        help_text="User who soft deleted this object"
    )
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Manager that includes deleted objects
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None):
        """Soft delete this object."""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        # Allow soft delete even with immutability
        super().save(force_update=True)
    
    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        super().save(force_update=True)


class ImmutableModelMixin:
    """
    Mixin to enforce immutability on model instances after creation.
    Prevents modification and deletion of content to maintain chronological integrity.
    Allows soft deletion as a compromise.
    """
    def save(self, *args, **kwargs):
        # Allow soft delete operations and force updates
        if self.pk and not kwargs.get('force_update', False):
            # Check if this is just a soft delete operation
            if hasattr(self, 'is_deleted') and hasattr(self, '_state'):
                # Get the current state from database
                try:
                    current = self.__class__.all_objects.get(pk=self.pk)
                    # Allow if only soft delete fields are changing
                    if (self.is_deleted != current.is_deleted or 
                        self.deleted_at != current.deleted_at or
                        self.deleted_by != current.deleted_by):
                        super().save(*args, **kwargs)
                        return
                except self.__class__.DoesNotExist:
                    pass
            
            from .exceptions import ImmutabilityViolationError
            raise ImmutabilityViolationError(
                message=f"{self.__class__.__name__} content cannot be modified after creation",
                content_type=self.__class__.__name__.lower(),
                content_id=self.pk
            )
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # If this model supports soft delete, use that instead
        if hasattr(self, 'soft_delete'):
            user = kwargs.get('user')
            self.soft_delete(user=user)
            return
            
        from .exceptions import ImmutabilityViolationError
        raise ImmutabilityViolationError(
            message=f"{self.__class__.__name__} content cannot be deleted",
            content_type=self.__class__.__name__.lower(),
            content_id=self.pk
        )


class UserProfile(models.Model):
    """
    Extension of Django's User model for worldbuilding-specific features.
    Tracks user preferences and contribution statistics.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worldbuilding_profile')
    bio = models.TextField(blank=True, help_text="User's bio for worldbuilding community")
    preferred_content_types = models.JSONField(
        default=list, 
        help_text="List of preferred content types for this user"
    )
    contribution_count = models.PositiveIntegerField(
        default=0, 
        help_text="Total number of content contributions"
    )
    worlds_created = models.PositiveIntegerField(
        default=0, 
        help_text="Number of worlds created by this user"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Worldbuilding Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class World(models.Model):
    """
    Represents a collaborative worldbuilding space where users can contribute content.
    Each world acts as a container for related content entries.
    """
    title = models.CharField(
        max_length=200, 
        help_text="The name of the world"
    )
    description = models.TextField(
        help_text="Detailed description of the world's setting and theme"
    )
    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_worlds',
        help_text="The user who created this world"
    )
    is_public = models.BooleanField(
        default=True, 
        help_text="Whether this world is publicly visible"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this world was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this world's metadata was last updated"
    )

    def __str__(self):
        return self.title

    def clean(self):
        """Validate world data before saving."""
        if not self.title.strip():
            raise ValidationError("World title cannot be empty")
        if len(self.title.strip()) < 3:
            raise ValidationError("World title must be at least 3 characters long")

    def save(self, *args, **kwargs):
        """Override save to run validation and update creator's world count."""
        self.full_clean()
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update creator's world count if this is a new world
        if is_new:
            profile, created = UserProfile.objects.get_or_create(user=self.creator)
            profile.worlds_created += 1
            profile.save()

    def get_all_content_by_tag(self, tag_name):
        """
        Get all content across all types in this world that has a specific tag.
        Returns a dictionary with content type names as keys and QuerySets as values.
        """
        # Use Django's apps registry to get models dynamically
        from django.apps import apps
        
        content_models = {
            'pages': apps.get_model('collab', 'Page'),
            'essays': apps.get_model('collab', 'Essay'),
            'characters': apps.get_model('collab', 'Character'),
            'stories': apps.get_model('collab', 'Story'),
            'images': apps.get_model('collab', 'Image')
        }
        
        results = {}
        for type_name, model_class in content_models.items():
            results[type_name] = model_class.get_content_by_tag(self, tag_name)
        
        return results
    
    def get_all_content_by_tags(self, tag_names, match_all=False):
        """
        Get all content across all types in this world that has specific tags.
        Returns a dictionary with content type names as keys and QuerySets as values.
        """
        # Use Django's apps registry to get models dynamically
        from django.apps import apps
        
        content_models = {
            'pages': apps.get_model('collab', 'Page'),
            'essays': apps.get_model('collab', 'Essay'),
            'characters': apps.get_model('collab', 'Character'),
            'stories': apps.get_model('collab', 'Story'),
            'images': apps.get_model('collab', 'Image')
        }
        
        results = {}
        for type_name, model_class in content_models.items():
            results[type_name] = model_class.get_content_by_tags(self, tag_names, match_all)
        
        return results
    
    def get_content_timeline(self):
        """
        Get all content in this world ordered chronologically.
        Returns a list of content objects sorted by creation date.
        """
        # Use Django's apps registry to get models dynamically
        from django.apps import apps
        
        all_content = []
        
        # Get all content model classes
        content_model_names = ['Page', 'Essay', 'Character', 'Story', 'Image']
        
        for model_name in content_model_names:
            try:
                model_class = apps.get_model('collab', model_name)
                content_queryset = model_class.objects.filter(world=self)
                all_content.extend(list(content_queryset))
            except LookupError:
                # Model doesn't exist yet, skip it
                continue
        
        # Sort by creation date (newest first)
        all_content.sort(key=lambda x: x.created_at, reverse=True)
        
        return all_content
    
    def get_popular_tags(self, limit=10):
        """
        Get the most frequently used tags in this world.
        Returns a list of tuples: (tag, usage_count)
        """
        from django.db.models import Count
        
        tags_with_counts = Tag.objects.filter(world=self).annotate(
            usage_count=Count('content_tags')
        ).order_by('-usage_count')[:limit]
        
        return [(tag, tag.usage_count) for tag in tags_with_counts]

    class Meta:
        ordering = ['-created_at']
        verbose_name = "World"
        verbose_name_plural = "Worlds"


class ContentBase(SoftDeleteMixin, ImmutableModelMixin, models.Model):
    """
    Abstract base model for all content types in the worldbuilding system.
    Provides common fields and immutability enforcement.
    """
    title = models.CharField(
        max_length=300, 
        help_text="The title of this content entry"
    )
    content = models.TextField(
        help_text="The main content/body text"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='%(class)s_authored',
        help_text="The user who created this content"
    )
    world = models.ForeignKey(
        World, 
        on_delete=models.CASCADE, 
        related_name='%(class)s_entries',
        help_text="The world this content belongs to"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this content was created (immutable)"
    )

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    def clean(self):
        """Validate content data before saving."""
        from .exceptions import ContentValidationError
        
        # Title validation
        if not self.title or not self.title.strip():
            raise ContentValidationError(
                "Content title cannot be empty",
                field='title',
                code='required'
            )
        
        if len(self.title.strip()) < 3:
            raise ContentValidationError(
                "Content title must be at least 3 characters long",
                field='title',
                code='min_length'
            )
        
        if len(self.title.strip()) > 300:
            raise ContentValidationError(
                "Content title cannot exceed 300 characters",
                field='title',
                code='max_length'
            )
        
        # Content validation
        if not self.content or not self.content.strip():
            raise ContentValidationError(
                "Content body cannot be empty",
                field='content',
                code='required'
            )
        
        if len(self.content.strip()) < 10:
            raise ContentValidationError(
                "Content body must be at least 10 characters long",
                field='content',
                code='min_length'
            )
        
        # World and author validation
        if not self.world:
            raise ContentValidationError(
                "Content must be associated with a world",
                field='world',
                code='required'
            )
        
        if not self.author:
            raise ContentValidationError(
                "Content must have an author",
                field='author',
                code='required'
            )
        
        # Check for duplicate titles within the same world (optional constraint)
        if self.__class__.objects.filter(
            world=self.world,
            title__iexact=self.title.strip()
        ).exclude(pk=self.pk).exists():
            raise ContentValidationError(
                f"A {self.__class__.__name__.lower()} with this title already exists in this world",
                field='title',
                code='unique_within_world'
            )

    def save(self, *args, **kwargs):
        """Override save to run validation and update author's contribution count."""
        self.full_clean()
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update author's contribution count if this is new content
        if is_new:
            profile, created = UserProfile.objects.get_or_create(user=self.author)
            profile.contribution_count += 1
            profile.save()

    # Tag Management Methods
    
    def add_tag(self, tag_name):
        """
        Add a tag to this content. Creates the tag if it doesn't exist in the world.
        Returns the ContentTag instance.
        """
        tag_name = tag_name.strip().lower()
        if not tag_name:
            raise ValidationError("Tag name cannot be empty")
        
        # Get or create the tag for this world
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            world=self.world
        )
        
        # Create the content-tag relationship
        content_tag, created = ContentTag.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            tag=tag
        )
        
        return content_tag
    
    def remove_tag(self, tag_name):
        """
        Remove a tag from this content.
        Returns True if tag was removed, False if tag wasn't associated.
        """
        tag_name = tag_name.strip().lower()
        try:
            tag = Tag.objects.get(name=tag_name, world=self.world)
            content_tag = ContentTag.objects.get(
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.pk,
                tag=tag
            )
            content_tag.delete()
            return True
        except (Tag.DoesNotExist, ContentTag.DoesNotExist):
            return False
    
    def get_tags(self):
        """
        Get all tags associated with this content.
        Returns a QuerySet of Tag objects.
        """
        content_type = ContentType.objects.get_for_model(self)
        tag_ids = ContentTag.objects.filter(
            content_type=content_type,
            object_id=self.pk
        ).values_list('tag_id', flat=True)
        
        return Tag.objects.filter(id__in=tag_ids)
    
    def add_tags(self, tag_names):
        """
        Add multiple tags to this content.
        tag_names can be a list of strings or a comma-separated string.
        Returns a list of ContentTag instances.
        """
        if isinstance(tag_names, str):
            tag_names = [name.strip() for name in tag_names.split(',')]
        
        content_tags = []
        for tag_name in tag_names:
            if tag_name.strip():
                content_tags.append(self.add_tag(tag_name))
        
        return content_tags
    
    # Link Management Methods
    
    def link_to(self, target_content):
        """
        Create a bidirectional link to another content entry.
        Returns the ContentLink instance.
        """
        if target_content.world != self.world:
            raise ValidationError("Cannot link content from different worlds")
        
        # Create the forward link
        forward_link, created = ContentLink.objects.get_or_create(
            from_content_type=ContentType.objects.get_for_model(self),
            from_object_id=self.pk,
            to_content_type=ContentType.objects.get_for_model(target_content),
            to_object_id=target_content.pk
        )
        
        # Create the reverse link for bidirectionality
        reverse_link, created = ContentLink.objects.get_or_create(
            from_content_type=ContentType.objects.get_for_model(target_content),
            from_object_id=target_content.pk,
            to_content_type=ContentType.objects.get_for_model(self),
            to_object_id=self.pk
        )
        
        return forward_link
    
    def unlink_from(self, target_content):
        """
        Remove bidirectional link to another content entry.
        Returns True if links were removed, False if no links existed.
        """
        try:
            # Remove forward link
            forward_link = ContentLink.objects.get(
                from_content_type=ContentType.objects.get_for_model(self),
                from_object_id=self.pk,
                to_content_type=ContentType.objects.get_for_model(target_content),
                to_object_id=target_content.pk
            )
            forward_link.delete()
            
            # Remove reverse link
            reverse_link = ContentLink.objects.get(
                from_content_type=ContentType.objects.get_for_model(target_content),
                from_object_id=target_content.pk,
                to_content_type=ContentType.objects.get_for_model(self),
                to_object_id=self.pk
            )
            reverse_link.delete()
            
            return True
        except ContentLink.DoesNotExist:
            return False
    
    def get_linked_content(self):
        """
        Get all content entries linked to this content.
        Returns a list of content objects (mixed types).
        """
        content_type = ContentType.objects.get_for_model(self)
        
        # Get all outgoing links
        outgoing_links = ContentLink.objects.filter(
            from_content_type=content_type,
            from_object_id=self.pk
        )
        
        linked_content = []
        for link in outgoing_links:
            try:
                content_obj = link.to_content
                if content_obj:
                    linked_content.append(content_obj)
            except:
                # Handle cases where linked content might have been deleted
                continue
        
        return linked_content
    
    def get_content_linking_to_this(self):
        """
        Get all content entries that link to this content.
        Returns a list of content objects (mixed types).
        """
        content_type = ContentType.objects.get_for_model(self)
        
        # Get all incoming links
        incoming_links = ContentLink.objects.filter(
            to_content_type=content_type,
            to_object_id=self.pk
        )
        
        linking_content = []
        for link in incoming_links:
            try:
                content_obj = link.from_content
                if content_obj:
                    linking_content.append(content_obj)
            except:
                # Handle cases where linking content might have been deleted
                continue
        
        return linking_content
    
    @classmethod
    def get_content_by_tag(cls, world, tag_name):
        """
        Get all content of this type in a world that has a specific tag.
        Returns a QuerySet of content objects.
        """
        try:
            tag = Tag.objects.get(name=tag_name.strip().lower(), world=world)
            content_type = ContentType.objects.get_for_model(cls)
            
            content_ids = ContentTag.objects.filter(
                tag=tag,
                content_type=content_type
            ).values_list('object_id', flat=True)
            
            return cls.objects.filter(id__in=content_ids, world=world)
        except Tag.DoesNotExist:
            return cls.objects.none()
    
    @classmethod
    def get_content_by_tags(cls, world, tag_names, match_all=False):
        """
        Get all content of this type in a world that has specific tags.
        
        Args:
            world: The World instance
            tag_names: List of tag names or comma-separated string
            match_all: If True, content must have ALL tags. If False, content must have ANY tag.
        
        Returns a QuerySet of content objects.
        """
        if isinstance(tag_names, str):
            tag_names = [name.strip().lower() for name in tag_names.split(',')]
        else:
            tag_names = [name.strip().lower() for name in tag_names]
        
        tag_names = [name for name in tag_names if name]  # Remove empty strings
        
        if not tag_names:
            return cls.objects.none()
        
        tags = Tag.objects.filter(name__in=tag_names, world=world)
        content_type = ContentType.objects.get_for_model(cls)
        
        if match_all:
            # Content must have ALL specified tags
            content_ids = None
            for tag in tags:
                tag_content_ids = set(ContentTag.objects.filter(
                    tag=tag,
                    content_type=content_type
                ).values_list('object_id', flat=True))
                
                if content_ids is None:
                    content_ids = tag_content_ids
                else:
                    content_ids = content_ids.intersection(tag_content_ids)
            
            if content_ids:
                return cls.objects.filter(id__in=content_ids, world=world)
            else:
                return cls.objects.none()
        else:
            # Content must have ANY of the specified tags
            content_ids = ContentTag.objects.filter(
                tag__in=tags,
                content_type=content_type
            ).values_list('object_id', flat=True)
            
            return cls.objects.filter(id__in=content_ids, world=world).distinct()

    class Meta:
        abstract = True
        ordering = ['-created_at']


class Tag(models.Model):
    """
    Tags for categorizing and linking content within a world.
    Tags are scoped to individual worlds to prevent cross-contamination.
    """
    name = models.CharField(
        max_length=100,
        help_text="The tag name"
    )
    world = models.ForeignKey(
        World, 
        on_delete=models.CASCADE, 
        related_name='tags',
        help_text="The world this tag belongs to"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.world.title})"

    def clean(self):
        """Validate tag data before saving."""
        if not self.name.strip():
            raise ValidationError("Tag name cannot be empty")
        self.name = self.name.strip().lower()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_tagged_content(self):
        """
        Get all content entries that have this tag.
        Returns a list of content objects (mixed types).
        """
        content_tags = ContentTag.objects.filter(tag=self)
        tagged_content = []
        
        for content_tag in content_tags:
            try:
                content_obj = content_tag.content_object
                if content_obj:
                    tagged_content.append(content_obj)
            except:
                # Handle cases where content might have been deleted
                continue
        
        return tagged_content
    
    def get_usage_count(self):
        """
        Get the number of content entries that use this tag.
        """
        return ContentTag.objects.filter(tag=self).count()
    
    def get_content_by_type(self, content_type_name):
        """
        Get all content of a specific type that has this tag.
        
        Args:
            content_type_name: String name of the content type ('page', 'essay', etc.)
        
        Returns a QuerySet of content objects of the specified type.
        """
        from django.apps import apps
        
        try:
            # Capitalize the model name
            model_name = content_type_name.capitalize()
            model_class = apps.get_model('collab', model_name)
            content_type = ContentType.objects.get_for_model(model_class)
            
            content_ids = ContentTag.objects.filter(
                tag=self,
                content_type=content_type
            ).values_list('object_id', flat=True)
            
            return model_class.objects.filter(id__in=content_ids)
        except (LookupError, ContentType.DoesNotExist):
            # Model or content type doesn't exist
            return None

    class Meta:
        unique_together = ['name', 'world']
        ordering = ['name']
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class ContentTag(models.Model):
    """
    Many-to-many relationship between content and tags using generic foreign keys.
    Allows any content type to be tagged.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='content_tags')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tag.name} -> {self.content_object}"

    class Meta:
        unique_together = ['content_type', 'object_id', 'tag']
        verbose_name = "Content Tag"
        verbose_name_plural = "Content Tags"


class ContentLink(models.Model):
    """
    Bidirectional links between content entries.
    Allows content to reference and be referenced by other content.
    """
    from_content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        related_name='links_from'
    )
    from_object_id = models.PositiveIntegerField()
    from_content = GenericForeignKey('from_content_type', 'from_object_id')
    
    to_content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        related_name='links_to'
    )
    to_object_id = models.PositiveIntegerField()
    to_content = GenericForeignKey('to_content_type', 'to_object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_content} -> {self.to_content}"

    def clean(self):
        """Validate that content isn't linking to itself."""
        if (self.from_content_type == self.to_content_type and 
            self.from_object_id == self.to_object_id):
            raise ValidationError("Content cannot link to itself")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['from_content_type', 'from_object_id', 'to_content_type', 'to_object_id']
        verbose_name = "Content Link"
        verbose_name_plural = "Content Links"


# Specific Content Type Models

class Page(ContentBase):
    """
    Wiki-style entries for general worldbuilding information.
    Inherits immutability and common fields from ContentBase.
    """
    summary = models.CharField(
        max_length=500,
        blank=True,
        help_text="Brief summary of the page content"
    )
    
    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ['-created_at']


class Essay(ContentBase):
    """
    Long-form analytical content for in-depth worldbuilding exploration.
    Inherits immutability and common fields from ContentBase.
    """
    abstract = models.TextField(
        blank=True,
        help_text="Abstract or summary of the essay's main points"
    )
    word_count = models.PositiveIntegerField(
        default=0,
        help_text="Approximate word count of the essay content"
    )
    
    def save(self, *args, **kwargs):
        """Calculate word count before saving."""
        if self.content:
            self.word_count = len(self.content.split())
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Essay"
        verbose_name_plural = "Essays"
        ordering = ['-created_at']


class Character(ContentBase):
    """
    Character profiles with structured fields for worldbuilding.
    Inherits immutability and common fields from ContentBase.
    """
    full_name = models.CharField(
        max_length=200,
        help_text="Character's full name"
    )
    age = models.CharField(
        max_length=50,
        blank=True,
        help_text="Character's age (can be descriptive like 'ancient' or 'young adult')"
    )
    species = models.CharField(
        max_length=100,
        blank=True,
        help_text="Character's species or race"
    )
    occupation = models.CharField(
        max_length=200,
        blank=True,
        help_text="Character's job or role in the world"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Where the character is typically found"
    )
    personality_traits = models.JSONField(
        default=list,
        help_text="List of personality traits"
    )
    physical_description = models.TextField(
        blank=True,
        help_text="Detailed physical description of the character"
    )
    background = models.TextField(
        blank=True,
        help_text="Character's backstory and history"
    )
    relationships = models.JSONField(
        default=dict,
        help_text="Relationships with other characters (JSON format)"
    )
    
    def clean(self):
        """Validate character data before saving."""
        super().clean()
        if not self.full_name.strip():
            raise ValidationError("Character must have a full name")
    
    class Meta:
        verbose_name = "Character"
        verbose_name_plural = "Characters"
        ordering = ['-created_at']


class Story(ContentBase):
    """
    Narrative content with story-specific metadata.
    Inherits immutability and common fields from ContentBase.
    """
    genre = models.CharField(
        max_length=100,
        blank=True,
        help_text="Story genre (e.g., fantasy, sci-fi, mystery)"
    )
    story_type = models.CharField(
        max_length=50,
        choices=[
            ('short_story', 'Short Story'),
            ('novella', 'Novella'),
            ('chapter', 'Chapter'),
            ('vignette', 'Vignette'),
            ('legend', 'Legend'),
            ('myth', 'Myth'),
            ('historical_account', 'Historical Account'),
        ],
        default='short_story',
        help_text="Type of narrative content"
    )
    timeline_period = models.CharField(
        max_length=200,
        blank=True,
        help_text="When in the world's timeline this story takes place"
    )
    setting_location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Where in the world this story takes place"
    )
    main_characters = models.JSONField(
        default=list,
        help_text="List of main character names or references"
    )
    word_count = models.PositiveIntegerField(
        default=0,
        help_text="Approximate word count of the story"
    )
    is_canonical = models.BooleanField(
        default=True,
        help_text="Whether this story is considered canonical to the world"
    )
    
    def save(self, *args, **kwargs):
        """Calculate word count before saving."""
        if self.content:
            self.word_count = len(self.content.split())
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"
        ordering = ['-created_at']


class Image(ContentBase):
    """
    Visual content with file upload handling.
    Inherits immutability and common fields from ContentBase.
    """
    image_file = models.ImageField(
        upload_to='worldbuilding/images/%Y/%m/%d/',
        help_text="The uploaded image file"
    )
    caption = models.CharField(
        max_length=500,
        blank=True,
        help_text="Brief caption for the image"
    )
    alt_text = models.CharField(
        max_length=200,
        help_text="Alternative text for accessibility"
    )
    image_type = models.CharField(
        max_length=50,
        choices=[
            ('concept_art', 'Concept Art'),
            ('map', 'Map'),
            ('character_portrait', 'Character Portrait'),
            ('location_photo', 'Location Photo'),
            ('item_illustration', 'Item Illustration'),
            ('scene_illustration', 'Scene Illustration'),
            ('diagram', 'Diagram'),
            ('other', 'Other'),
        ],
        default='other',
        help_text="Type of image content"
    )
    dimensions = models.CharField(
        max_length=50,
        blank=True,
        help_text="Image dimensions (automatically populated)"
    )
    file_size = models.PositiveIntegerField(
        default=0,
        help_text="File size in bytes (automatically populated)"
    )
    
    def clean(self):
        """Validate image data before saving."""
        super().clean()
        from .exceptions import ContentValidationError, FileUploadError
        from .exceptions import validate_file_upload
        
        # Alt text validation for accessibility
        if not self.alt_text or not self.alt_text.strip():
            raise ContentValidationError(
                "Images must have alt text for accessibility",
                field='alt_text',
                code='required'
            )
        
        if len(self.alt_text.strip()) > 200:
            raise ContentValidationError(
                "Alt text cannot exceed 200 characters",
                field='alt_text',
                code='max_length'
            )
        
        # Caption validation
        if self.caption and len(self.caption.strip()) > 500:
            raise ContentValidationError(
                "Caption cannot exceed 500 characters",
                field='caption',
                code='max_length'
            )
        
        # Image file validation
        if self.image_file:
            try:
                # Define allowed image types
                allowed_types = [
                    'image/jpeg',
                    'image/png', 
                    'image/gif',
                    'image/webp',
                    'image/bmp',
                    'image/tiff'
                ]
                
                # Validate file upload (10MB max for images)
                validate_file_upload(
                    self.image_file,
                    max_size_mb=10,
                    allowed_types=allowed_types
                )
                
                # Additional image-specific validation
                if hasattr(self.image_file, 'content_type'):
                    # Check for potentially problematic image formats
                    if self.image_file.content_type == 'image/svg+xml':
                        raise FileUploadError(
                            "SVG files are not allowed for security reasons",
                            file_name=self.image_file.name,
                            file_type=self.image_file.content_type
                        )
                
                # Validate image dimensions if possible
                try:
                    from PIL import Image as PILImage
                    with PILImage.open(self.image_file) as img:
                        width, height = img.size
                        
                        # Check minimum dimensions
                        if width < 50 or height < 50:
                            raise FileUploadError(
                                f"Image dimensions ({width}x{height}) are too small. Minimum size is 50x50 pixels",
                                file_name=self.image_file.name
                            )
                        
                        # Check maximum dimensions
                        if width > 8000 or height > 8000:
                            raise FileUploadError(
                                f"Image dimensions ({width}x{height}) are too large. Maximum size is 8000x8000 pixels",
                                file_name=self.image_file.name
                            )
                        
                        # Check aspect ratio (prevent extremely wide or tall images)
                        aspect_ratio = max(width, height) / min(width, height)
                        if aspect_ratio > 10:
                            raise FileUploadError(
                                f"Image aspect ratio ({aspect_ratio:.1f}:1) is too extreme. Maximum ratio is 10:1",
                                file_name=self.image_file.name
                            )
                            
                except ImportError:
                    # PIL not available, skip dimension validation
                    pass
                except Exception as e:
                    raise FileUploadError(
                        f"Unable to process image file: {str(e)}",
                        file_name=self.image_file.name
                    )
                    
            except (FileUploadError, ContentValidationError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                raise FileUploadError(
                    f"Image file validation failed: {str(e)}",
                    file_name=getattr(self.image_file, 'name', 'unknown')
                )
    
    def save(self, *args, **kwargs):
        """Populate image metadata before saving."""
        if self.image_file:
            # Get file size
            self.file_size = self.image_file.size
            
            # Get dimensions if possible
            try:
                from PIL import Image as PILImage
                with PILImage.open(self.image_file) as img:
                    self.dimensions = f"{img.width}x{img.height}"
            except Exception:
                # If PIL is not available or image can't be processed
                self.dimensions = "Unknown"
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
        ordering = ['-created_at']
