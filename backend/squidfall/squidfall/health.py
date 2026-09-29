# Third party imports.
from ninja import Router

api = Router(tags=["health"])


@api.get("/", auth=None)
def health(request):
    return {"status": "ok"}
