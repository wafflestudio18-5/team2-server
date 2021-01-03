from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache

from .models import Story, StoryComment, StoryRead, StoryTag
from .serializers import StorySerializer, SimpleStorySerializer
from .paginators import StoryPagination


class StoryViewSet(viewsets.GenericViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = (IsAuthenticated(),)
    pagination_class = StoryPagination

    cache_story_page1_key = 'story:list-1'
    cache_story_main_key = 'story:main'
    cache_story_trending_key = 'story:trending'
    cache_timeout = 60
    cache_timeout_long = 600

    def get_serializer_class(self):
        if self.action in ('list', 'main', 'trending'):
            return SimpleStorySerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ('retrieve', 'list', 'main', 'trending'):
            return (AllowAny(),)
        return self.permission_classes

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        story = self.get_object()
        if story.writer != request.user:
            return Response({'error': "You can't edit others' story"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(story, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(story, serializer.validated_data)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        story = self.get_object()
        return Response(self.get_serializer(story).data)

    def list(self, request):
        queryset = self.get_queryset(). \
            filter(published=True). \
            order_by('-published_at'). \
            defer('body'). \
            select_related('writer'). \
            prefetch_related('writer__userprofile')
        is_cacheable = True
        if 'title' in request.query_params:
            title = request.query_params.get('title')
            queryset = queryset.filter(title__icontains=title)
            is_cacheable = False
        if 'tag' in request.query_params:
            return Response({'error': 'tag query is not implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)
            # is_cacheable = False
        if is_cacheable:
            queryset = queryset.filter(main_order=None, trending_order=None)
        if is_cacheable and request.query_params.get('page', 1) in (1, '1'):
            cached_data = cache.get(self.cache_story_page1_key)
            if cached_data is None:
                page = self.paginate_queryset(queryset)
                assert page is not None
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                data = response.data
                cache.set(self.cache_story_page1_key, data, timeout=self.cache_timeout)
                return response
            else:
                data = cached_data
                return Response(data)

        page = self.paginate_queryset(queryset)
        assert page is not None
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=False)
    def main(self, request):
        cached_data = cache.get(self.cache_story_main_key)
        if cached_data is None:
            queryset = self.get_queryset(). \
                filter(published=True). \
                filter(main_order__gte=1, main_order__lte=5). \
                order_by('main_order'). \
                defer('body'). \
                select_related('writer'). \
                prefetch_related('writer__userprofile')
            data = self.get_serializer(queryset, many=True).data
            cache.set(self.cache_story_main_key, data, timeout=self.cache_timeout_long)
        else:
            data = cached_data
        return Response(data)

    @action(methods=['GET'], detail=False)
    def trending(self, request):
        cached_data = cache.get(self.cache_story_trending_key)
        if cached_data is None:
            queryset = self.get_queryset(). \
                filter(published=True). \
                filter(trending_order__gte=1, trending_order__lte=6). \
                order_by('trending_order'). \
                defer('body'). \
                select_related('writer'). \
                prefetch_related('writer__userprofile')
            data = self.get_serializer(queryset, many=True).data
            cache.set(self.cache_story_trending_key, data, timeout=self.cache_timeout_long)
        else:
            data = cached_data
        return Response(data)

    @action(methods=['POST'], detail=True)
    def publish(self, request, pk=None):
        story = self.get_object()
        if story.writer != request.user:
            return Response({'error': "You can't publish others' story"}, status=status.HTTP_403_FORBIDDEN)
        if story.published:
            story.published_at = None
            story.published = False
        else:
            story.published_at = timezone.now()
            story.published = True
        story.save()
        return Response(self.get_serializer(story).data)

    def destroy(self, request, pk=None):
        story = self.get_object()
        if story.writer != request.user:
            return Response({'error': "You can't delete others' story"}, status=status.HTTP_403_FORBIDDEN)
        story.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
