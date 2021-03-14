from typing import Any, List, Union

from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.schema import Table


class ModelHelper:
    """
    A friendly wrapper for a database schema, that lets
    """

    engine: Any

    def __init__(self, table: Table, engine: Any):
        self.table = table
        self.engine = engine

    async def load_all(self, **where):
        where_clauses = [self.table.c[col] == val for col, val in where.items()]
        async with self.engine.connect() as conn:
            stmt = self.table.select()

            for key in where:
                if hasattr(self.table.c, key):
                    stmt = stmt.where(self.table.c[key] == where[key])

            cursor = await conn.execute(stmt)
            return cursor.fetchall()

    async def load_by_id(self, ids: List[int]):
        """"""
        async with self.engine.connect() as conn:
            stmt = self.table.select().where(self.table.c.id.in_(ids))
            cursor = await conn.execute(stmt)
            return cursor.fetchall()

    async def create(
        self, *, returning: List[Union[ColumnElement, str]] = None, **values
    ):
        """Generic database record creation function, for use with an sqlachemy table."""
        async with self.engine.connect() as conn:
            stmt = self.table.insert().values(**values)
            if returning:
                stmt = stmt.returning(self.coerce_returning(returning))

            cursor = await conn.execute(stmt)
            return cursor.fetchone()

    async def update(
        self,
        item_id: int,
        *,
        returning: List[Union[ColumnElement, str]] = None,
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
                stmt = stmt.returning(self.coerce_returning(returning))

            cursor = await conn.execute(stmt)
            return cursor.fetchone()

    async def delete(self, item_id: int, *, returning: List[Union[ColumnElement, str]]):
        """Generic database item delete function"""
        async with self.engine.connect() as conn:
            stmt = self.table.delete().where(self.table.c["id"] == item_id)
            if returning:
                stmt = stmt.returning(self.coerce_returning(returning))

            cursor = await conn.execute(stmt)
            return cursor.fetchone()

    def coerce_returning(self, returning: List[Union[ColumnElement, str]]):
        return (self.table.c[col] if isinstance(col, str) else col for col in returning)
