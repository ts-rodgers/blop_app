from typing import Any, List, Sequence, Union

from sqlalchemy.sql import select, ColumnElement
from sqlalchemy.schema import Table

from blog_app.core import Result


class ModelHelper:
    """
    A friendly wrapper for a database schema, that lets
    """

    engine: Any

    def __init__(self, table: Table, engine: Any):
        self.table = table
        self.engine = engine

    async def load_all(self, *cols: Union[ColumnElement, str], conn=None, **where):
        columns = [self.table.c[col] if isinstance(col, str) else col for col in cols]
        stmt = select(*(columns or self.table.columns))

        for key in where:
            if hasattr(self.table.c, key):
                stmt = stmt.where(self.table.c[key] == where[key])

        if conn is None:
            async with self.engine.connect() as conn:
                cursor = await conn.execute(stmt)
        else:
            cursor = await conn.execute(stmt)

        return cursor.fetchall()

    async def load_by_id(self, ids: List[int]):
        """"""
        async with self.engine.connect() as conn:
            stmt = self.table.select().where(self.table.c.id.in_(ids))
            cursor = await conn.execute(stmt)
            return cursor.fetchall()

    async def create(
        self, *, returning: Sequence[Union[ColumnElement, str]] = None, **values
    ):
        """Generic database record creation function, for use with an sqlachemy table."""
        async with self.engine.connect() as conn:
            stmt = self.table.insert().values(**values)
            cursor = await conn.execute(stmt)
            await conn.commit()

            if returning:
                all_values = await self.load_all(
                    *returning, conn=conn, id=cursor.lastrowid
                )
                return Result(value=all_values[0])

        return Result(value=None)

    async def update(
        self,
        item_id: int,
        *,
        returning: Sequence[Union[ColumnElement, str]] = None,
        **values
    ):
        """Generic database record update function, for use with an sqlachemy table."""
        async with self.engine.connect() as conn:
            stmt = (
                self.table.update()
                .where(self.table.c["id"] == item_id)
                .values(**values)
            )
            if returning:
                stmt = stmt.returning(*self.coerce_returning(returning))

            cursor = await conn.execute(stmt)
            return cursor.fetchone()

    async def delete(
        self, item_id: int, *, returning: Sequence[Union[ColumnElement, str]]
    ):
        """Generic database item delete function"""
        async with self.engine.connect() as conn:
            stmt = self.table.delete().where(self.table.c["id"] == item_id)
            if returning:
                stmt = stmt.returning(*self.coerce_returning(returning))

            cursor = await conn.execute(stmt)
            return cursor.fetchone()

    def coerce_returning(self, returning: Sequence[Union[ColumnElement, str]]):
        return (self.table.c[col] if isinstance(col, str) else col for col in returning)
