import asyncio
from typing import (
    Any,
    Callable,
    Generic,
    Hashable,
    List,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
    Union,
)

from sqlalchemy.schema import Table
from sqlalchemy.sql.visitors import Visitable
from strawberry.dataloader import DataLoader


class Identifyable(Protocol):
    id: Hashable


LoaderType = TypeVar("LoaderType", covariant=True)
RowItemType = TypeVar("RowItemType", bound=Identifyable)


class Loader(Generic[LoaderType]):
    def __init__(
        self,
        constructor: Callable[..., LoaderType],
        engine: Any,
        table: Table,
    ):
        self.constructor = constructor
        self.engine = engine
        self.table = table
        self.dataloader = DataLoader(self._dataloader_fn)

    async def all(self, where_clause: Union[str, bool, Visitable] = None):
        async with self.engine.connect() as conn:
            cursor = await conn.execute(
                self.table.select().where(where_clause)
                if where_clause
                else self.table.select()
            )

            for row in cursor.fetchall():
                yield self.constructor(**row._asdict())

    async def load(self, key: int) -> Optional[LoaderType]:
        return await self.dataloader.load(key)

    async def load_many(self, keys: List[int]) -> Sequence[Optional[LoaderType]]:
        return await asyncio.gather(*(self.load(key) for key in keys))

    async def _dataloader_fn(self, keys: List[int]) -> List[Optional[LoaderType]]:
        async with self.engine.connect() as conn:
            cursor = await conn.execute(
                self.table.select().where(self.table.c.id.in_(keys))
            )
            return list(self.fillBy(keys, cursor.fetchall()))

    @staticmethod
    def fillBy(keys: Sequence[Hashable], items: Sequence[RowItemType]):
        mapped = {item.id: item for item in items}
        return (mapped.get(key) for key in keys)


__all__ = ["Loader"]
