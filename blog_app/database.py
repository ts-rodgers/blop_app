from typing import Any, NamedTuple

from typed_settings import settings, secret
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import MetaData

from .core.model import ModelMap, register_tables


@settings
class DatabaseSettings:
    connection_url: str = secret(
        default="mysql+aiomysql://blog_app:5678@127.0.0.1:3306/blog_app"
    )
    echo_statements: bool = True


class DatabaseHelpers(NamedTuple):
    engine: Any
    table_map: ModelMap


def create_database_helpers(settings: DatabaseSettings) -> DatabaseHelpers:
    """Create an asyncronous db engine from the database settings."""
    engine = create_async_engine(settings.connection_url, echo=settings.echo_statements)
    metadata = MetaData()
    metadata.bind = engine
    table_map = register_tables(metadata=metadata)
    return DatabaseHelpers(engine=engine, table_map=table_map)
