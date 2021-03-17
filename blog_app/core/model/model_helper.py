from typing import Any, Dict, List, Sequence, Union, cast

from sqlalchemy.sql import select, ColumnElement
from sqlalchemy.schema import Table

from blog_app.core import Result
from blog_app.core import InternalError


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

    async def create(self, **values):
        """Generic database record creation function, for use with an sqlachemy table."""
        with InternalError.from_exception() as result:
            async with self.engine.connect() as conn:
                stmt = self.table.insert().values(**values)
                cursor = await conn.execute(stmt)
                await conn.commit()
                result = result.map(lambda _: cast(int, cursor.lastrowid))
            return result

    async def update(self, item_id: int, *, where: Dict[str, Any] = None, **values):
        """Generic database record update function, for use with an sqlachemy table."""
        with InternalError.from_exception() as result:
            async with self.engine.connect() as conn:
                stmt = (
                    self.table.update()
                    .where(self.table.c["id"] == item_id)
                    .values(**values)
                )

                for key, val in (where or {}).items():
                    if hasattr(self.table.c, key):
                        stmt = stmt.where(self.table.c[key] == val)

                cursor = await conn.execute(stmt)
                await conn.commit()
                result = result.map(lambda _: cast(int, cursor.rowcount))
            return result

    async def delete(self, item_id: int, *, where: Dict[str, Any] = None):
        """Generic database item delete function"""
        with InternalError.from_exception() as result:
            async with self.engine.connect() as conn:
                stmt = self.table.delete().where(self.table.c["id"] == item_id)

                for key, val in (where or {}).items():
                    if hasattr(self.table.c, key):
                        stmt = stmt.where(self.table.c[key] == val)

                cursor = await conn.execute(stmt)
                await conn.commit()
                result = result.map(lambda _: cast(int, cursor.rowcount))
            return result
