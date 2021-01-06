from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, UserLoginSerializer, UserSelfSerializer, UserSocialSerializer, MyStorySerializer, UserStorySerializer
from .models import EmailAddress, EmailAuth, UserProfile
from .permissions import UserAccessPermission
from story.paginators import StoryPagination

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
import requests

from django.conf import settings
#from rest_framework.decorators import permission_classes

class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StoryPagination

    def get_permissions(self):
        if self.action == 'story':
            self.permission_classes = [UserAccessPermission]
        elif self.action == 'logout':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super(UserViewSet, self).get_permissions()

    def get_serializer_class(self):
        if self.action == 'story':
            if self.kwargs['pk'] == 'me':
                return MyStorySerializer
            else:
                return UserStorySerializer
        elif self.action == 'update' or self.action == 'retrieve':
            return UserSelfSerializer
        else:
            return self.serializer_class

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if data['auth_type'] == UserSerializer.TEST:
            user = serializer.save()
        elif data['auth_type'] == UserSerializer.EMAIL:
            if data['req_type'] == UserSerializer.INIT:
                with transaction.atomic():
                    email_address, created = EmailAddress.objects.get_or_create(email=data['userprofile']['email'])
                    email_auth = EmailAuth.objects.create(email_address=email_address)
                    sent = email_auth.send(signup=email_address.available)
                    if sent:
                        return Response(status=status.HTTP_204_NO_CONTENT)
                    else:
                        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
            elif data['req_type'] == UserSerializer.CHECK:
                email_auth = get_object_or_404(EmailAuth, token=data['access_token'])
                email_auth.is_valid(must_be_email=True)
                email_address = email_auth.email_address
                if not email_address.available:
                    return Response({'error': 'Associated email address is not available'},
                                    status=status.HTTP_400_BAD_REQUEST)
                new_token = EmailAuth.objects.create(
                    email_address=email_address,
                    expires_at=timezone.now() + timezone.timedelta(minutes=10),
                ).token
                return Response({
                    'email': email_address.email,
                    'username': UserProfile.get_unique_username(email_address.email),
                    'access_token': new_token
                })
            elif data['req_type'] == UserSerializer.CREATE:
                user = serializer.save()
        elif data['auth_type'] == UserSerializer.OAUTH:
            pass
        else:
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

        login(request, user)
        data = serializer.data
        data['token'] = user.auth_token.key
        return Response(data=data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['POST'])
    def login(self, request):
        login_serializer = UserLoginSerializer(data=request.data)
        login_serializer.is_valid(raise_exception=True)
        data = login_serializer.validated_data
        if data['auth_type'] == UserLoginSerializer.TEST:
            user = login_serializer.get_user(data)
        elif data['auth_type'] == UserLoginSerializer.EMAIL:
            if data['req_type'] == UserLoginSerializer.INIT:
                with transaction.atomic():
                    email_address = get_object_or_404(EmailAddress, email=data['email'])
                    if email_address.available:
                        return Response(data={
                            'email': 'No user is associated with given email'
                        }, status=status.HTTP_404_NOT_FOUND)
                    email_auth = EmailAuth.objects.create(email_address=email_address)
                    sent = email_auth.send(signup=False)
                    if sent:
                        return Response(status=status.HTTP_204_NO_CONTENT)
                    else:
                        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
            elif data['req_type'] == UserLoginSerializer.LOGIN:
                user = login_serializer.get_user(data)
        elif data['auth_type'] == UserLoginSerializer.OAUTH:
            pass
        else:
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

        login(request, user)

        data = self.get_serializer(instance=user).data
        token, created = Token.objects.get_or_create(user=user)
        data['token'] = token.key
        return Response(data=data)

    @action(detail=False, methods=['POST'])
    def logout(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        username = request.query_params.get('username', '')
        if not username:
            return Response({
                'error': 'username query is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        users = self.get_queryset().filter(username__icontains=username).select_related('userprofile')
        if users.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(self.get_serializer(users, many=True).data)

    @action(detail=True, methods=['GET'])
    def about(self, request, pk):
        user = request.user if pk == 'me' else self.get_object()
        if user.is_authenticated:
            return Response(self.get_serializer(user).data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # 자신의 정보 확인
    def retrieve(self, request, pk=None):
        if pk != 'me':
            return Response({"error": "Can't show other user's information"}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_404_NOT_FOUND)
        profile = request.user.userprofile
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    # 자신의 정보 수정
    def update(self, request, pk=None):
        if pk != 'me':
            return Response({"error": "Can't update other user's information"}, status=status.HTTP_403_FORBIDDEN)

        profile = request.user.userprofile
        data = request.data

        serializer = self.get_serializer(profile, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(profile, serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    def story(self, request, pk=None):
        if pk == 'me':
            # /user/me/story/?public=[true|false]
            public_query = request.query_params.get('public')
            if public_query is None:
                return Response({
                    'error': "'public' is required."
                }, status=status.HTTP_400_BAD_REQUEST)
            if public_query in ('true', 'True', ' TRUE'):
                public = True
            elif public_query in ('false', 'False', 'FALSE'):
                public = False
            else:
                return Response({
                    'error': "'public' should either be 'true' or 'false'."
                }, status=status.HTTP_400_BAD_REQUEST)

            queryset = request.user.stories. \
                filter(published=public). \
                only(*MyStorySerializer.Meta.fields, 'writer')
            if public:
                queryset = queryset.order_by('-published_at')
            else:
                queryset = queryset.order_by('-updated_at')
            page = self.paginate_queryset(queryset)
            assert page is not None
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # /user/{user_id}/story/
        queryset = self.get_object().stories. \
            filter(published=True). \
            only(*UserStorySerializer.Meta.fields, 'writer'). \
            order_by('-published_at')
        if 'title' in request.query_params:
            title = request.query_params.get('title')
            queryset = queryset.filter(title__icontains=title)
        if 'tag' in request.query_params:
            return Response({'error': 'tag query is not implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)
        self.paginator.page_size = 5
        page = self.paginate_queryset(queryset)
        assert page is not None
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
