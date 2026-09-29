# Standard library imports.
from collections.abc import Iterable
from os import environ
from typing import Any, Literal

# Third party imports.
from httpx import AsyncClient
from langgraph.store.base import (
    NOT_PROVIDED,
    BaseStore,
    Item,
    NotProvided,
    Op,
    Result,
    SearchItem,
)

BACKEND_ENDPOINT = environ["BACKEND_ENDPOINT"]


class DjangoStore(BaseStore):
    """A Django-based Langgraph store for managing agent memory persistence."""

    def _row_to_item(self, row: dict) -> Item:
        """Convert a row into an Item."""
        return Item(
            namespace=tuple(row["namespace"]),
            key=row["key"],
            value=row["value"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_search_item(self, row: dict) -> SearchItem:
        """Convert a row into a SearchItem."""
        return SearchItem(
            namespace=tuple(row["namespace"]),
            key=row["key"],
            value=row["value"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            score=row.get("score"),
        )

    async def aget(
        self, namespace: tuple, key: str, *, refresh_ttl: bool | None = None
    ) -> Item | None:
        """Fetch a single memory using Django."""
        async with AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_ENDPOINT}/api/v1/memories/",
                params={"namespace": list(namespace), "key": key},
            )

        if response.status_code == 404:
            return None

        return self._row_to_item(response.json())

    async def aput(
        self,
        namespace: tuple[str, ...],
        key: str,
        value: dict,
        index: Literal[False] | list[str] | None = None,
        *,
        ttl: float | None | NotProvided = NOT_PROVIDED,
    ) -> None:
        """Store a single memory using Django."""
        async with AsyncClient() as client:
            await client.post(
                f"{BACKEND_ENDPOINT}/api/v1/memories/",
                json={"namespace": list(namespace), "key": key, "value": value},
            )

    async def adelete(self, namespace: tuple[str, ...], key: str) -> None:
        """Delete a single memory using Django."""
        async with AsyncClient() as client:
            await client.delete(
                f"{BACKEND_ENDPOINT}/api/v1/memories/",
                params={"namespace": list(namespace), "key": key},
            )

    async def asearch(
        self,
        namespace_prefix: tuple[str, ...],
        *,
        query: str | None = None,
        filter: dict[str, Any] | None = None,
        limit: int = 10,
        offset: int = 0,
        refresh_ttl: bool | None = None,
    ) -> list[SearchItem]:
        """Search for one of more memories from Django."""
        async with AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_ENDPOINT}/api/v1/memories/search/",
                params={
                    "namespace_prefix": list(namespace_prefix),
                    "query": query,
                    "limit": limit,
                    "offset": offset,
                },
            )
        return [self._row_to_search_item(row) for row in response.json()]

    async def abatch(self, ops: Iterable[Op]) -> list[Result]:
        """Perform a batch of operations using Django."""
        raise NotImplementedError

    def get(
        self, namespace: tuple[str, ...], key: str, *, refresh_ttl: bool | None = None
    ) -> Item | None:
        """Fetch a single memory from Django."""
        raise NotImplementedError

    def put(self, namespace: tuple[str, ...], key: str, value: dict) -> None:
        """Store a single memory in Django."""
        raise NotImplementedError

    def delete(self, namespace: tuple[str, ...], key: str) -> None:
        """Delete a single memory from Django."""
        raise NotImplementedError

    def search(self, namespace_prefix: tuple[str, ...], **kwargs) -> list[SearchItem]:
        """Search for one of more memories in Django."""
        raise NotImplementedError

    def batch(self, ops: Iterable[Op]) -> list[Result]:
        """Perform a batch of operations using Django."""
        raise NotImplementedError
