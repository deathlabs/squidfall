# Standard library imports.
from datetime import datetime

# Third party imports.
from ninja import Schema


class MemoryCreateSchema(Schema):
    namespace: list[str]
    key: str
    value: dict


class MemorySchema(Schema):
    namespace: list[str]
    key: str
    value: dict
    created_at: datetime
    updated_at: datetime


class NotFoundSchema(Schema):
    message: str
