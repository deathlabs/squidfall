# Standard library imports.
from chats.router import chats_router
from django.urls import path

# Local imports.
from ninja import NinjaAPI

from .health import api as health_api

api = NinjaAPI()
api.add_router("/chats/", chats_router)
api.add_router("/health/", health_api)

urlpatterns = [
    path("api/v1/", api.urls),
]
