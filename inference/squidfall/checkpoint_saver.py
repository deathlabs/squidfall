# Standard library imports.
from os import environ
from typing import Any, AsyncIterator, Optional, Sequence, Tuple

# Third party imports.
from httpx import AsyncClient
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id,
)

BACKEND_ENDPOINT = environ["BACKEND_ENDPOINT"]


class DjangoCheckpointSaver(BaseCheckpointSaver):

    async def aget_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = get_checkpoint_id(config)

        async with AsyncClient() as client:
            resp = await client.get(
                f"{BACKEND_ENDPOINT}/api/v1/chats/{thread_id}/",
                params={"checkpoint_id": checkpoint_id} if checkpoint_id else {},
            )

        if resp.status_code == 404:
            return None

        return self._row_to_tuple(config, resp.json())

    async def alist(self, config: dict, **kwargs) -> AsyncIterator[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]

        async with AsyncClient() as client:
            resp = await client.get(
                f"{BACKEND_ENDPOINT}/api/v1/chats/", params={"thread_id": thread_id}
            )

        for row in resp.json():
            yield self._row_to_tuple(config, row)

    async def aput(
        self,
        config: dict,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict,
    ) -> dict:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = get_checkpoint_id(config)

        ctype, serialized = self.serde.dumps_typed(checkpoint)
        mtype, meta_serialized = self.serde.dumps_typed(metadata)

        async with AsyncClient() as client:
            await client.post(
                f"{BACKEND_ENDPOINT}/api/v1/chats/",
                json={
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": checkpoint_id,
                    "parent_checkpoint_id": parent_checkpoint_id,
                    "type": ctype,
                    "checkpoint": serialized.hex(),
                    "metadata_type": mtype,
                    "metadata": meta_serialized.hex(),
                },
            )

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }

    async def aput_writes(
        self,
        config: dict,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        pass

    def get_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        raise NotImplementedError

    def list(self, config: dict, **kwargs):
        raise NotImplementedError

    def put(self, config, checkpoint, metadata, new_versions):
        raise NotImplementedError

    def put_writes(self, config, writes, task_id):
        raise NotImplementedError

    def _row_to_tuple(self, config: dict, row: dict) -> CheckpointTuple:
        return CheckpointTuple(
            config={
                "configurable": {
                    "thread_id": row["thread_id"],
                    "checkpoint_ns": row["checkpoint_ns"],
                    "checkpoint_id": row["checkpoint_id"],
                }
            },
            checkpoint=self.serde.loads_typed(
                (row["type"], bytes.fromhex(row["checkpoint"]))
            ),
            metadata=self.serde.loads_typed(
                (row["metadata_type"], bytes.fromhex(row["metadata"]))
            ),
            parent_config=(
                {
                    "configurable": {
                        "thread_id": row["thread_id"],
                        "checkpoint_ns": row["checkpoint_ns"],
                        "checkpoint_id": row["parent_checkpoint_id"],
                    }
                }
                if row.get("parent_checkpoint_id")
                else None
            ),
        )
