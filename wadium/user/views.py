from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, UserLoginSerializer
from .models import EmailAddress, EmailAuth, UserProfile

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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
        else:
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

        login(request, user)

        data = self.get_serializer(instance=user).data
        token, created = Token.objects.get_or_create(user=user)
        data['token'] = token.key
        return Response(data=data)

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
