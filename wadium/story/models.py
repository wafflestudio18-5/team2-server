from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Story(models.Model):
    uid  = models.CharField(max_length=100, null=False)
    writer = models.ForeignKey(User, null=False, related_name='stories', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False)
    subtitle = models.CharField(max_length=200, blank=True)
    featured_image = models.ImageField(upload_to='/file/path/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(null=False, default=False)
    published_at = models.DateTimeField(null=True)

class StoryBlock(models.Model):
    BlockTypes = (
        ('text', 'text'),
        ('image', 'image'),
    )
    story = models.ForeignKey(Story, null=False, related_name='blocks', on_delete=models.CASCADE)
    order = models.SmallIntegerField(null=False)
    block_type = models.CharField(max_length=50, choices=BlockTypes, null=False)
    content = models.CharField(max_length=1000, blank=True) # how about image?
    
