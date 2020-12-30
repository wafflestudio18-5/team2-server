from rest_framework import serializers
from .models import Story

class StorySerializer(serializers.ModelSerializer):
    writer = serializers.IntegerField(source='writer.id', read_only=True)
    title = serializers.CharField(default='Untitled', allow_blank=True)
    subtitle = serializers.CharField()
    body = serializers.JSONField()
    featured_image = serializers.URLField(allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    published = serializers.BooleanField(default=False, read_only=True)
    published_at = serializers.DateTimeField(allow_null=True, default=None, read_only=True)

    class Meta: 
        model = Story
        fields = (
            '__all__'
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
