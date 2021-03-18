import asyncio
import functools
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Generic,
    Hashable,
    List,
    Literal,
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
        self.dataloader = self.get_dataloader("id")

    async def all(self):
        for row in await self.model.load_all():
            yield self.constructor(**row._asdict())

    async def load(self, key: int) -> Optional[LoaderType]:
        return await self.dataloader.load(key)

    async def load_many(self, keys: List[int]) -> Sequence[Optional[LoaderType]]:
        return await asyncio.gather(*(self.load(key) for key in keys))

    K = TypeVar("K", bound=Hashable)
    V = TypeVar("V")

    @staticmethod
    def fillBy(keys: Sequence[K], items: Sequence[V], key_fn: Callable[[V], K]):
        return (
            matches[0] if matches else None
            for matches in Loader.groupBy(keys, items, key_fn)
        )

    @staticmethod
    def groupBy(keys: Sequence[K], items: Sequence[V], key_fn: Callable[[V], K]):
        groups: Dict[Loader.K, List[Loader.V]] = {}

        for item in items:
            groups.setdefault(key_fn(item), []).append(item)

        return (groups.get(key, []) for key in keys)

    @functools.cache
    def get_dataloader(self, key_field: str) -> DataLoader[int, Optional[LoaderType]]:
        async def load_fn(keys: List[int]) -> List[Optional[LoaderType]]:
            matching_rows = await self.model.load_all(
                **{key_field: keys}
            )  # where `<key_field>` in `<keys>`
            return [
                self.constructor(**row._asdict()) if row else None
                for row in Loader.fillBy(
                    keys, matching_rows, lambda row: getattr(row, key_field, None)
                )
            ]

        return DataLoader(load_fn)

    @functools.cache
    def get_group_dataloader(self, key_field: str) -> DataLoader[int, List[LoaderType]]:
        async def load_fn(keys: List[int]) -> List[List[LoaderType]]:
            matching_rows = await self.model.load_all(
                **{key_field: keys}
            )  # where `<key_field>` in `<keys>`
            return [
                [self.constructor(**row._asdict()) for row in group]
                for group in Loader.groupBy(
                    keys, matching_rows, lambda row: getattr(row, key_field, None)
                )
            ]

        return DataLoader(load_fn)


__all__ = ["Loader"]
