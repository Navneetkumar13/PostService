from django.db import models
import uuid

class Likes(models.Model):
    like_id = models.UUIDField(default=uuid.uuid4, unique=True)
    liked_by = models.CharField(max_length=500, default=None)
    reference_type = models.CharField(max_length=256, default=None)
    reference_id = models.UUIDField(default=None, null=True)