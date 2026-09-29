# Standard library imports.
# Local imports.
from django.urls import path
from ninja import NinjaAPI

from checkpoints.router import checkpoint_router
from memories.router import memory_router

from .health import api as health_api

api = NinjaAPI()
api.add_router("/health/", health_api)
api.add_router("/checkpoints/", checkpoint_router)
api.add_router("/memories/", memory_router)
urlpatterns = [
    path("api/v1/", api.urls),
]
