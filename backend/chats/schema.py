# Third party imports.
from typing import Optional
from ninja import Schema


class ChatSchema(Schema):
    thread_id: str
    checkpoint_ns: str = ""
    checkpoint_id: str
    parent_checkpoint_id: Optional[str] = None
    type: str
    checkpoint: str
    metadata_type: str
    metadata: str


class NotFoundSchema(Schema):
    message: str
