from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from user.serializers import UserSerializer, UserUpdateSerializer
from user.models import UserProfile

class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ('create', 'login', 'list', 'about'):
            return (AllowAny(),)
        return super(UserViewSet, self).get_permissions()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        data = serializer.data
        data['token'] = user.auth_token.key
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['PUT'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            data = self.get_serializer(user).data
            token, created = Token.objects.get_or_create(user=user)
            data['token'] = token.key
            return Response(data)
        return Response({"error": "Wrong username or wrong password"}, status=status.HTTP_403_FORBIDDEN)

    def list(self, request):
        username = request.query_params.get('username')
        cache_key = 'user-list'
        data = cache.get(cache_key)
        if not data:
            user = self.get_queryset()
            if username:
                user = user.filter(username__icontains=username)
                data = self.get_serializer(user, many=True).data
            else:
                data = self.get_serializer(user, many=True).data
                cache.set(cache_key, data, timeout=30)
        else:
            print('cache miss')
        return Response(data)

    @action(detail=True, methods=['GET'])
    def about(self, request, pk):
        user = request.user if pk == 'me' else self.get_object()
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        if pk != 'me':
            return Response({"error": "Can't show other user's information"}, status=status.HTTP_403_FORBIDDEN)
        user = request.user
        u = User.objects.get(id=user.id)
        profile = UserProfile.objects.get(user=u)
        serializer = self.get_serializer(profile)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        if pk != 'me':
            return Response({"error": "Can't update other user's information"}, status=status.HTTP_403_FORBIDDEN)

        user = request.user
        u = User.objects.get(id = user.id)
        profile = UserProfile.objects.get(user=u)
        data = request.data.copy()

        serializer = self.get_serializer(profile, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(profile, serializer.validated_data)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'retrieve':
            return UserUpdateSerializer
        else:
            return UserSerializer


































