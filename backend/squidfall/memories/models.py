from django.db import models


class Memory(models.Model):
    namespace = models.JSONField()
    key = models.CharField(max_length=255)
    value = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=["namespace", "key"], name="unique_memory"),
        )
