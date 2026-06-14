# Third party imports.
from django.db import models


# Create your models here.
class Chat(models.Model):
    session_id = models.CharField(max_length=250)
    message = models.CharField(max_length=250)
