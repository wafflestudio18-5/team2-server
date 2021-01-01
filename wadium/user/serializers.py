from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, PermissionDenied

from .models import UserProfile, EmailAddress, UserSocial, UserGoogle, UserFacebook


class UserSerializer(serializers.ModelSerializer):
    TEST = 'TEST'
    OAUTH = 'OAUTH'
    EMAIL = 'EMAIL'
    AUTH_TYPE_CHOICES = [TEST, OAUTH, EMAIL, ]
    auth_type = serializers.ChoiceField(write_only=True, choices=AUTH_TYPE_CHOICES,
                                        error_messages={
                                            'invalid_choice': f'auth_type should be one of {AUTH_TYPE_CHOICES}'})
    name = serializers.CharField(source='userprofile.name')
    email = serializers.EmailField(source='userprofile.email', write_only=True)
    profile_image = serializers.URLField(source='userprofile.profile_image', required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'username',
            'email',
            'name',
            'profile_image',
        )

    def validate_auth_type(self, value):
        if value in (self.OAUTH, self.EMAIL):
            raise serializers.ValidationError(f'{value} is not yet implemented.')
        else:
            return value

    def validate_email(self, value):
        try:
            email_address = EmailAddress.objects.get(email=value)
        except EmailAddress.DoesNotExist:
            return value
        if email_address.available:
            return value
        else:
            raise serializers.ValidationError('A user with that email already exists.')

    def create(self, validated_data):
        auth_type = validated_data.pop('auth_type')
        user = UserProfile.create_user(**validated_data, test_user=auth_type == 'TEST')
        Token.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        raise NotImplementedError()


class UserLoginSerializer(serializers.ModelSerializer):
    TEST = 'TEST'
    OAUTH = 'OAUTH'
    EMAIL = 'EMAIL'
    AUTH_TYPE_CHOICES = [TEST, OAUTH, EMAIL, ]
    auth_type = serializers.ChoiceField(write_only=True, choices=AUTH_TYPE_CHOICES,
                                        error_messages={
                                            'invalid_choice': f'auth_type should be one of {AUTH_TYPE_CHOICES}'})
    username = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'auth_type',
            'username',
        )

    def validate_auth_type(self, value):
        if value in (self.OAUTH, self.EMAIL):
            raise serializers.ValidationError(f'{value} is not yet implemented.')
        else:
            return value

    def get_user(self, validated_data):
        """
        Retrieve User.
        """
        auth_type = validated_data.pop('auth_type')
        if auth_type == 'TEST':
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
        else:
            raise NotImplementedError()

#자신의 정보 확인/수정
class UserSelfSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    bio = serializers.CharField(required=False)
    profile_image = serializers.URLField(required=False)
    email = serializers.CharField()
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
    #google = serializers.SerializerMethodField()
    #facebook = serializers.SerializerMethodField()
    google = serializers.CharField(source='user.usergoogle.google_sub', required=False)
    facebook = serializers.CharField(source='user.userfacebook.facebook_sub', required=False)
    class Meta:
        model = User
        fields = (
            'google',
            'facebook',
        )

#    def get_google(self, user):
#        return UserGoogle.objects.filter(user=user.user).last()

#    def get_facebook(self, user):
#        return UserFacebook.objects.filter(user=user.user).last()

