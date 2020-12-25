from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Story, StoryBlock, StoryComment, StoryRead, StoryTag
from .serializers import StorySerializer

class StoryViewSet(viewsets.GenericViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = (IsAuthenticated(), )

    def get_permissions(self):
        if self.action in ('retrieve', 'get'):
            return (AllowAny(), )
        return self.permission_classes

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        story = self.get_object()
        serializer = self.get_serializer(story, data=request.data)
        serializer = serializer.is_valid(raise_exception=True)
        serializer.update(story, serializer.validated_data)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        story = self.get_object()
        return Response(self.get_serializer(story).data)
    
    def get(self, request):
        return None