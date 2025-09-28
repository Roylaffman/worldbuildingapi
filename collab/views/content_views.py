"""
Views for managing content creation API endpoints.
Handles immutable content creation for Pages, Essays, Characters, Stories, and Images.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from ..models import World, Page, Essay, Character, Story, Image, Tag, ContentTag, ContentLink
from ..serializers import (
    PageSerializer, EssaySerializer, CharacterSerializer, 
    StorySerializer, ImageSerializer, TagSerializer, ContentLinkSerializer
)
from ..permissions import IsAuthorOrReadOnly


class ContentViewSetMixin:
    """
    Mixin providing common functionality for all content ViewSets.
    Handles world-scoped content, immutability enforcement, and tagging.
    """
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    
    def get_world(self):
        """Get the world from URL parameters."""
        world_id = self.kwargs.get('world_pk')
        if not world_id:
            # Fallback to request data for world_id if not in URL
            world_id = self.request.data.get('world_id') or self.request.query_params.get('world_id')
        return get_object_or_404(World, pk=world_id)
    
    def get_queryset(self):
        """Filter content by world and optimize queries."""
        world = self.get_world()
        return self.queryset.filter(world=world).select_related(
            'author', 'world'
        ).prefetch_related(
            'author__worldbuilding_profile'
        )
    
    def perform_create(self, serializer):
        """Set author and world automatically on content creation."""
        world = self.get_world()
        serializer.save(author=self.request.user, world=world)
    
    def create(self, request, *args, **kwargs):
        """
        Create new content with automatic tagging and linking.
        Enforces immutability by only allowing POST operations.
        """
        from ..exceptions import WorldAccessError, ContentValidationError
        
        # Get world and validate access
        try:
            world = self.get_world()
        except Exception:
            raise WorldAccessError(
                "World not found or access denied",
                world_id=self.kwargs.get('world_pk')
            )
        
        # Create the content with enhanced error handling
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            content = serializer.save(author=request.user, world=world)
        except Exception as e:
            # Convert Django validation errors to our custom format
            if hasattr(e, 'detail') and isinstance(e.detail, dict):
                # DRF validation error
                raise ContentValidationError(
                    "Content validation failed",
                    field=list(e.detail.keys())[0] if e.detail else None
                )
            else:
                # Other validation errors
                raise ContentValidationError(str(e))
        
        # Handle tags if provided
        tags_data = request.data.get('tags', [])
        if tags_data:
            if isinstance(tags_data, str):
                tag_names = [name.strip() for name in tags_data.split(',')]
            else:
                tag_names = tags_data
            
            for tag_name in tag_names:
                if tag_name.strip():
                    content.add_tag(tag_name.strip())
        
        # Handle content links if provided
        links_data = request.data.get('links', [])
        if links_data:
            for link_data in links_data:
                try:
                    target_type = link_data.get('content_type')
                    target_id = link_data.get('content_id')
                    
                    if target_type and target_id:
                        # Get the target content model
                        model_map = {
                            'page': Page,
                            'essay': Essay,
                            'character': Character,
                            'story': Story,
                            'image': Image
                        }
                        
                        target_model = model_map.get(target_type.lower())
                        if target_model:
                            target_content = target_model.objects.get(
                                id=target_id, world=world
                            )
                            content.link_to(target_content)
                except Exception:
                    # Skip invalid links silently
                    continue
        
        # Return the created content with full serialization
        headers = self.get_success_headers(serializer.data)
        return Response(
            self.get_serializer(content).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def update(self, request, *args, **kwargs):
        """
        Prevent updates to enforce immutability.
        Returns 405 Method Not Allowed.
        """
        return Response({
            'error': 'Content cannot be modified after creation',
            'message': 'This content is immutable. Create new content instead.'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Prevent partial updates to enforce immutability.
        Returns 405 Method Not Allowed.
        """
        return Response({
            'error': 'Content cannot be modified after creation',
            'message': 'This content is immutable. Create new content instead.'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def destroy(self, request, *args, **kwargs):
        """
        Prevent deletion to enforce immutability.
        Returns 405 Method Not Allowed.
        """
        return Response({
            'error': 'Content cannot be deleted',
            'message': 'This content is immutable and cannot be deleted.'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @action(detail=True, methods=['post'])
    def add_tags(self, request, pk=None, world_pk=None):
        """Add tags to existing content."""
        content = self.get_object()
        tags_data = request.data.get('tags', [])
        
        if isinstance(tags_data, str):
            tag_names = [name.strip() for name in tags_data.split(',')]
        else:
            tag_names = tags_data
        
        added_tags = []
        for tag_name in tag_names:
            if tag_name.strip():
                try:
                    content_tag = content.add_tag(tag_name.strip())
                    if content_tag:
                        added_tags.append(content_tag.tag.name)
                except Exception as e:
                    # Skip invalid tags silently
                    continue
        
        return Response({
            'message': f'Added {len(added_tags)} tags',
            'added_tags': added_tags,
            'all_tags': [tag.name for tag in content.get_tags()]
        })
    
    @action(detail=True, methods=['post'])
    def add_links(self, request, pk=None, world_pk=None):
        """Add links to other content."""
        content = self.get_object()
        world = self.get_world()
        links_data = request.data.get('links', [])
        
        added_links = []
        for link_data in links_data:
            try:
                target_type = link_data.get('content_type')
                target_id = link_data.get('content_id')
                
                if target_type and target_id:
                    model_map = {
                        'page': Page,
                        'essay': Essay,
                        'character': Character,
                        'story': Story,
                        'image': Image
                    }
                    
                    target_model = model_map.get(target_type.lower())
                    if target_model:
                        target_content = target_model.objects.get(
                            id=target_id, world=world
                        )
                        content.link_to(target_content)
                        added_links.append({
                            'target_type': target_type,
                            'target_id': target_id,
                            'target_title': target_content.title
                        })
            except Exception:
                continue
        
        return Response({
            'message': f'Added {len(added_links)} links',
            'added_links': added_links
        })
    
    @action(detail=False, methods=['get'])
    def chronological_content(self, request, world_pk=None):
        """Get content in chronological order with advanced filtering."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply date range filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            try:
                from django.utils.dateparse import parse_datetime, parse_date
                start_datetime = parse_datetime(start_date) or parse_date(start_date)
                if start_datetime:
                    queryset = queryset.filter(created_at__gte=start_datetime)
            except ValueError:
                pass
        
        if end_date:
            try:
                from django.utils.dateparse import parse_datetime, parse_date
                end_datetime = parse_datetime(end_date) or parse_date(end_date)
                if end_datetime:
                    queryset = queryset.filter(created_at__lte=end_datetime)
            except ValueError:
                pass
        
        # Apply additional filters
        author_username = request.query_params.get('author')
        if author_username:
            queryset = queryset.filter(author__username__icontains=author_username)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        tag = request.query_params.get('tag')
        if tag:
            world = self.get_world()
            tagged_content = self.queryset.model.get_content_by_tag(world, tag)
            queryset = queryset.filter(id__in=tagged_content.values_list('id', flat=True))
        
        # Sort chronologically (newest first by default)
        sort_order = request.query_params.get('sort', 'desc')
        if sort_order == 'asc':
            queryset = queryset.order_by('created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search_by_tags(self, request, world_pk=None):
        """Search content by multiple tags with advanced filtering."""
        world = self.get_world()
        
        # Get tag names from query parameters
        tags_param = request.query_params.get('tags', '')
        if not tags_param:
            return Response({
                'error': 'No tags specified',
                'message': 'Please provide tags parameter with comma-separated tag names'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tag_names = [name.strip() for name in tags_param.split(',') if name.strip()]
        if not tag_names:
            return Response({
                'error': 'No valid tags specified',
                'message': 'Please provide valid tag names'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine if we should match all tags or any tag
        match_all = request.query_params.get('match_all', 'false').lower() in ('true', '1', 'yes')
        
        # Get content by tags for this specific content type
        if match_all:
            queryset = self.queryset.model.get_content_by_tags(world, tag_names, match_all=True)
        else:
            queryset = self.queryset.model.get_content_by_tags(world, tag_names, match_all=False)
        
        # Apply additional filtering
        author_username = request.query_params.get('author')
        if author_username:
            queryset = queryset.filter(author__username=author_username)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attribution_details(self, request, pk=None, world_pk=None):
        """Get detailed attribution information for a specific content item."""
        content = self.get_object()
        world = self.get_world()
        
        # Get linked content with attribution details
        linked_content = content.get_linked_content()
        linking_content = content.get_content_linking_to_this()
        
        # Build attribution details
        references_made = []
        for linked in linked_content:
            references_made.append({
                'id': linked.id,
                'title': linked.title,
                'type': linked.__class__.__name__.lower(),
                'author': {
                    'id': linked.author.id,
                    'username': linked.author.username,
                    'full_name': linked.author.get_full_name() or linked.author.username
                },
                'created_at': linked.created_at,
                'attribution_text': f"References '{linked.title}' by {linked.author.get_full_name() or linked.author.username}",
                'is_cross_author': linked.author != content.author
            })
        
        references_received = []
        for linking in linking_content:
            references_received.append({
                'id': linking.id,
                'title': linking.title,
                'type': linking.__class__.__name__.lower(),
                'author': {
                    'id': linking.author.id,
                    'username': linking.author.username,
                    'full_name': linking.author.get_full_name() or linking.author.username
                },
                'created_at': linking.created_at,
                'attribution_text': f"'{linking.title}' by {linking.author.get_full_name() or linking.author.username} references this content",
                'is_cross_author': linking.author != content.author
            })
        
        # Get collaboration metrics
        cross_author_references_made = len([r for r in references_made if r['is_cross_author']])
        cross_author_references_received = len([r for r in references_received if r['is_cross_author']])
        
        # Get tags for context
        tags = [tag.name for tag in content.get_tags()]
        
        return Response({
            'content': {
                'id': content.id,
                'title': content.title,
                'type': content.__class__.__name__.lower(),
                'author': {
                    'id': content.author.id,
                    'username': content.author.username,
                    'full_name': content.author.get_full_name() or content.author.username
                },
                'created_at': content.created_at,
                'world': {
                    'id': world.id,
                    'title': world.title
                }
            },
            'attribution': {
                'primary_attribution': f"Created by {content.author.get_full_name() or content.author.username} on {content.created_at.strftime('%B %d, %Y at %I:%M %p')}",
                'references_made': references_made,
                'references_received': references_received,
                'tags': tags
            },
            'collaboration_metrics': {
                'total_references_made': len(references_made),
                'total_references_received': len(references_received),
                'cross_author_references_made': cross_author_references_made,
                'cross_author_references_received': cross_author_references_received,
                'collaboration_score': cross_author_references_made + cross_author_references_received,
                'is_collaborative': cross_author_references_made > 0 or cross_author_references_received > 0,
                'collaboration_type': 'bidirectional' if cross_author_references_made > 0 and cross_author_references_received > 0 else
                                   'outgoing' if cross_author_references_made > 0 else
                                   'incoming' if cross_author_references_received > 0 else
                                   'standalone'
            },
            'attribution_suggestions': {
                'should_reference_others': cross_author_references_made == 0 and len(tags) > 0,
                'well_attributed': cross_author_references_made > 0 or cross_author_references_received > 0,
                'attribution_quality': 'excellent' if cross_author_references_made >= 2 and cross_author_references_received >= 1 else
                                     'good' if cross_author_references_made >= 1 or cross_author_references_received >= 1 else
                                     'needs_improvement'
            }
        })


class PageViewSet(ContentViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint for Page content (wiki entries).
    
    Provides:
    - Create-only operations (immutable after creation)
    - List and retrieve with world filtering
    - Automatic timestamp enforcement
    - Tag and link management
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    
    def list(self, request, *args, **kwargs):
        """List pages in a world with filtering options."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Add filtering options
        author_username = request.query_params.get('author')
        if author_username:
            queryset = queryset.filter(author__username=author_username)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(summary__icontains=search)
            )
        
        tag = request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(
                id__in=Page.get_content_by_tag(self.get_world(), tag).values_list('id', flat=True)
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def chronological(self, request, world_pk=None):
        """Get pages in chronological order with advanced filtering."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply date range filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            try:
                from django.utils.dateparse import parse_datetime, parse_date
                start_datetime = parse_datetime(start_date) or parse_date(start_date)
                if start_datetime:
                    queryset = queryset.filter(created_at__gte=start_datetime)
            except ValueError:
                pass
        
        if end_date:
            try:
                from django.utils.dateparse import parse_datetime, parse_date
                end_datetime = parse_datetime(end_date) or parse_date(end_date)
                if end_datetime:
                    queryset = queryset.filter(created_at__lte=end_datetime)
            except ValueError:
                pass
        
        # Apply additional filters
        author_username = request.query_params.get('author')
        if author_username:
            queryset = queryset.filter(author__username__icontains=author_username)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        tag = request.query_params.get('tag')
        if tag:
            world = self.get_world()
            tagged_content = Page.get_content_by_tag(world, tag)
            queryset = queryset.filter(id__in=tagged_content.values_list('id', flat=True))
        
        # Sort chronologically (newest first by default)
        sort_order = request.query_params.get('sort', 'desc')
        if sort_order == 'asc':
            queryset = queryset.order_by('created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EssayViewSet(ContentViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint for Essay content (long-form content).
    
    Provides:
    - Create-only operations with automatic word count calculation
    - Timestamp enforcement for chronological integrity
    - Abstract field handling
    """
    queryset = Essay.objects.all()
    serializer_class = EssaySerializer
    
    def list(self, request, *args, **kwargs):
        """List essays in a world with filtering options."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Add filtering options
        author_username = request.query_params.get('author')
        if author_username:
            queryset = queryset.filter(author__username=author_username)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(abstract__icontains=search)
            )
        
        tag = request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(
                id__in=Essay.get_content_by_tag(self.get_world(), tag).values_list('id', flat=True)
            )
        
        # Filter by word count range
        min_words = request.query_params.get('min_words')
        max_words = request.query_params.get('max_words')
        if min_words:
            try:
                queryset = queryset.filter(word_count__gte=int(min_words))
            except ValueError:
                pass
        if max_words:
            try:
                queryset = queryset.filter(word_count__lte=int(max_words))
            except ValueError:
                pass
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CharacterViewSet(ContentViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint for Character profiles.
    
    Provides:
    - Create-only operations with structured profile handling
    - Validation for required character fields
    - JSON field handling for personality traits and relationships
    """
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    
    def list(self, request, *args, **kwargs):
        """List characters in a world with filtering options."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Add filtering options
        author_username = request.query_params.get('author')
        if author_username:
            queryset = queryset.filter(author__username=author_username)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(full_name__icontains=search) |
                Q(content__icontains=search) |
                Q(occupation__icontains=search) |
                Q(species__icontains=search)
            )
        
        tag = request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(
                id__in=Character.get_content_by_tag(self.get_world(), tag).values_list('id', flat=True)
            )
        
        # Filter by character attributes
        species = request.query_params.get('species')
        if species:
            queryset = queryset.filter(species__icontains=species)
        
        occupation = request.query_params.get('occupation')
        if occupation:
            queryset = queryset.filter(occupation__icontains=occupation)
        
        location = request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StoryViewSet(ContentViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint for Story content (narrative content).
    
    Provides:
    - Create-only operations with narrative metadata
    - Automatic word count calculation
    - Timeline and setting location handling
    """
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    
    def list(self, request, *args, **kwargs):
        """List stories in a world with filtering options."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Add filtering options
        author_username = request.query_params.get('author')
        if author_username:
            queryset = queryset.filter(author__username=author_username)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(genre__icontains=search) |
                Q(setting_location__icontains=search)
            )
        
        tag = request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(
                id__in=Story.get_content_by_tag(self.get_world(), tag).values_list('id', flat=True)
            )
        
        # Filter by story attributes
        genre = request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        
        story_type = request.query_params.get('story_type')
        if story_type:
            queryset = queryset.filter(story_type=story_type)
        
        is_canonical = request.query_params.get('is_canonical')
        if is_canonical is not None:
            is_canonical_bool = is_canonical.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_canonical=is_canonical_bool)
        
        timeline_period = request.query_params.get('timeline_period')
        if timeline_period:
            queryset = queryset.filter(timeline_period__icontains=timeline_period)
        
        # Filter by word count range
        min_words = request.query_params.get('min_words')
        max_words = request.query_params.get('max_words')
        if min_words:
            try:
                queryset = queryset.filter(word_count__gte=int(min_words))
            except ValueError:
                pass
        if max_words:
            try:
                queryset = queryset.filter(word_count__lte=int(max_words))
            except ValueError:
                pass
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ImageViewSet(ContentViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint for Image content (visual content).
    
    Provides:
    - Create-only operations with file upload validation
    - Multi-part form data parsing for image uploads
    - Automatic dimension and file size calculation
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def list(self, request, *args, **kwargs):
        """List images in a world with filtering options."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Add filtering options
        author_username = request.query_params.get('author')
        if author_username:
            queryset = queryset.filter(author__username=author_username)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(caption__icontains=search) |
                Q(alt_text__icontains=search)
            )
        
        tag = request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(
                id__in=Image.get_content_by_tag(self.get_world(), tag).values_list('id', flat=True)
            )
        
        # Filter by image attributes
        image_type = request.query_params.get('image_type')
        if image_type:
            queryset = queryset.filter(image_type=image_type)
        
        # Filter by file size range (in bytes)
        min_size = request.query_params.get('min_size')
        max_size = request.query_params.get('max_size')
        if min_size:
            try:
                queryset = queryset.filter(file_size__gte=int(min_size))
            except ValueError:
                pass
        if max_size:
            try:
                queryset = queryset.filter(file_size__lte=int(max_size))
            except ValueError:
                pass
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Create new image with file upload handling.
        Validates file type, size, and automatically extracts metadata.
        """
        # Validate that image file is provided
        if 'image_file' not in request.data:
            return Response({
                'error': 'Image file is required',
                'message': 'Please provide an image file in the image_file field.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Call parent create method which handles world assignment and tagging
        return super().create(request, *args, **kwargs)