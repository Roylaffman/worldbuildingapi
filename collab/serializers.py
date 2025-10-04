"""
Serializers for the collaborative worldbuilding application.
Handles data validation and serialization for API endpoints.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.contenttypes.models import ContentType
from .models import (
    UserProfile, World, Tag, ContentTag, ContentLink,
    Page, Essay, Character, Story, Image
)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with password validation.
    Creates both User and UserProfile instances.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    bio = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
        help_text="Optional bio for your worldbuilding profile"
    )
    preferred_content_types = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True,
        help_text="List of preferred content types (page, essay, character, story, image)"
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'bio', 'preferred_content_types'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate_username(self, value):
        """Validate username is unique and meets requirements."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("Username can only contain letters, numbers, hyphens, and underscores.")
        
        return value

    def validate_email(self, value):
        """Validate email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate_password(self, value):
        """Validate password using Django's password validators."""
        try:
            # Create a temporary user instance for validation
            temp_user = User(
                username=self.initial_data.get('username', ''),
                email=self.initial_data.get('email', ''),
                first_name=self.initial_data.get('first_name', ''),
                last_name=self.initial_data.get('last_name', '')
            )
            validate_password(value, user=temp_user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_preferred_content_types(self, value):
        """Validate preferred content types are valid."""
        valid_types = ['page', 'essay', 'character', 'story', 'image']
        for content_type in value:
            if content_type not in valid_types:
                raise serializers.ValidationError(
                    f"'{content_type}' is not a valid content type. "
                    f"Valid types are: {', '.join(valid_types)}"
                )
        return value

    def validate(self, attrs):
        """Validate password confirmation matches."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Password confirmation does not match password."
            })
        return attrs

    def create(self, validated_data):
        """Create user and associated profile."""
        # Remove fields that don't belong to User model
        bio = validated_data.pop('bio', '')
        preferred_content_types = validated_data.pop('preferred_content_types', [])
        password_confirm = validated_data.pop('password_confirm')
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            bio=bio,
            preferred_content_types=preferred_content_types
        )
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    Read-only serializer for displaying user stats and preferences.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'first_name', 'last_name', 'date_joined',
            'bio', 'preferred_content_types', 'contribution_count', 
            'worlds_created', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'contribution_count', 'worlds_created', 'created_at', 'updated_at'
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for displaying user information in content.
    Used for author attribution and user references.
    """
    profile = UserProfileSerializer(source='worldbuilding_profile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'date_joined', 'profile']
        read_only_fields = ['id', 'username', 'date_joined']


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    Requires current password for security.
    """
    current_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_current_password(self, value):
        """Validate current password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        """Validate new password using Django's password validators."""
        try:
            validate_password(value, user=self.context['request'].user)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, attrs):
        """Validate new password confirmation matches."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "New password confirmation doesn't match new password."
            })
        return attrs

    def save(self):
        """Change the user's password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class WorldSerializer(serializers.ModelSerializer):
    """
    Serializer for the World model.
    Handles CRUD operations for worlds and displays related information.
    Enhanced with collaborative features and contribution tracking.
    """
    creator = UserSerializer(read_only=True)
    content_counts = serializers.SerializerMethodField()
    contributor_count = serializers.SerializerMethodField()
    collaboration_stats = serializers.SerializerMethodField()
    top_contributors = serializers.SerializerMethodField()

    class Meta:
        model = World
        fields = [
            'id', 'title', 'description', 'creator', 'is_public',
            'created_at', 'updated_at', 'content_counts', 'contributor_count',
            'collaboration_stats', 'top_contributors'
        ]
        read_only_fields = [
            'creator', 'created_at', 'updated_at', 'content_counts', 
            'contributor_count', 'collaboration_stats', 'top_contributors'
        ]

    def get_content_counts(self, obj):
        """Calculate counts of different content types within the world."""
        return {
            'pages': obj.page_entries.count(),
            'essays': obj.essay_entries.count(),
            'characters': obj.character_entries.count(),
            'stories': obj.story_entries.count(),
            'images': obj.image_entries.count(),
        }

    def get_contributor_count(self, obj):
        """Get the number of unique contributors to this world."""
        from django.contrib.auth.models import User
        from django.db.models import Q
        
        return User.objects.filter(
            Q(page_authored__world=obj) |
            Q(essay_authored__world=obj) |
            Q(character_authored__world=obj) |
            Q(story_authored__world=obj) |
            Q(image_authored__world=obj)
        ).distinct().count()

    def get_collaboration_stats(self, obj):
        """Get detailed collaboration statistics for this world."""
        from django.db.models import Count, Q
        from django.contrib.auth.models import User
        
        # Get total content links within this world
        total_links = ContentLink.objects.filter(
            from_content_type__in=[
                ContentType.objects.get_for_model(Page),
                ContentType.objects.get_for_model(Essay),
                ContentType.objects.get_for_model(Character),
                ContentType.objects.get_for_model(Story),
                ContentType.objects.get_for_model(Image)
            ]
        ).count()
        
        # Get cross-author collaborations (content linking between different authors)
        cross_author_links = 0
        all_links = ContentLink.objects.all()
        for link in all_links:
            try:
                if (link.from_content and link.to_content and 
                    hasattr(link.from_content, 'world') and hasattr(link.to_content, 'world') and
                    link.from_content.world == obj and link.to_content.world == obj and
                    hasattr(link.from_content, 'author') and hasattr(link.to_content, 'author') and
                    link.from_content.author != link.to_content.author):
                    cross_author_links += 1
            except:
                continue
        
        # Get total tags used
        total_tags = obj.tags.count()
        
        # Get average content per contributor
        contributor_count = self.get_contributor_count(obj)
        total_content = sum(self.get_content_counts(obj).values())
        avg_content_per_contributor = total_content / contributor_count if contributor_count > 0 else 0
        
        return {
            'total_content_links': total_links,
            'cross_author_collaborations': cross_author_links,
            'total_tags_used': total_tags,
            'average_content_per_contributor': round(avg_content_per_contributor, 2),
            'collaboration_ratio': round(cross_author_links / max(total_links, 1), 2),
            'is_highly_collaborative': cross_author_links > 5 and contributor_count > 2
        }

    def get_top_contributors(self, obj):
        """Get top 5 contributors by content count with their contribution details."""
        from django.contrib.auth.models import User
        from django.db.models import Count, Q
        
        contributors = User.objects.filter(
            Q(page_authored__world=obj) |
            Q(essay_authored__world=obj) |
            Q(character_authored__world=obj) |
            Q(story_authored__world=obj) |
            Q(image_authored__world=obj)
        ).distinct().annotate(
            page_count=Count('page_authored', filter=Q(page_authored__world=obj)),
            essay_count=Count('essay_authored', filter=Q(essay_authored__world=obj)),
            character_count=Count('character_authored', filter=Q(character_authored__world=obj)),
            story_count=Count('story_authored', filter=Q(story_authored__world=obj)),
            image_count=Count('image_authored', filter=Q(image_authored__world=obj)),
            total_contributions=Count('page_authored', filter=Q(page_authored__world=obj)) +
                              Count('essay_authored', filter=Q(essay_authored__world=obj)) +
                              Count('character_authored', filter=Q(character_authored__world=obj)) +
                              Count('story_authored', filter=Q(story_authored__world=obj)) +
                              Count('image_authored', filter=Q(image_authored__world=obj))
        ).order_by('-total_contributions')[:5]

        result = []
        for contributor in contributors:
            # Get first and last contribution dates
            from datetime import datetime
            first_contribution = None
            last_contribution = None
            
            all_content = []
            if contributor.page_authored.filter(world=obj).exists():
                all_content.extend(contributor.page_authored.filter(world=obj))
            if contributor.essay_authored.filter(world=obj).exists():
                all_content.extend(contributor.essay_authored.filter(world=obj))
            if contributor.character_authored.filter(world=obj).exists():
                all_content.extend(contributor.character_authored.filter(world=obj))
            if contributor.story_authored.filter(world=obj).exists():
                all_content.extend(contributor.story_authored.filter(world=obj))
            if contributor.image_authored.filter(world=obj).exists():
                all_content.extend(contributor.image_authored.filter(world=obj))
            
            if all_content:
                all_content.sort(key=lambda x: x.created_at)
                first_contribution = all_content[0].created_at
                last_contribution = all_content[-1].created_at
            
            result.append({
                'id': contributor.id,
                'username': contributor.username,
                'first_name': contributor.first_name,
                'last_name': contributor.last_name,
                'full_name': contributor.get_full_name() or contributor.username,
                'contributions': {
                    'pages': contributor.page_count,
                    'essays': contributor.essay_count,
                    'characters': contributor.character_count,
                    'stories': contributor.story_count,
                    'images': contributor.image_count,
                    'total': contributor.total_contributions
                },
                'first_contribution': first_contribution,
                'last_contribution': last_contribution,
                'is_creator': contributor == obj.creator
            })
        
        return result


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for the Tag model.
    Handles tag creation and display within worlds.
    """
    usage_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'world', 'created_at', 'usage_count']
        read_only_fields = ['world', 'created_at', 'usage_count']

    def get_usage_count(self, obj):
        """Get the number of content entries using this tag."""
        return obj.get_usage_count()

    def validate_name(self, value):
        """Validate and normalize tag name."""
        if not value.strip():
            raise serializers.ValidationError("Tag name cannot be empty.")
        
        normalized_name = value.strip().lower()
        
        # Check for uniqueness within the world (if world is provided)
        world = self.context.get('world')
        if world and self.instance is None:  # Only check on creation
            if Tag.objects.filter(name=normalized_name, world=world).exists():
                raise serializers.ValidationError(
                    f"Tag '{normalized_name}' already exists in this world."
                )
        
        return normalized_name


class ContentLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for ContentLink model.
    Handles bidirectional content relationships.
    """
    from_content_title = serializers.SerializerMethodField()
    from_content_type_name = serializers.SerializerMethodField()
    to_content_title = serializers.SerializerMethodField()
    to_content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = ContentLink
        fields = [
            'id', 'from_content_type', 'from_object_id', 'from_content_title', 'from_content_type_name',
            'to_content_type', 'to_object_id', 'to_content_title', 'to_content_type_name',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def get_from_content_title(self, obj):
        """Get the title of the source content."""
        try:
            return obj.from_content.title if obj.from_content else "Unknown"
        except:
            return "Unknown"

    def get_from_content_type_name(self, obj):
        """Get the model name of the source content."""
        return obj.from_content_type.model if obj.from_content_type else "Unknown"

    def get_to_content_title(self, obj):
        """Get the title of the target content."""
        try:
            return obj.to_content.title if obj.to_content else "Unknown"
        except:
            return "Unknown"

    def get_to_content_type_name(self, obj):
        """Get the model name of the target content."""
        return obj.to_content_type.model if obj.to_content_type else "Unknown"


class ContentBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for all content types.
    Provides common fields and validation for content models.
    Enhanced with collaborative features and attribution.
    """
    author = UserSerializer(read_only=True)
    world = serializers.PrimaryKeyRelatedField(read_only=True)
    tags = serializers.SerializerMethodField()
    linked_content = serializers.SerializerMethodField()
    attribution = serializers.SerializerMethodField()
    collaboration_info = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'id', 'title', 'content', 'author', 'world', 'created_at',
            'tags', 'linked_content', 'attribution', 'collaboration_info'
        ]
        read_only_fields = ['author', 'world', 'created_at', 'tags', 'linked_content', 'attribution', 'collaboration_info']

    def get_tags(self, obj):
        """Get all tags associated with this content."""
        tags = obj.get_tags()
        return TagSerializer(tags, many=True).data

    def get_linked_content(self, obj):
        """Get basic info about linked content with enhanced attribution."""
        linked_content = obj.get_linked_content()
        result = []
        for content in linked_content:
            result.append({
                'id': content.id,
                'title': content.title,
                'type': content.__class__.__name__.lower(),
                'author': {
                    'id': content.author.id,
                    'username': content.author.username,
                    'first_name': content.author.first_name,
                    'last_name': content.author.last_name
                },
                'created_at': content.created_at,
                'attribution': f"Created by {content.author.username} on {content.created_at.strftime('%B %d, %Y at %I:%M %p')}"
            })
        return result

    def get_attribution(self, obj):
        """Get formatted attribution string for this content."""
        author_name = obj.author.get_full_name() or obj.author.username
        created_date = obj.created_at.strftime('%B %d, %Y at %I:%M %p')
        return f"Created by {author_name} on {created_date}"

    def get_collaboration_info(self, obj):
        """Get collaboration-related information for this content."""
        # Get linked content count
        linked_count = len(obj.get_linked_content())
        
        # Get content linking to this
        linking_count = len(obj.get_content_linking_to_this())
        
        # Get tags count
        tags_count = obj.get_tags().count()
        
        # Check if this content references other authors' work
        linked_content = obj.get_linked_content()
        referenced_authors = set()
        for content in linked_content:
            if content.author != obj.author:
                referenced_authors.add(content.author.username)
        
        # Check if other authors have referenced this content
        linking_content = obj.get_content_linking_to_this()
        referencing_authors = set()
        for content in linking_content:
            if content.author != obj.author:
                referencing_authors.add(content.author.username)
        
        return {
            'links_to_count': linked_count,
            'linked_from_count': linking_count,
            'tags_count': tags_count,
            'references_other_authors': list(referenced_authors),
            'referenced_by_authors': list(referencing_authors),
            'is_collaborative': len(referenced_authors) > 0 or len(referencing_authors) > 0,
            'collaboration_score': linked_count + linking_count + tags_count
        }

    def validate_title(self, value):
        """Validate content title."""
        if not value or not value.strip():
            raise serializers.ValidationError({
                'message': "Title cannot be empty",
                'code': 'required',
                'field': 'title'
            })
        
        if len(value.strip()) < 3:
            raise serializers.ValidationError({
                'message': "Title must be at least 3 characters long",
                'code': 'min_length',
                'field': 'title',
                'min_length': 3,
                'current_length': len(value.strip())
            })
        
        if len(value.strip()) > 300:
            raise serializers.ValidationError({
                'message': "Title cannot exceed 300 characters",
                'code': 'max_length',
                'field': 'title',
                'max_length': 300,
                'current_length': len(value.strip())
            })
        
        return value.strip()

    def validate_content(self, value):
        """Validate content body."""
        if not value or not value.strip():
            raise serializers.ValidationError({
                'message': "Content cannot be empty",
                'code': 'required',
                'field': 'content'
            })
        
        if len(value.strip()) < 10:
            raise serializers.ValidationError({
                'message': "Content must be at least 10 characters long",
                'code': 'min_length',
                'field': 'content',
                'min_length': 10,
                'current_length': len(value.strip())
            })
        
        return value.strip()


class PageSerializer(ContentBaseSerializer):
    """
    Serializer for Page model (wiki entries).
    Inherits common content fields from ContentBaseSerializer.
    """
    class Meta(ContentBaseSerializer.Meta):
        model = Page
        fields = ContentBaseSerializer.Meta.fields + ['summary']
        read_only_fields = ContentBaseSerializer.Meta.read_only_fields

    def validate_summary(self, value):
        """Validate page summary."""
        if value and len(value.strip()) > 500:
            raise serializers.ValidationError("Summary cannot exceed 500 characters.")
        return value.strip() if value else ""


class EssaySerializer(ContentBaseSerializer):
    """
    Serializer for Essay model (long-form content).
    Inherits common content fields from ContentBaseSerializer.
    """
    class Meta(ContentBaseSerializer.Meta):
        model = Essay
        fields = ContentBaseSerializer.Meta.fields + ['abstract', 'word_count']
        read_only_fields = ContentBaseSerializer.Meta.read_only_fields + ['word_count']

    def validate_abstract(self, value):
        """Validate essay abstract."""
        if value and len(value.strip()) > 1000:
            raise serializers.ValidationError("Abstract cannot exceed 1000 characters.")
        return value.strip() if value else ""


class CharacterSerializer(ContentBaseSerializer):
    """
    Serializer for Character model (character profiles).
    Inherits common content fields from ContentBaseSerializer.
    """
    class Meta(ContentBaseSerializer.Meta):
        model = Character
        fields = ContentBaseSerializer.Meta.fields + [
            'full_name', 'age', 'species', 'occupation', 'location',
            'personality_traits', 'physical_description', 'background', 'relationships'
        ]
        read_only_fields = ContentBaseSerializer.Meta.read_only_fields

    def validate_full_name(self, value):
        """Validate character full name."""
        if not value.strip():
            raise serializers.ValidationError("Character must have a full name.")
        return value.strip()

    def validate_personality_traits(self, value):
        """Validate personality traits list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Personality traits must be a list.")
        return [trait.strip() for trait in value if trait.strip()]

    def validate_relationships(self, value):
        """Validate relationships dictionary."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Relationships must be a dictionary.")
        return value


class StorySerializer(ContentBaseSerializer):
    """
    Serializer for Story model (narrative content).
    Inherits common content fields from ContentBaseSerializer.
    """
    class Meta(ContentBaseSerializer.Meta):
        model = Story
        fields = ContentBaseSerializer.Meta.fields + [
            'genre', 'story_type', 'timeline_period', 'setting_location',
            'main_characters', 'word_count', 'is_canonical'
        ]
        read_only_fields = ContentBaseSerializer.Meta.read_only_fields + ['word_count']

    def validate_main_characters(self, value):
        """Validate main characters list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Main characters must be a list.")
        return [char.strip() for char in value if char.strip()]


class ImageSerializer(ContentBaseSerializer):
    """
    Serializer for Image model (visual content).
    Inherits common content fields from ContentBaseSerializer.
    """
    image_url = serializers.SerializerMethodField()

    class Meta(ContentBaseSerializer.Meta):
        model = Image
        fields = ContentBaseSerializer.Meta.fields + [
            'image_file', 'image_url', 'caption', 'alt_text', 'image_type',
            'dimensions', 'file_size'
        ]
        read_only_fields = ContentBaseSerializer.Meta.read_only_fields + [
            'dimensions', 'file_size', 'image_url'
        ]

    def get_image_url(self, obj):
        """Get the URL for the uploaded image."""
        if obj.image_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_file.url)
            return obj.image_file.url
        return None

    def validate_alt_text(self, value):
        """Validate alt text for accessibility."""
        if not value.strip():
            raise serializers.ValidationError("Alt text is required for accessibility.")
        return value.strip()

    def validate_image_file(self, value):
        """Validate uploaded image file."""
        from .exceptions import validate_file_upload, FileUploadError
        
        if not value:
            raise serializers.ValidationError("Image file is required.")
        
        try:
            # Use the centralized file upload validation
            allowed_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                'image/bmp', 'image/tiff'
            ]
            validate_file_upload(value, max_size_mb=10, allowed_types=allowed_types)
            
        except FileUploadError as e:
            raise serializers.ValidationError(e.message)
        
        return value


