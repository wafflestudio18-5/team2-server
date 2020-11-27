from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.FileField.storage
class Story(models.Model):
    writer_id = models.ForeignKey(User, null=False, related_name='story', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False)
    subtitle = models.CharField(max_length=100, null=True)
    featured_image = models.ImageField(upload_to='/file/path/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(null=False, default=False)
    published_at = models.DateTimeField(null=True)

    # uid  = models.CharField(max_length=100, null=False)
    # can't understand the role of uid


