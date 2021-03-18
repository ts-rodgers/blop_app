from typing import Any, NamedTuple, Tuple

from typed_settings import settings, secret
from typer.main import get_install_completion_arguments
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import MetaData

from .core.model import ModelMap, register_tables


@settings
class DatabaseSettings:
    connection_url: str = secret(
        default="mysql+aiomysql://blog_app:5678@127.0.0.1:3306/blog_app"
    )
    echo_statements: bool = True


def create_metadata(settings: DatabaseSettings) -> Tuple[MetaData, ModelMap]:
    engine = create_async_engine(settings.connection_url, echo=settings.echo_statements)
    metadata = MetaData()
    metadata.bind = engine
    return metadata, register_tables(metadata=metadata)


def create_model_map(settings: DatabaseSettings) -> ModelMap:
    """Create an asyncronous db engine from the database settings."""
    return create_metadata(settings)[1]


async def create_tables(settings: DatabaseSettings):
    metadata = create_metadata(settings)[0]
    engine: Any = metadata.bind
    async with engine.connect() as conn:
        await conn.run_sync(metadata.create_all)
