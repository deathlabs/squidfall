# Third party imports.
from django.db import models


class Chat(models.Model):
    thread_id = models.CharField(max_length=255)
    checkpoint_ns = models.CharField(max_length=255, default="")
    checkpoint_id = models.CharField(max_length=255, unique=True)
    parent_checkpoint_id = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=50)
    checkpoint = models.TextField()
    metadata_type = models.CharField(max_length=50)
    metadata = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
