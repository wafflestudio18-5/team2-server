from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Story(models.Model):
    writer = models.ForeignKey(User, related_name='stories', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, db_index=True)
    subtitle = models.CharField(max_length=140, blank=True)
    body = models.JSONField(default=list)
    featured_image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True)


class StoryComment(models.Model):
    story = models.ForeignKey(Story, related_name='comments', on_delete=models.CASCADE)
    writer = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    body = models.TextField() # is there text field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

class StoryTag(models.Model):
    story = models.ForeignKey(Story, related_name='story_tag', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, related_name='story_tag', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['story', 'tag']

class StoryRead(models.Model):
    story = models.ForeignKey(Story, related_name='story_read', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='story_read', on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField()
    read_at = models.DateTimeField()
    class Meta:
        unique_together = ['story', 'user']
