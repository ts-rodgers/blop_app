import asyncio
from typing import (
    Any,
    Callable,
    Generator,
    Generic,
    Hashable,
    List,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
    Union,
    overload,
)

from strawberry.dataloader import DataLoader

from blog_app.core.model import ModelHelper


class Identifyable(Protocol):
    id: Hashable


LoaderType = TypeVar("LoaderType", covariant=True)


class Loader(Generic[LoaderType]):
    def __init__(
        self,
        constructor: Callable[..., LoaderType],
        model: ModelHelper,
    ):
        self.constructor = constructor
        self.model = model
        self.dataloader = DataLoader(self._dataloader_fn)

    async def all(self):
        for row in await self.model.load_all():
            yield self.constructor(**row._asdict())

    async def _dataloader_fn(self, keys: List[int]) -> List[Optional[LoaderType]]:
        return list(
            Loader.fillBy(keys, await self.model.load_by_id(keys), lambda row: row.id)
        )

    async def load(self, key: int) -> Optional[LoaderType]:
        return await self.dataloader.load(key)

    async def load_many(self, keys: List[int]) -> Sequence[Optional[LoaderType]]:
        return await asyncio.gather(*(self.load(key) for key in keys))

    K = TypeVar("K", bound=Hashable)
    V = TypeVar("V")

    @staticmethod
    def fillBy(keys: Sequence[K], items: Sequence[V], key_fn: Callable[[V], K]):
        mapped = {key_fn(item): item for item in items}
        return (mapped.get(key) for key in keys)


__all__ = ["Loader"]
