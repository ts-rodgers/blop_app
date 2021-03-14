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


def create_model_map(settings: DatabaseSettings) -> ModelMap:
    """Create an asyncronous db engine from the database settings."""
    engine = create_async_engine(settings.connection_url, echo=settings.echo_statements)
    metadata = MetaData()
    metadata.bind = engine
    return register_tables(metadata=metadata)
