"""
Views for managing tagging and linking API endpoints.
Handles tag management, content tagging, content linking, and tag-based search.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.contrib.contenttypes.models import ContentType
from ..models import World, Tag, ContentTag, ContentLink, Page, Essay, Character, Story, Image
from ..serializers import TagSerializer, ContentLinkSerializer
from ..permissions import IsAuthorOrReadOnly


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Tag management within worlds.
    
    Provides:
    - CRUD operations for tags within a world
    - Tag usage statistics
    - Content filtering by tags
    """
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_world(self):
        """Get the world from URL parameters."""
        world_id = self.kwargs.get('world_pk')
        return get_object_or_404(World, pk=world_id)
    
    def get_queryset(self):
        """Filter tags by world and optimize queries."""
        world = self.get_world()
        return Tag.objects.filter(world=world).annotate(
            usage_count=Count('content_tags')
        ).order_by('name')
    
    def get_serializer_context(self):
        """Add world to serializer context."""
        context = super().get_serializer_context()
        context['world'] = self.get_world()
        return context
    
    def perform_create(self, serializer):
        """Set world automatically on tag creation."""
        world = self.get_world()
        serializer.save(world=world)
    
    def list(self, request, *args, **kwargs):
        """List tags in a world with filtering options."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by usage count
        min_usage = request.query_params.get('min_usage')
        if min_usage:
            try:
                queryset = queryset.filter(usage_count__gte=int(min_usage))
            except ValueError:
                pass
        
        # Search by tag name
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Sort options
        sort_by = request.query_params.get('sort', 'name')
        if sort_by == 'usage':
            queryset = queryset.order_by('-usage_count', 'name')
        elif sort_by == 'created':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('name')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def content(self, request, pk=None, world_pk=None):
        """Get all content that has this tag."""
        tag = self.get_object()
        world = self.get_world()
        
        # Get content by type
        content_by_type = {}
        content_models = {
            'pages': Page,
            'essays': Essay,
            'characters': Character,
            'stories': Story,
            'images': Image
        }
        
        for type_name, model_class in content_models.items():
            content_queryset = model_class.get_content_by_tag(world, tag.name)
            
            # Apply additional filtering if requested
            author_username = request.query_params.get('author')
            if author_username:
                content_queryset = content_queryset.filter(author__username=author_username)
            
            search = request.query_params.get('search')
            if search:
                content_queryset = content_queryset.filter(
                    Q(title__icontains=search) | Q(content__icontains=search)
                )
            
            # Convert to list with basic info
            content_list = []
            for content in content_queryset:
                content_list.append({
                    'id': content.id,
                    'title': content.title,
                    'type': type_name[:-1],  # Remove 's' from plural
                    'author': content.author.username,
                    'created_at': content.created_at,
                    'url': f'/api/worlds/{world.id}/{type_name}/{content.id}/'
                })
            
            content_by_type[type_name] = content_list
        
        return Response({
            'tag': TagSerializer(tag).data,
            'content_by_type': content_by_type,
            'total_content': sum(len(content_list) for content_list in content_by_type.values())
        })
    
    @action(detail=False, methods=['get'], url_path='by-name/(?P<tag_name>[^/.]+)')
    def by_name(self, request, tag_name=None, world_pk=None):
        """Get a tag by name with its tagged content."""
        world = self.get_world()
        
        try:
            tag = Tag.objects.get(world=world, name=tag_name)
        except Tag.DoesNotExist:
            return Response({
                'error': 'Tag not found',
                'message': f'Tag "{tag_name}" does not exist in this world'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get all content that has this tag
        tagged_content = []
        content_models = {
            'page': Page,
            'essay': Essay,
            'character': Character,
            'story': Story,
            'image': Image
        }
        
        for type_name, model_class in content_models.items():
            content_queryset = model_class.get_content_by_tag(world, tag.name)
            
            for content in content_queryset:
                tagged_content.append({
                    'object_id': content.id,
                    'content_type': type_name,
                    'title': content.title,
                    'author_name': content.author.first_name or content.author.username,
                    'created_at': content.created_at,
                })
        
        # Sort by creation date (newest first)
        tagged_content.sort(key=lambda x: x['created_at'], reverse=True)
        
        tag_data = TagSerializer(tag).data
        tag_data['tagged_content'] = tagged_content
        
        return Response(tag_data)

    @action(detail=False, methods=['get'])
    def popular(self, request, world_pk=None):
        """Get the most popular tags in the world."""
        world = self.get_world()
        limit = min(int(request.query_params.get('limit', 20)), 100)  # Max 100 tags
        
        popular_tags = world.get_popular_tags(limit=limit)
        
        tag_data = []
        for tag, usage_count in popular_tags:
            tag_data.append({
                'id': tag.id,
                'name': tag.name,
                'usage_count': usage_count,
                'created_at': tag.created_at
            })
        
        return Response({
            'popular_tags': tag_data,
            'world': world.title
        })
    
    @action(detail=False, methods=['get'])
    def search_content(self, request, world_pk=None):
        """Search content across all types by tags."""
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
        
        # Get content by tags across all types
        content_by_type = world.get_all_content_by_tags(tag_names, match_all=match_all)
        
        # Format response
        results = {}
        total_results = 0
        
        for type_name, queryset in content_by_type.items():
            # Apply additional filtering
            author_username = request.query_params.get('author')
            if author_username:
                queryset = queryset.filter(author__username=author_username)
            
            search = request.query_params.get('search')
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) | Q(content__icontains=search)
                )
            
            # Convert to list with basic info
            content_list = []
            for content in queryset[:50]:  # Limit to 50 per type
                content_list.append({
                    'id': content.id,
                    'title': content.title,
                    'type': type_name[:-1],  # Remove 's' from plural
                    'author': content.author.username,
                    'created_at': content.created_at,
                    'tags': [tag.name for tag in content.get_tags()],
                    'url': f'/api/worlds/{world.id}/{type_name}/{content.id}/'
                })
            
            results[type_name] = content_list
            total_results += len(content_list)
        
        return Response({
            'search_tags': tag_names,
            'match_all': match_all,
            'results_by_type': results,
            'total_results': total_results,
            'world': world.title
        })


class ContentLinkViewSet(viewsets.ModelViewSet):
    """
    API endpoint for ContentLink management.
    
    Provides:
    - CRUD operations for content links
    - Bidirectional relationship management
    - Link discovery and navigation
    """
    serializer_class = ContentLinkSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    
    def get_world(self):
        """Get the world from URL parameters."""
        world_id = self.kwargs.get('world_pk')
        return get_object_or_404(World, pk=world_id)
    
    def get_queryset(self):
        """Filter links by world through content relationships."""
        world = self.get_world()
        
        # Get all content types and their IDs in this world
        content_models = [Page, Essay, Character, Story, Image]
        world_content_ids = {}
        
        for model_class in content_models:
            content_type = ContentType.objects.get_for_model(model_class)
            content_ids = list(model_class.objects.filter(world=world).values_list('id', flat=True))
            world_content_ids[content_type.id] = content_ids
        
        # Filter links to only include those between content in this world
        queryset = ContentLink.objects.none()
        for content_type_id, content_ids in world_content_ids.items():
            if content_ids:
                world_links = ContentLink.objects.filter(
                    from_content_type_id=content_type_id,
                    from_object_id__in=content_ids
                )
                queryset = queryset.union(world_links)
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Create a new content link with validation."""
        world = self.get_world()
        
        # Get source and target content information
        from_type = request.data.get('from_content_type')
        from_id = request.data.get('from_object_id')
        to_type = request.data.get('to_content_type')
        to_id = request.data.get('to_object_id')
        
        if not all([from_type, from_id, to_type, to_id]):
            return Response({
                'error': 'Missing required fields',
                'message': 'Please provide from_content_type, from_object_id, to_content_type, and to_object_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get content type objects
        try:
            from_content_type = ContentType.objects.get(id=from_type)
            to_content_type = ContentType.objects.get(id=to_type)
        except ContentType.DoesNotExist:
            return Response({
                'error': 'Invalid content type',
                'message': 'One or more content types do not exist'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get actual content objects and validate they're in the same world
        try:
            from_content = from_content_type.get_object_for_this_type(id=from_id)
            to_content = to_content_type.get_object_for_this_type(id=to_id)
            
            if from_content.world != world or to_content.world != world:
                return Response({
                    'error': 'Content not in world',
                    'message': 'Both content entries must be in the specified world'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception:
            return Response({
                'error': 'Content not found',
                'message': 'One or more content entries do not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user has permission to create links from the source content
        if from_content.author != request.user:
            return Response({
                'error': 'Permission denied',
                'message': 'You can only create links from content you authored'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create the bidirectional link using the model method
        try:
            link = from_content.link_to(to_content)
            serializer = self.get_serializer(link)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': 'Link creation failed',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a content link and its bidirectional counterpart."""
        link = self.get_object()
        
        # Check if user has permission to delete this link
        try:
            from_content = link.from_content
            if from_content.author != request.user:
                return Response({
                    'error': 'Permission denied',
                    'message': 'You can only delete links from content you authored'
                }, status=status.HTTP_403_FORBIDDEN)
        except:
            return Response({
                'error': 'Content not found',
                'message': 'Source content no longer exists'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Use the model method to remove bidirectional links
        try:
            to_content = link.to_content
            from_content.unlink_from(to_content)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'error': 'Link deletion failed',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def for_content(self, request, world_pk=None):
        """Get all links for a specific content entry."""
        world = self.get_world()
        
        content_type_name = request.query_params.get('content_type')
        content_id = request.query_params.get('content_id')
        
        if not content_type_name or not content_id:
            return Response({
                'error': 'Missing parameters',
                'message': 'Please provide content_type and content_id parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the content model and object
        model_map = {
            'page': Page,
            'essay': Essay,
            'character': Character,
            'story': Story,
            'image': Image
        }
        
        model_class = model_map.get(content_type_name.lower())
        if not model_class:
            return Response({
                'error': 'Invalid content type',
                'message': f'Content type must be one of: {", ".join(model_map.keys())}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            content = model_class.objects.get(id=content_id, world=world)
        except model_class.DoesNotExist:
            return Response({
                'error': 'Content not found',
                'message': 'Content entry does not exist in this world'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get linked content
        linked_content = content.get_linked_content()
        linking_content = content.get_content_linking_to_this()
        
        # Format response
        linked_data = []
        for linked in linked_content:
            linked_data.append({
                'id': linked.id,
                'title': linked.title,
                'type': linked.__class__.__name__.lower(),
                'author': linked.author.username,
                'created_at': linked.created_at,
                'url': f'/api/worlds/{world.id}/{linked.__class__.__name__.lower()}s/{linked.id}/'
            })
        
        linking_data = []
        for linking in linking_content:
            linking_data.append({
                'id': linking.id,
                'title': linking.title,
                'type': linking.__class__.__name__.lower(),
                'author': linking.author.username,
                'created_at': linking.created_at,
                'url': f'/api/worlds/{world.id}/{linking.__class__.__name__.lower()}s/{linking.id}/'
            })
        
        return Response({
            'content': {
                'id': content.id,
                'title': content.title,
                'type': content_type_name,
                'author': content.author.username
            },
            'links_to': linked_data,
            'linked_from': linking_data,
            'total_links': len(linked_data) + len(linking_data)
        })
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request, world_pk=None):
        """Create multiple content links at once."""
        world = self.get_world()
        links_data = request.data.get('links', [])
        
        if not isinstance(links_data, list):
            return Response({
                'error': 'Invalid data format',
                'message': 'Links must be provided as a list'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created_links = []
        errors = []
        
        for i, link_data in enumerate(links_data):
            try:
                # Validate required fields
                from_type = link_data.get('from_content_type')
                from_id = link_data.get('from_object_id')
                to_type = link_data.get('to_content_type')
                to_id = link_data.get('to_object_id')
                
                if not all([from_type, from_id, to_type, to_id]):
                    errors.append({
                        'index': i,
                        'error': 'Missing required fields'
                    })
                    continue
                
                # Get content objects
                from_content_type = ContentType.objects.get(id=from_type)
                to_content_type = ContentType.objects.get(id=to_type)
                from_content = from_content_type.get_object_for_this_type(id=from_id)
                to_content = to_content_type.get_object_for_this_type(id=to_id)
                
                # Validate world membership
                if from_content.world != world or to_content.world != world:
                    errors.append({
                        'index': i,
                        'error': 'Content not in world'
                    })
                    continue
                
                # Check permissions
                if from_content.author != request.user:
                    errors.append({
                        'index': i,
                        'error': 'Permission denied'
                    })
                    continue
                
                # Create the link
                link = from_content.link_to(to_content)
                created_links.append(ContentLinkSerializer(link).data)
                
            except Exception as e:
                errors.append({
                    'index': i,
                    'error': str(e)
                })
        
        return Response({
            'created_links': created_links,
            'errors': errors,
            'total_created': len(created_links),
            'total_errors': len(errors)
        }, status=status.HTTP_201_CREATED if created_links else status.HTTP_400_BAD_REQUEST)