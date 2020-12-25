from rest_framework import serializers
from .models import Story

class StorySerializer(serializers.ModelSerializer):
    # uid = serializers.CharField()
    # writer_id = serializers.IntegerField()
    title = serializers.CharField(allow_blank=True)
    subtitle = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    published_at = serializers.DateTimeField(allow_null=True, default=None)
    published = serializers.BooleanField(default=False)

    class Meta:
        model = Story
        fields = (
            'id',
            # 'uid',
            # 'writer_id',
            'title',
            'subtitle',
            'created_at',
            'updated_at',
            'published_at',
            'published',
        )
    def validate(self, data):
        if data['title'] == '':
            data['title'] = 'Untitled'
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['writer'] = user
        story = super(StorySerializer, self).create(validated_data)
        return story
