from typing import Any, Collection, Dict, List, Sequence, Union, cast, overload

from sqlalchemy.sql import select, ColumnElement
from sqlalchemy.schema import Table
from sqlalchemy.sql.dml import Delete, Insert, Update
from sqlalchemy.sql.selectable import Select

from blog_app.core import Result
from blog_app.core import InternalError


class ModelHelper:
    """
    A friendly wrapper for a database schema, that lets
    """

    engine: Any
    author_key: str

    def __init__(self, author_key: str, table: Table, engine: Any):
        self.table = table
        self.engine = engine
        self.author_key = author_key

    async def load_all(self, *cols: Union[ColumnElement, str], conn=None, **where):
        columns = [self.table.c[col] if isinstance(col, str) else col for col in cols]
        stmt = select(*(columns or self.table.columns))
        stmt = self._restrict_rows(stmt, where)

        if conn is None:
            async with self.engine.connect() as conn:
                cursor = await conn.execute(stmt)
        else:
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

                stmt = self._restrict_rows(stmt, where)

                cursor = await conn.execute(stmt)
                await conn.commit()
                result = result.map(lambda _: cast(int, cursor.rowcount))
            return result

    async def delete(self, item_id: int, *, where: Dict[str, Any] = None):
        """Generic database item delete function"""
        with InternalError.from_exception() as result:
            async with self.engine.connect() as conn:
                stmt = self.table.delete().where(self.table.c["id"] == item_id)
                stmt = self._restrict_rows(stmt, where)

                cursor = await conn.execute(stmt)
                await conn.commit()
                result = result.map(lambda _: cast(int, cursor.rowcount))
            return result

    @overload
    def _restrict_rows(self, stmt: Select, where: Dict[str, Any] = None) -> Select:
        ...

    @overload
    def _restrict_rows(self, stmt: Update, where: Dict[str, Any] = None) -> Update:
        ...

    @overload
    def _restrict_rows(self, stmt: Delete, where: Dict[str, Any] = None) -> Delete:
        ...

    def _restrict_rows(
        self, stmt: Union[Select, Update, Delete], where: Dict[str, Any] = None
    ) -> Union[Select, Update, Delete]:
        if not where:
            return stmt

        for key, val in where.items():
            if hasattr(self.table.c, key):
                stmt = stmt.where(
                    self.table.c[key].in_(val)
                    if isinstance(val, Collection)
                    else self.table.c[key] == val
                )

        return stmt
