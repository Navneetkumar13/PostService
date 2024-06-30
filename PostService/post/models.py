from django.db import models
import uuid

class Post(models.Model):
    post_id = models.UUIDField(default=uuid.uuid4, unique=True)
    caption = models.TextField(default=None, null=True)
    image_s3_link = models.TextField(default=None, null=True)
    image_s3_path = models.TextField(default=None, null=True)
    hashtags = models.JSONField(default=list, null=True, blank=True)
    created_by = models.CharField(max_length=500, default=None)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()