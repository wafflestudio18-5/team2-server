from rest_framework import serializers
from .models import Story, StoryComment, Tag, StoryTag
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


class SimpleStorySerializer(serializers.ModelSerializer):
    writer = UserSerializer(read_only=True)

    class Meta:
        model = Story
        fields = (
            'id',
            'writer',
            'title',
            'subtitle',
            'featured_image',
            'created_at',
            'published_at',
        )
        read_only_fields = fields

class CommentSerializer(serializers.ModelSerializer):
    writer = UserSerializer(read_only=True)
    story_id = serializers.IntegerField(source='story.id', read_only=True)

    class Meta:
        model = StoryComment
        fields = (
            'id',
            'story_id',
            'writer',
            'body',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at',)

    def create(self, validated_data):
        validated_data['writer'] = self.context['user']
        validated_data['story'] = self.context['story']
        comment = super(CommentSerializer, self).create(validated_data)
        return comment

class TagSerializer(serializers.ModelSerializer):
    tag_id = serializers.IntegerField(source='tag.id', read_only=True)
    story_id = serializers.IntegerField(source='story.id', read_only=True)
    tag_name = serializers.CharField(source='tag.name', max_length=100)
    
    class Meta:
        model = StoryTag
        fields = (
            'id',
            'tag_id',
            'story_id',
            'tag_name',
            'created_at',
        )
        read_only_fields = ('created_at',)

    def create(self, validated_data):
        validated_data['story'] = self.context['story']
        validated_data['tag'] = self.context['tag']
        story_tag = super(TagSerializer, self).create(validated_data)
        return story_tag