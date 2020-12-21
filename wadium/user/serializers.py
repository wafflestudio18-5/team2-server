from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import UserProfile, EmailAddress

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
#class UserSearchSerializer(serializers.ModelSerializer):

class UserUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='userprofile.name')
    bio = serializers.CharField(source='userprofile.bio',required=False)
    profile_image = serializers.URLField(source='userprofile.profile_image', required=False)
    #url = serializers.URLField(source='userprofile.url', required=False)
    email = serializers.CharField(source='userprofile.user.email')
    # connection =  serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = (
            'id',
            'name',
            'bio',
            'profile_image',
            #'url',
            'email',
            #'connection'
        )
