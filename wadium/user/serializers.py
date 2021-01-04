from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied

from .models import UserProfile, EmailAuth
from story.models import Story


class UserSerializer(serializers.ModelSerializer):
    TEST = 'TEST'
    OAUTH = 'OAUTH'
    EMAIL = 'EMAIL'
    INIT = 'INIT'
    CHECK = 'CHECK'
    CREATE = 'CREATE'
    AUTH_TYPE_CHOICES = [TEST, OAUTH, EMAIL, ]
    auth_type = serializers.ChoiceField(write_only=True, choices=AUTH_TYPE_CHOICES,
                                        error_messages={
                                            'invalid_choice': f'auth_type should be one of {AUTH_TYPE_CHOICES}'})
    REQ_TYPE_CHOICES = [INIT, CHECK, CREATE, ]
    req_type = serializers.ChoiceField(required=False, write_only=True, choices=REQ_TYPE_CHOICES,
                                       error_messages={
                                           'invalid_choice': f'req_type should be one of {REQ_TYPE_CHOICES}'})
    name = serializers.CharField(source='userprofile.name', required=False)
    email = serializers.EmailField(source='userprofile.email', write_only=True, required=False)
    profile_image = serializers.URLField(source='userprofile.profile_image', required=False)
    access_token = serializers.CharField(required=False, write_only=True, min_length=12, max_length=12)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'req_type',
            'username',
            'email',
            'name',
            'profile_image',
            'access_token'
        )
        extra_kwargs = {'username': {'required': False}}

    def validate_auth_type(self, value):
        if value in (self.OAUTH,):
            raise serializers.ValidationError(f'{value} is not yet implemented.')
        else:
            return value

    def validate(self, data):
        if data['auth_type'] == self.TEST:
            if 'username' not in data:
                raise serializers.ValidationError('username is required')
            required = {'name', 'email'}
            missing = required - set(data.get('userprofile', {}))
            if missing:
                raise serializers.ValidationError(f'{missing} is required')
        elif data['auth_type'] == self.EMAIL:
            if 'req_type' not in data:
                raise serializers.ValidationError('req_type is required')
            req_type = data['req_type']
            if req_type == self.INIT and 'email' not in data.get('userprofile', {}):
                raise serializers.ValidationError('email is required')
            elif req_type == self.CHECK and 'access_token' not in data:
                raise serializers.ValidationError('access_token is required')
            elif req_type == self.CREATE:
                if 'access_token' not in data:
                    raise serializers.ValidationError('access_token is required')
                if 'username' not in data:
                    raise serializers.ValidationError('username is required')
                required = {'name', 'email'}
                missing = required - set(data.get('userprofile', {}))
                if missing:
                    raise serializers.ValidationError(f'{missing} is required')
        return data

    def create(self, validated_data):
        auth_type = validated_data.pop('auth_type')
        if auth_type == self.TEST:
            user = UserProfile.create_user(**validated_data, test_user=True)
        elif auth_type == self.EMAIL and validated_data['req_type'] == self.CREATE:
            email_auth = get_object_or_404(EmailAuth, token=validated_data['access_token'])
            email_auth.is_valid(must_be_email=False)
            userprofile = validated_data['userprofile']
            if userprofile['email'] != email_auth.email_address.email:
                raise serializers.ValidationError({'email': 'Email does not match.'})
            user = UserProfile.create_user(validated_data['username'], userprofile, test_user=False)
        else:
            raise ValueError()
        Token.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        raise NotImplementedError()


class UserLoginSerializer(serializers.ModelSerializer):
    TEST = 'TEST'
    OAUTH = 'OAUTH'
    EMAIL = 'EMAIL'
    INIT = 'INIT'
    LOGIN = 'LOGIN'
    AUTH_TYPE_CHOICES = [TEST, OAUTH, EMAIL, ]
    auth_type = serializers.ChoiceField(write_only=True, choices=AUTH_TYPE_CHOICES,
                                        error_messages={
                                            'invalid_choice': f'auth_type should be one of {AUTH_TYPE_CHOICES}'})
    REQ_TYPE_CHOICES = [INIT, LOGIN, ]
    req_type = serializers.ChoiceField(required=False, write_only=True, choices=REQ_TYPE_CHOICES,
                                       error_messages={
                                           'invalid_choice': f'req_type should be one of {REQ_TYPE_CHOICES}'})
    username = serializers.CharField(required=False, write_only=True)
    email = serializers.EmailField(required=False, write_only=True)
    access_token = serializers.CharField(required=False, write_only=True, min_length=12, max_length=12)

    class Meta:
        model = User
        fields = (
            'auth_type',
            'req_type',
            'username',
            'email',
            'access_token',
        )

    def validate_auth_type(self, value):
        if value in (self.OAUTH,):
            raise serializers.ValidationError(f'{value} is not yet implemented.')
        else:
            return value

    def validate(self, data):
        if data['auth_type'] == self.TEST:
            if 'username' not in data:
                raise serializers.ValidationError('username is required')
        elif data['auth_type'] == self.EMAIL:
            if 'req_type' not in data:
                raise serializers.ValidationError('req_type is required')
            elif data['req_type'] == self.INIT and 'email' not in data:
                raise serializers.ValidationError('email is required')
            elif data['req_type'] == self.LOGIN and 'access_token' not in data:
                raise serializers.ValidationError('access_token is required')
        return data

    def get_user(self, validated_data):
        """
        Retrieve User.
        """
        auth_type = validated_data.pop('auth_type')
        if auth_type == self.TEST:
            try:
                user = User.objects.get(username=validated_data['username'])
            except User.DoesNotExist:
                raise NotFound({
                    "username": ["A user with that username does not exist."]
                })
            else:
                if user.password == UserProfile.TEST_PW:
                    return user
                else:
                    raise PermissionDenied({
                        "username": ["A user with that username is not a test user."]
                    })
        elif auth_type == self.EMAIL:
            req_type = validated_data['req_type']
            if req_type == self.INIT:
                raise ValueError('Cannot get user from EMAIL INIT request')
            elif req_type == self.LOGIN:
                email_auth = get_object_or_404(EmailAuth, token=validated_data['access_token'])
                email_auth.is_valid(must_be_email=True)
                return email_auth.email_address.user
        else:
            raise NotImplementedError()


class UserSelfSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    bio = serializers.CharField(required=False)
    profile_image = serializers.URLField(required=False)
    email = serializers.CharField(read_only=True)
    connection = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'name',
            'bio',
            'profile_image',
            'email',
            'connection'
        )

    def get_connection(self, user):
        return UserSocialSerializer(user, context=self.context).data


class UserSocialSerializer(serializers.ModelSerializer):
    google = serializers.CharField(source='user.usergoogle.google_sub', required=False)
    facebook = serializers.CharField(source='user.userfacebook.facebook_sub', required=False)

    class Meta:
        model = User
        fields = (
            'google',
            'facebook',
        )


class MyStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = (
            'id',
            'title',
            'subtitle',
            'created_at',
            'updated_at',
            'published_at',
            'published'
        )
        read_only_fields = fields


class UserStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = (
            'id',
            'title',
            'subtitle',
            'body',
            'published_at',
        )
        read_only_fields = fields
