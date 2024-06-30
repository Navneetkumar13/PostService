from django.db import models
import uuid

class Comments(models.Model):
    base_comment_id = models.UUIDField(default=None, null=True)
    comment_id = models.UUIDField(default=uuid.uuid4, unique=True)
    comment = models.TextField(default=None, null=True)
    is_reply = models.BooleanField(default=False)
    post_id = models.UUIDField(default=None, null=True)
    created_by = models.CharField(max_length=500, default=None)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()