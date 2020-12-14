from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Story(models.Model):
    uid  = models.CharField(max_length=100, null=False, unique=True)
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
    content = models.TextField()
    # for image, content should be like this: "<img src = "./img/model1.png" width="70%">"  

class StoryComment(models.Model):
    story = models.ForeignKey(Story, null=False, related_name='comments', on_delete=models.CASCADE)
    writer = models.ForeignKey(User, null=False, related_name='comments', on_delete=models.CASCADE)
    body = models.TextField() # is there text field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Tag(models.Model):
    name = models.CharField(max_length=100, blank=False, unique=True)

class StoryTag(models.Model):
    story = models.ForeignKey(Story, null=False, related_name='story_tag', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, null=False, related_name='story_tag', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class StoryRead(models.Model):
    story = models.ForeignKey(Story, null=False, related_name='story_read', on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, related_name='story_read', on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField(null=False)
    read_at = models.DateTimeField(null=False)
