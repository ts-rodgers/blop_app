import functools
from typing import Awaitable, Callable, Generic, List, Optional, Sequence, TypeVar

import strawberry

from .loader import Loader


ItemType = TypeVar("ItemType")


@strawberry.type
class Collection(Generic[ItemType]):
    def __init__(self, load_fn: Callable[[], Awaitable[Sequence[ItemType]]]):
        self.load_fn = functools.cache(load_fn)

    @strawberry.field
    async def all_items(self) -> List[ItemType]:
        return [item for item in await self.load_fn()]


@strawberry.type
class QueryableCollection(Collection[ItemType]):
    def __init__(self, loader: Loader[ItemType]):
        super().__init__(loader.all)
        self.loader = loader

    @strawberry.field
    async def by_id(self, ids: List[int]) -> List[Optional[ItemType]]:
        return [item for item in await self.loader.load_many(ids)]


__all__ = ["Collection", "QueryableCollection"]
