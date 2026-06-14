# Third party imports
from django.contrib import admin
from django.urls import path

# Local imports.
from chats.api import api as chats_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/chats/", chats_api.urls),
]
