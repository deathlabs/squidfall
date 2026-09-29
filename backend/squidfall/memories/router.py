# Standard library imports.

# Third party imports.
from ninja import Query, Router

# Local imports.
from memories.models import Memory
from memories.schemas import MemoryCreateSchema, MemorySchema, NotFoundSchema

# Init the memories API.
memory_router = Router(tags=["memories"])


@memory_router.get("/", response={200: MemorySchema, 404: NotFoundSchema})
def get_memory(request, namespace: list[str], key: str):
    try:
        return 200, Memory.objects.get(namespace=namespace, key=key)
    except Memory.DoesNotExist:
        return 404, {"message": "memory not found"}


@memory_router.get("/search/", response=list[MemorySchema])
def search_memories(
    request,
    namespace_prefix: Query[list[str]],
    query: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    if namespace_prefix is None:
        namespace_prefix = Query(...)
    memories = Memory.objects.filter(namespace__0=namespace_prefix[0])
    return memories.order_by("-updated_at")[offset : offset + limit]


@memory_router.post("/", response={201: MemoryCreateSchema})
def create_memory(request, payload: MemoryCreateSchema):
    memory, _ = Memory.objects.update_or_create(
        namespace=payload.namespace,
        key=payload.key,
        defaults={"value": payload.value},
    )
    return 201, memory


@memory_router.delete("/", response={204: None, 404: NotFoundSchema})
def delete_memory(request, namespace: list[str], key: str):
    try:
        Memory.objects.get(namespace=namespace, key=key).delete()
        return 204, None
    except Memory.DoesNotExist:
        return 404, {"message": "memory not found"}
