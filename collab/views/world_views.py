"""
Views for managing World resources.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.contrib.contenttypes.models import ContentType
from ..models import World, ContentTag, Page, Essay, Character, Story, Image
from ..serializers import WorldSerializer, WorldDetailSerializer
from ..permissions import IsCreatorOrReadOnly


class WorldViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows worlds to be viewed or edited.
    - Provides full CRUD functionality with contributor counts
    - Listing all worlds is available to any authenticated user
    - Creating a world is available to any authenticated user
    - Updating or deleting a world is restricted to the world's creator
    - Detail view includes associated content and statistics
    """
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]

    def get_queryset(self):
        """
        Get worlds with optimized queries for contributor counts.
        """
        return World.objects.select_related(
            'creator__worldbuilding_profile'
        ).prefetch_related(
            'page_entries__author',
            'essay_entries__author', 
            'character_entries__author',
            'story_entries__author',
            'image_entries__author',
            'tags'
        ).annotate(
            # Count unique contributors across all content types
            contributor_count=Count(
                'page_entries__author', distinct=True
            ) + Count(
                'essay_entries__author', distinct=True
            ) + Count(
                'character_entries__author', distinct=True
            ) + Count(
                'story_entries__author', distinct=True
            ) + Count(
                'image_entries__author', distinct=True
            )
        ).order_by('-created_at')

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        Use detailed serializer for retrieve action.
        """
        if self.action == 'retrieve':
            return WorldDetailSerializer
        return WorldSerializer

    def perform_create(self, serializer):
        """
        Automatically set the creator of the world to the current logged-in user.
        """
        serializer.save(creator=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        List all worlds with contributor counts and basic statistics.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Add filtering options
        is_public = request.query_params.get('is_public')
        if is_public is not None:
            is_public_bool = is_public.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_public=is_public_bool)
        
        creator_username = request.query_params.get('creator')
        if creator_username:
            queryset = queryset.filter(creator__username=creator_username)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific world with detailed content information.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def contributors(self, request, pk=None):
        """
        Get all contributors to a specific world with their contribution counts and collaboration details.
        Enhanced with attribution and collaboration tracking.
        """
        world = self.get_object()
        
        # Get all unique contributors across content types
        from django.contrib.auth.models import User
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        contributors = User.objects.filter(
            Q(page_authored__world=world) |
            Q(essay_authored__world=world) |
            Q(character_authored__world=world) |
            Q(story_authored__world=world) |
            Q(image_authored__world=world)
        ).distinct().annotate(
            page_count=Count('page_authored', filter=Q(page_authored__world=world)),
            essay_count=Count('essay_authored', filter=Q(essay_authored__world=world)),
            character_count=Count('character_authored', filter=Q(character_authored__world=world)),
            story_count=Count('story_authored', filter=Q(story_authored__world=world)),
            image_count=Count('image_authored', filter=Q(image_authored__world=world))
        ).annotate(
            total_contributions=Count('page_authored', filter=Q(page_authored__world=world)) +
                              Count('essay_authored', filter=Q(essay_authored__world=world)) +
                              Count('character_authored', filter=Q(character_authored__world=world)) +
                              Count('story_authored', filter=Q(story_authored__world=world)) +
                              Count('image_authored', filter=Q(image_authored__world=world))
        ).order_by('-total_contributions')

        contributor_data = []
        for contributor in contributors:
            # Get collaboration metrics for this contributor
            all_content = []
            if contributor.page_authored.filter(world=world).exists():
                all_content.extend(contributor.page_authored.filter(world=world))
            if contributor.essay_authored.filter(world=world).exists():
                all_content.extend(contributor.essay_authored.filter(world=world))
            if contributor.character_authored.filter(world=world).exists():
                all_content.extend(contributor.character_authored.filter(world=world))
            if contributor.story_authored.filter(world=world).exists():
                all_content.extend(contributor.story_authored.filter(world=world))
            if contributor.image_authored.filter(world=world).exists():
                all_content.extend(contributor.image_authored.filter(world=world))
            
            # Calculate collaboration metrics
            total_links_created = 0
            total_links_received = 0
            collaborating_authors = set()
            
            for content in all_content:
                # Links this contributor created to others
                linked_content = content.get_linked_content()
                total_links_created += len(linked_content)
                for linked in linked_content:
                    if linked.author != contributor:
                        collaborating_authors.add(linked.author.username)
                
                # Links others created to this contributor's content
                linking_content = content.get_content_linking_to_this()
                total_links_received += len(linking_content)
                for linking in linking_content:
                    if linking.author != contributor:
                        collaborating_authors.add(linking.author.username)
            
            # Get contribution timeline
            first_contribution = None
            last_contribution = None
            recent_activity = 0
            
            if all_content:
                all_content.sort(key=lambda x: x.created_at)
                first_contribution = all_content[0].created_at
                last_contribution = all_content[-1].created_at
                
                # Count recent activity (last 30 days)
                thirty_days_ago = datetime.now() - timedelta(days=30)
                recent_activity = len([c for c in all_content if c.created_at.replace(tzinfo=None) >= thirty_days_ago])
            
            contributor_data.append({
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
                'collaboration_metrics': {
                    'links_created': total_links_created,
                    'links_received': total_links_received,
                    'collaborating_with': list(collaborating_authors),
                    'collaboration_count': len(collaborating_authors),
                    'is_collaborative': len(collaborating_authors) > 0
                },
                'activity_timeline': {
                    'first_contribution': first_contribution,
                    'last_contribution': last_contribution,
                    'recent_activity_count': recent_activity,
                    'days_since_first': (datetime.now() - first_contribution.replace(tzinfo=None)).days if first_contribution else 0,
                    'days_since_last': (datetime.now() - last_contribution.replace(tzinfo=None)).days if last_contribution else 0
                },
                'role': 'creator' if contributor == world.creator else 'contributor',
                'attribution': f"{contributor.get_full_name() or contributor.username} - {contributor.total_contributions} contributions"
            })

        return Response({
            'world': {
                'id': world.id,
                'title': world.title,
                'creator': world.creator.username
            },
            'total_contributors': len(contributor_data),
            'contributors': contributor_data,
            'collaboration_summary': {
                'total_cross_author_links': sum(c['collaboration_metrics']['links_created'] + c['collaboration_metrics']['links_received'] for c in contributor_data) // 2,
                'most_collaborative': max(contributor_data, key=lambda x: x['collaboration_metrics']['collaboration_count'])['username'] if contributor_data else None,
                'most_active': max(contributor_data, key=lambda x: x['contributions']['total'])['username'] if contributor_data else None,
                'recent_contributors': len([c for c in contributor_data if c['activity_timeline']['recent_activity_count'] > 0])
            }
        })

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """
        Get chronological timeline of all content in the world with advanced filtering.
        
        Query parameters:
        - limit: Number of items to return (default: 50, max: 200)
        - offset: Number of items to skip for pagination
        - content_types: Comma-separated list of content types to include
        - author: Filter by author username
        - tags: Comma-separated list of tags (content must have at least one)
        - start_date: ISO date string for earliest content
        - end_date: ISO date string for latest content
        - search: Search term to filter content by title and body text
        """
        world = self.get_object()
        
        # Parse query parameters
        limit = min(int(request.query_params.get('limit', 50)), 200)
        offset = int(request.query_params.get('offset', 0))
        content_types_param = request.query_params.get('content_types', '')
        author_username = request.query_params.get('author', '')
        tags_param = request.query_params.get('tags', '')
        start_date_param = request.query_params.get('start_date', '')
        end_date_param = request.query_params.get('end_date', '')
        search_param = request.query_params.get('search', '')
        
        # Get all content and apply filters
        from django.db.models import Q
        from django.utils.dateparse import parse_datetime, parse_date
        from datetime import datetime
        
        # Parse content types filter
        if content_types_param:
            requested_types = [t.strip().lower() for t in content_types_param.split(',')]
            # Normalize plural forms
            type_mapping = {
                'page': 'pages', 'essay': 'essays', 'character': 'characters',
                'story': 'stories', 'image': 'images'
            }
            requested_types = [type_mapping.get(t, t) for t in requested_types]
        else:
            requested_types = []
        
        # Parse date filters
        start_date = None
        end_date = None
        
        if start_date_param:
            try:
                start_date = parse_datetime(start_date_param)
                if not start_date:
                    start_date = parse_date(start_date_param)
                    if start_date:
                        start_date = datetime.combine(start_date, datetime.min.time())
            except ValueError:
                pass
        
        if end_date_param:
            try:
                end_date = parse_datetime(end_date_param)
                if not end_date:
                    end_date = parse_date(end_date_param)
                    if end_date:
                        end_date = datetime.combine(end_date, datetime.max.time())
            except ValueError:
                pass
        
        # Collect all content items with filtering
        all_content = []
        content_models = {
            'pages': Page,
            'essays': Essay,
            'characters': Character,
            'stories': Story,
            'images': Image,
        }
        
        for type_name, model_class in content_models.items():
            # Skip if content type not requested
            if requested_types and type_name not in requested_types:
                continue
            
            # Start with world filter
            queryset = model_class.objects.filter(world=world)
            
            # Apply author filter
            if author_username:
                queryset = queryset.filter(author__username__icontains=author_username)
            
            # Apply date range filters
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)
            if end_date:
                queryset = queryset.filter(created_at__lte=end_date)
            
            # Apply search filter
            if search_param:
                queryset = queryset.filter(
                    Q(title__icontains=search_param) | 
                    Q(content__icontains=search_param)
                )
            
            # Apply tags filter
            if tags_param:
                tag_names = [name.strip().lower() for name in tags_param.split(',') if name.strip()]
                if tag_names:
                    # Get content that has at least one of the specified tags
                    tagged_content = model_class.get_content_by_tags(world, tag_names, match_all=False)
                    queryset = queryset.filter(id__in=tagged_content.values_list('id', flat=True))
            
            # Optimize queries
            queryset = queryset.select_related('author', 'world')
            
            # Add to collection
            all_content.extend(list(queryset))
        
        # Sort by creation date (newest first)
        all_content.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        total_count = len(all_content)
        paginated_content = all_content[offset:offset + limit]
        
        # Convert to serializable format
        timeline_data = []
        for content in paginated_content:
            timeline_data.append({
                'id': content.id,
                'title': content.title,
                'content_type': content.__class__.__name__.lower(),
                'type': content.__class__.__name__.lower(),  # Keep for backward compatibility
                'author': {
                    'id': content.author.id,
                    'username': content.author.username,
                    'first_name': content.author.first_name,
                    'last_name': content.author.last_name
                },
                'created_at': content.created_at,
                'timeline_position': content.created_at.isoformat(),
                'summary': getattr(content, 'summary', '')[:200] if hasattr(content, 'summary') else content.content[:200],
                'tags': [tag.name for tag in content.get_tags()],
                'url': f'/api/worlds/{world.id}/{content.__class__.__name__.lower()}s/{content.id}/'
            })

        return Response({
            'world': {
                'id': world.id,
                'title': world.title
            },
            'timeline': timeline_data,
            'pagination': {
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_next': offset + limit < total_count,
                'has_previous': offset > 0
            },
            'filters_applied': {
                'content_types': requested_types or 'all',
                'author': author_username or 'all',
                'tags': tags_param.split(',') if tags_param else [],
                'start_date': start_date_param or None,
                'end_date': end_date_param or None,
                'search': search_param or None
            }
        })

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get detailed statistics for the world.
        """
        world = self.get_object()
        
        # Content counts
        content_counts = {
            'pages': world.page_entries.count(),
            'essays': world.essay_entries.count(),
            'characters': world.character_entries.count(),
            'stories': world.story_entries.count(),
            'images': world.image_entries.count(),
        }
        content_counts['total'] = sum(content_counts.values())
        
        # Popular tags
        popular_tags = world.get_popular_tags(limit=10)
        
        # Recent activity (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        recent_activity = {
            'pages': world.page_entries.filter(created_at__gte=thirty_days_ago).count(),
            'essays': world.essay_entries.filter(created_at__gte=thirty_days_ago).count(),
            'characters': world.character_entries.filter(created_at__gte=thirty_days_ago).count(),
            'stories': world.story_entries.filter(created_at__gte=thirty_days_ago).count(),
            'images': world.image_entries.filter(created_at__gte=thirty_days_ago).count(),
        }
        recent_activity['total'] = sum(recent_activity.values())
        
        # Contributor count
        from django.contrib.auth.models import User
        contributor_count = User.objects.filter(
            Q(page_authored__world=world) |
            Q(essay_authored__world=world) |
            Q(character_authored__world=world) |
            Q(story_authored__world=world) |
            Q(image_authored__world=world)
        ).distinct().count()

        return Response({
            'world': {
                'id': world.id,
                'title': world.title,
                'creator': world.creator.username,
                'created_at': world.created_at,
                'is_public': world.is_public
            },
            'content_counts': content_counts,
            'contributor_count': contributor_count,
            'popular_tags': [{'name': tag.name, 'usage_count': count} for tag, count in popular_tags],
            'recent_activity': recent_activity
        })
    
    @action(detail=True, methods=['get'])
    def search(self, request, pk=None):
        """
        Advanced search functionality within a world.
        
        Query parameters:
        - q: Search query (searches title and content)
        - content_types: Comma-separated list of content types to search
        - author: Filter by author username
        - tags: Comma-separated list of tags
        - match_all_tags: If true, content must have ALL specified tags
        - sort: Sort order ('relevance', 'date_desc', 'date_asc', 'title')
        - limit: Number of results to return (default: 20, max: 100)
        """
        world = self.get_object()
        
        # Parse query parameters
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({
                'error': 'Search query required',
                'message': 'Please provide a search query using the "q" parameter'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        content_types_param = request.query_params.get('content_types', '')
        author_username = request.query_params.get('author', '')
        tags_param = request.query_params.get('tags', '')
        match_all_tags = request.query_params.get('match_all_tags', 'false').lower() in ('true', '1', 'yes')
        sort_param = request.query_params.get('sort', 'relevance')
        limit = min(int(request.query_params.get('limit', 20)), 100)
        
        # Parse content types
        if content_types_param:
            requested_types = [t.strip().lower() for t in content_types_param.split(',')]
            type_mapping = {
                'page': 'pages', 'essay': 'essays', 'character': 'characters',
                'story': 'stories', 'image': 'images'
            }
            requested_types = [type_mapping.get(t, t) for t in requested_types]
        else:
            requested_types = []
        
        # Search across content types
        search_results = []
        content_models = {
            'pages': Page,
            'essays': Essay,
            'characters': Character,
            'stories': Story,
            'images': Image,
        }
        
        for type_name, model_class in content_models.items():
            if requested_types and type_name not in requested_types:
                continue
            
            # Build search query
            queryset = model_class.objects.filter(world=world)
            
            # Text search
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
            
            # Apply filters
            if author_username:
                queryset = queryset.filter(author__username__icontains=author_username)
            
            # Apply tags filter
            if tags_param:
                tag_names = [name.strip().lower() for name in tags_param.split(',') if name.strip()]
                if tag_names:
                    tagged_content = model_class.get_content_by_tags(world, tag_names, match_all=match_all_tags)
                    queryset = queryset.filter(id__in=tagged_content.values_list('id', flat=True))
            
            # Optimize queries
            queryset = queryset.select_related('author', 'world')
            
            # Add relevance scoring (simple implementation)
            from datetime import datetime
            for item in queryset:
                relevance_score = 0
                
                # Title matches are more relevant
                if query.lower() in item.title.lower():
                    relevance_score += 10
                
                # Content matches
                content_matches = item.content.lower().count(query.lower())
                relevance_score += content_matches
                
                # Recent content is slightly more relevant
                days_old = (datetime.now() - item.created_at.replace(tzinfo=None)).days
                recency_score = max(0, 30 - days_old) / 30  # Boost for content less than 30 days old
                relevance_score += recency_score
                
                search_results.append({
                    'content': item,
                    'relevance_score': relevance_score,
                    'content_type': type_name[:-1]  # Remove 's' from plural
                })
        
        # Sort results
        if sort_param == 'relevance':
            search_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        elif sort_param == 'date_desc':
            search_results.sort(key=lambda x: x['content'].created_at, reverse=True)
        elif sort_param == 'date_asc':
            search_results.sort(key=lambda x: x['content'].created_at)
        elif sort_param == 'title':
            search_results.sort(key=lambda x: x['content'].title.lower())
        
        # Limit results
        search_results = search_results[:limit]
        
        # Serialize results
        results = []
        for result in search_results:
            content = result['content']
            results.append({
                'id': content.id,
                'title': content.title,
                'content_type': result['content_type'],
                'author': {
                    'id': content.author.id,
                    'username': content.author.username,
                    'first_name': content.author.first_name,
                    'last_name': content.author.last_name
                },
                'created_at': content.created_at,
                'relevance_score': result['relevance_score'],
                'summary': getattr(content, 'summary', '')[:200] if hasattr(content, 'summary') else content.content[:200],
                'tags': [tag.name for tag in content.get_tags()],
                'url': f'/api/worlds/{world.id}/{result["content_type"]}s/{content.id}/'
            })
        
        return Response({
            'query': query,
            'results': results,
            'total_results': len(results),
            'search_parameters': {
                'content_types': requested_types or 'all',
                'author': author_username or 'all',
                'tags': tags_param.split(',') if tags_param else [],
                'match_all_tags': match_all_tags,
                'sort': sort_param
            },
            'world': {
                'id': world.id,
                'title': world.title
            }
        })
    
    @action(detail=True, methods=['get'])
    def related_content(self, request, pk=None):
        """
        Discover related content based on tags and links.
        
        Query parameters:
        - content_type: Type of the source content (page, essay, character, story, image)
        - content_id: ID of the source content
        - relation_types: Comma-separated list of relation types ('tags', 'links', 'author')
        - limit: Number of related items to return per type (default: 10)
        """
        world = self.get_object()
        
        content_type_param = request.query_params.get('content_type', '').lower()
        content_id = request.query_params.get('content_id', '')
        relation_types_param = request.query_params.get('relation_types', 'tags,links')
        limit = min(int(request.query_params.get('limit', 10)), 50)
        
        if not content_type_param or not content_id:
            return Response({
                'error': 'Missing parameters',
                'message': 'Please provide content_type and content_id parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the source content
        content_models = {
            'pages': Page,
            'essays': Essay,
            'characters': Character,
            'stories': Story,
            'images': Image,
        }
        
        type_mapping = {
            'page': 'pages', 'essay': 'essays', 'character': 'characters',
            'story': 'stories', 'image': 'images'
        }
        
        content_type_key = type_mapping.get(content_type_param)
        if not content_type_key or content_type_key not in content_models:
            return Response({
                'error': 'Invalid content type',
                'message': f'Content type must be one of: {", ".join(type_mapping.keys())}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        model_class = content_models[content_type_key]
        
        try:
            source_content = model_class.objects.get(id=content_id, world=world)
        except model_class.DoesNotExist:
            return Response({
                'error': 'Content not found',
                'message': 'The specified content does not exist in this world'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Parse relation types
        relation_types = [t.strip() for t in relation_types_param.split(',')]
        
        related_content = {
            'source_content': {
                'id': source_content.id,
                'title': source_content.title,
                'content_type': content_type_param,
                'author': {
                    'id': source_content.author.id,
                    'username': source_content.author.username,
                    'first_name': source_content.author.first_name,
                    'last_name': source_content.author.last_name
                },
                'created_at': source_content.created_at
            },
            'related_by_tags': [],
            'related_by_links': [],
            'related_by_author': []
        }
        
        # Find content related by tags
        if 'tags' in relation_types:
            source_tags = source_content.get_tags()
            if source_tags.exists():
                tag_names = [tag.name for tag in source_tags]
                
                # Find other content with similar tags
                for type_name, rel_model_class in content_models.items():
                    related_by_tags = rel_model_class.get_content_by_tags(world, tag_names, match_all=False)
                    # Exclude the source content itself (only if same content type)
                    if type_name == content_type_key:
                        related_by_tags = related_by_tags.exclude(id=source_content.id)
                    
                    # Score by number of shared tags
                    for item in related_by_tags[:limit]:
                        item_tags = set(tag.name for tag in item.get_tags())
                        shared_tags = set(tag_names) & item_tags
                        
                        related_content['related_by_tags'].append({
                            'id': item.id,
                            'title': item.title,
                            'content_type': type_name[:-1],
                            'author': {
                                'id': item.author.id,
                                'username': item.author.username,
                                'first_name': item.author.first_name,
                                'last_name': item.author.last_name
                            },
                            'created_at': item.created_at,
                            'shared_tags': list(shared_tags),
                            'shared_tag_count': len(shared_tags),
                            'url': f'/api/worlds/{world.id}/{type_name}/{item.id}/'
                        })
                
                # Sort by number of shared tags
                related_content['related_by_tags'].sort(
                    key=lambda x: x['shared_tag_count'], 
                    reverse=True
                )
                related_content['related_by_tags'] = related_content['related_by_tags'][:limit]
        
        # Find content related by links
        if 'links' in relation_types:
            linked_content = source_content.get_linked_content()
            linking_content = source_content.get_content_linking_to_this()
            
            all_linked = list(linked_content) + list(linking_content)
            
            for item in all_linked[:limit]:
                # Determine the content type for this item
                item_type = item.__class__.__name__.lower()
                
                related_content['related_by_links'].append({
                    'id': item.id,
                    'title': item.title,
                    'content_type': item_type,
                    'author': {
                        'id': item.author.id,
                        'username': item.author.username,
                        'first_name': item.author.first_name,
                        'last_name': item.author.last_name
                    },
                    'created_at': item.created_at,
                    'url': f'/api/worlds/{world.id}/{item_type}s/{item.id}/'
                })
        
        # Find content by same author
        if 'author' in relation_types:
            for type_name, rel_model_class in content_models.items():
                author_content = rel_model_class.objects.filter(
                    world=world, 
                    author=source_content.author
                ).order_by('-created_at')
                
                # Only exclude if it's the same content type and same ID
                if type_name == content_type_key:
                    author_content = author_content.exclude(id=source_content.id)
                
                for item in author_content[:limit]:
                    related_content['related_by_author'].append({
                        'id': item.id,
                        'title': item.title,
                        'content_type': type_name[:-1],
                        'author': {
                            'id': item.author.id,
                            'username': item.author.username,
                            'first_name': item.author.first_name,
                            'last_name': item.author.last_name
                        },
                        'created_at': item.created_at,
                        'url': f'/api/worlds/{world.id}/{type_name}/{item.id}/'
                    })
            
            # Sort by creation date (newest first)
            related_content['related_by_author'].sort(
                key=lambda x: x['created_at'], 
                reverse=True
            )
            related_content['related_by_author'] = related_content['related_by_author'][:limit]
        
        return Response(related_content)
    
    @action(detail=True, methods=['get'])
    def attribution_report(self, request, pk=None):
        """
        Generate a detailed attribution report showing how contributors reference each other's work.
        This helps track collaborative patterns and proper attribution practices.
        """
        world = self.get_object()
        
        # Get all content in the world
        all_content = world.get_content_timeline()
        
        # Build attribution network
        attribution_network = {}
        cross_references = []
        
        for content in all_content:
            author_username = content.author.username
            
            if author_username not in attribution_network:
                attribution_network[author_username] = {
                    'authored_count': 0,
                    'references_to_others': 0,
                    'references_from_others': 0,
                    'collaborates_with': set(),
                    'content_types': set()
                }
            
            attribution_network[author_username]['authored_count'] += 1
            attribution_network[author_username]['content_types'].add(content.__class__.__name__.lower())
            
            # Check links to other authors' content
            linked_content = content.get_linked_content()
            for linked in linked_content:
                if linked.author.username != author_username:
                    attribution_network[author_username]['references_to_others'] += 1
                    attribution_network[author_username]['collaborates_with'].add(linked.author.username)
                    
                    cross_references.append({
                        'from_author': author_username,
                        'to_author': linked.author.username,
                        'from_content': {
                            'id': content.id,
                            'title': content.title,
                            'type': content.__class__.__name__.lower()
                        },
                        'to_content': {
                            'id': linked.id,
                            'title': linked.title,
                            'type': linked.__class__.__name__.lower()
                        },
                        'created_at': content.created_at
                    })
            
            # Check links from other authors' content
            linking_content = content.get_content_linking_to_this()
            for linking in linking_content:
                if linking.author.username != author_username:
                    attribution_network[author_username]['references_from_others'] += 1
                    attribution_network[author_username]['collaborates_with'].add(linking.author.username)
        
        # Convert sets to lists for JSON serialization
        for author_data in attribution_network.values():
            author_data['collaborates_with'] = list(author_data['collaborates_with'])
            author_data['content_types'] = list(author_data['content_types'])
        
        # Calculate collaboration metrics
        total_authors = len(attribution_network)
        total_cross_references = len(cross_references)
        collaborative_authors = len([data for data in attribution_network.values() if len(data['collaborates_with']) > 0])
        
        # Find most collaborative pairs
        collaboration_pairs = {}
        for ref in cross_references:
            pair_key = tuple(sorted([ref['from_author'], ref['to_author']]))
            if pair_key not in collaboration_pairs:
                collaboration_pairs[pair_key] = 0
            collaboration_pairs[pair_key] += 1
        
        top_collaborations = sorted(collaboration_pairs.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return Response({
            'world': {
                'id': world.id,
                'title': world.title,
                'creator': world.creator.username
            },
            'attribution_network': attribution_network,
            'cross_references': cross_references,
            'collaboration_metrics': {
                'total_authors': total_authors,
                'collaborative_authors': collaborative_authors,
                'collaboration_percentage': round((collaborative_authors / max(total_authors, 1)) * 100, 2),
                'total_cross_references': total_cross_references,
                'average_references_per_author': round(total_cross_references / max(total_authors, 1), 2)
            },
            'top_collaborations': [
                {
                    'authors': list(pair[0]),
                    'reference_count': pair[1],
                    'collaboration_strength': 'high' if pair[1] >= 5 else 'medium' if pair[1] >= 2 else 'low'
                }
                for pair in top_collaborations
            ],
            'attribution_quality': {
                'has_cross_references': total_cross_references > 0,
                'is_well_attributed': total_cross_references > total_authors,
                'collaboration_health': 'excellent' if collaborative_authors / max(total_authors, 1) > 0.7 else 
                                      'good' if collaborative_authors / max(total_authors, 1) > 0.4 else 
                                      'needs_improvement'
            }
        })