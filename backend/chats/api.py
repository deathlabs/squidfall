# Standard library imports.
from typing import List, Optional

# Third party imports.
from ninja import NinjaAPI

# Local imports.
from .models import Chat
from .schema import ChatSchema, NotFoundSchema

# Init the chats API.
api = NinjaAPI()


@api.get("/{session_id}", response={200: ChatSchema, 404: NotFoundSchema})
def chat(request, session_id):
    try:
        chat = Chat.objects.get(pk=session_id)
        return 200, chat
    except Chat.DoesNotExist:
        return 404, {"message": "chat not found"}


@api.get("/", response=List[ChatSchema])
def chats(request, session_id: Optional[str] = None):
    if session_id:
        return Chat.objects.filter(chat__icontains=session_id)
    return Chat.objects.all()


@api.post("/")
def respond(request, payload: ChatSchema):
    chat = Chat.objects.create(**payload.dict())
    print(chat)
    return {"message_id": chat.id}
