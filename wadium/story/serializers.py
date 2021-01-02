from rest_framework import serializers
from .models import Story
from user.serializers import UserSerializer

class StorySerializer(serializers.ModelSerializer):
    writer = UserSerializer(read_only=True)
    title = serializers.CharField(max_length=100, allow_blank=True)
    subtitle = serializers.CharField(max_length=140, allow_blank=True)
    body = serializers.JSONField()
    featured_image = serializers.URLField(allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    published = serializers.BooleanField(default=False, read_only=True)
    published_at = serializers.DateTimeField(allow_null=True, default=None, read_only=True)

    class Meta: 
        model = Story
        fields = (
            'id',
            'writer',
            'title',
            'subtitle',
            'body',
            'featured_image',
            'created_at',
            'updated_at',
            'published',
            'published_at',
        )
        
    def validate(self, data):
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['writer'] = user

        if validated_data['title'] == '':
            validated_data['title'] = 'Untitled'

        story = super(StorySerializer, self).create(validated_data)
        return story

    def update(self, instance, validated_data):
        if 'title' in validated_data and validated_data['title'] == '':
            validated_data['title'] = 'Untitled'

        story = super(StorySerializer, self).update(instance, validated_data)
        return story
