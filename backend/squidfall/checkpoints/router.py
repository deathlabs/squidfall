# Third party imports.
from ninja import Router

# Local imports.
from checkpoints.models import Checkpoint
from checkpoints.schema import CheckpointSchema, NotFoundSchema

# Init the exercises router.
checkpoint_router = Router(tags=["checkpoints"])


@checkpoint_router.get(
    "/{thread_id}/", response={200: CheckpointSchema, 404: NotFoundSchema}
)
def get_checkpoint(request, thread_id: str, checkpoint_id: str | None = None):
    try:
        checkpoints = Checkpoint.objects.filter(thread_id=thread_id)
        if checkpoint_id:
            checkpoints = checkpoints.filter(checkpoint_id=checkpoint_id)
        return 200, checkpoints.latest("updated_at")
    except Checkpoint.DoesNotExist:
        return 404, {"message": "chat not found"}


@checkpoint_router.get("/", response=list[CheckpointSchema])
def list_checkpoints(request, thread_id: str | None = None):
    checkpoints = Checkpoint.objects.all()
    if thread_id:
        checkpoints = checkpoints.filter(thread_id=thread_id)
    return checkpoints.order_by("-updated_at")


@checkpoint_router.post("/", response={201: CheckpointSchema})
def create_checkpoint(request, payload: CheckpointSchema):
    checkpoint, _ = Checkpoint.objects.update_or_create(
        checkpoint_id=payload.checkpoint_id,
        defaults=payload.dict(exclude={"checkpoint_id"}),
    )
    return 201, checkpoint
