from django.db import models
from django.contrib.auth.models import User


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
    MAIN_ORDER_CHOICES = list(zip(range(1, 6), map(str, range(1, 6))))
    TRENDING_ORDER_CHOICES = list(zip(range(1, 7), map(str, range(1, 7))))
    main_order = models.PositiveSmallIntegerField(null=True, blank=True, choices=MAIN_ORDER_CHOICES)
    trending_order = models.PositiveSmallIntegerField(null=True, blank=True, choices=TRENDING_ORDER_CHOICES)
    # blank set to integer fields to pass validation in admin site


class StoryComment(models.Model):
    story = models.ForeignKey(Story, related_name='comments', on_delete=models.CASCADE)
    writer = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    body = models.TextField()  # is there text field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.name

class StoryTag(models.Model):
    story = models.ForeignKey(Story, related_name='story_tag', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, related_name='story_tag', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['story', 'tag']

    def __str__(self):
        return f'({self.story.id}, {self.tag.name})'

class StoryRead(models.Model):
    story = models.ForeignKey(Story, related_name='story_read', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='story_read', on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField()
    read_at = models.DateTimeField()

    class Meta:
        unique_together = ['story', 'user']