# Enhanced WorldSerializer with nested content relationships
class WorldDetailSerializer(WorldSerializer):
    """
    Detailed world serializer with nested content relationships.
    Used for world detail views with full content listings.
    """
    recent_pages = serializers.SerializerMethodField()
    recent_essays = serializers.SerializerMethodField()
    recent_characters = serializers.SerializerMethodField()
    recent_stories = serializers.SerializerMethodField()
    recent_images = serializers.SerializerMethodField()
    popular_tags = serializers.SerializerMethodField()

    class Meta(WorldSerializer.Meta):
        fields = WorldSerializer.Meta.fields + [
            'recent_pages', 'recent_essays', 'recent_characters',
            'recent_stories', 'recent_images', 'popular_tags'
        ]

    def get_recent_pages(self, obj):
        """Get the 5 most recent pages in this world."""
        recent_pages = obj.page_entries.all()[:5]
        return PageSerializer(recent_pages, many=True, context=self.context).data

    def get_recent_essays(self, obj):
        """Get the 5 most recent essays in this world."""
        recent_essays = obj.essay_entries.all()[:5]
        return EssaySerializer(recent_essays, many=True, context=self.context).data

    def get_recent_characters(self, obj):
        """Get the 5 most recent characters in this world."""
        recent_characters = obj.character_entries.all()[:5]
        return CharacterSerializer(recent_characters, many=True, context=self.context).data

    def get_recent_stories(self, obj):
        """Get the 5 most recent stories in this world."""
        recent_stories = obj.story_entries.all()[:5]
        return StorySerializer(recent_stories, many=True, context=self.context).data

    def get_recent_images(self, obj):
        """Get the 5 most recent images in this world."""
        recent_images = obj.image_entries.all()[:5]
        return ImageSerializer(recent_images, many=True, context=self.context).data

    def get_popular_tags(self, obj):
        """Get the 10 most popular tags in this world."""
        popular_tags = obj.get_popular_tags(limit=10)
        return [{'name': tag.name, 'usage_count': count} for tag, count in popular_tags]