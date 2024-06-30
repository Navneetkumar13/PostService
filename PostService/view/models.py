from django.db import models

class View(models.Model):
    post_id = models.UUIDField(default=None, null=True)
    visited_by = models.CharField(max_length=500, default=None)