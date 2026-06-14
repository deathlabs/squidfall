# Third party imports.
from ninja import Schema


class ChatSchema(Schema):
    session_id: str
    message: str


class NotFoundSchema(Schema):
    message: str
