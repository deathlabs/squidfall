# Standard library imports.
from typing import List, Optional

# Third party imports.
from ninja import NinjaAPI

# Local imports.
from chats.models import Chat
from chats.schema import ChatSchema, NotFoundSchema

# Init the chats API.
api = NinjaAPI()


@api.get("/{thread_id}/", response={200: ChatSchema, 404: NotFoundSchema})
def get_chat(request, thread_id: str, checkpoint_id: Optional[str] = None):
    try:
        chats = Chat.objects.filter(thread_id=thread_id)
        if checkpoint_id:
            chats = chats.filter(checkpoint_id=checkpoint_id)
        return 200, chats.latest("updated_at")
    except Chat.DoesNotExist:
        return 404, {"message": "chat not found"}


@api.get("/", response=List[ChatSchema])
def list_chats(request, thread_id: Optional[str] = None):
    chats = Chat.objects.all()
    if thread_id:
        chats = chats.filter(thread_id=thread_id)
    return chats.order_by("-updated_at")


@api.post("/", response={201: ChatSchema})
def create_chat(request, payload: ChatSchema):
    chat, _ = Chat.objects.update_or_create(
        checkpoint_id=payload.checkpoint_id,
        defaults=payload.dict(exclude={"checkpoint_id"}),
    )
    return 201, chat
