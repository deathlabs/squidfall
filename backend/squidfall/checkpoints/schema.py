# Third party imports.

from ninja import Schema


class CheckpointSchema(Schema):
    thread_id: str
    checkpoint_ns: str = ""
    checkpoint_id: str
    parent_checkpoint_id: str | None = None
    type: str
    checkpoint: str
    metadata_type: str
    metadata: str


class NotFoundSchema(Schema):
    message: str
