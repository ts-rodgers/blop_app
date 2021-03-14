from typing import Generic, List, Optional, TypeVar

import strawberry

from .loader import Loader


ItemType = TypeVar("ItemType")


@strawberry.type
class Collection(Generic[ItemType]):
    loader: strawberry.Private[Loader[ItemType]]

    @strawberry.field
    async def all_items(self) -> List[ItemType]:
        return [item for item in self.loader.all()]

    @strawberry.field
    async def by_id(self, ids: List[int]) -> List[Optional[ItemType]]:
        return [item for item in await self.loader.load_many(ids)]


__all__ = ["Collection"]
