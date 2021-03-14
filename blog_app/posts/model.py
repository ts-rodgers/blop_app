from sqlalchemy.schema import Column, MetaData, Table
from sqlalchemy.sql import func, text
from sqlalchemy.types import Integer, String, TIMESTAMP


def register(metadata: MetaData):
    """Register the model with the SQLAlchemy metadata."""
    return Table(
        "post",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("title", String(75), nullable=False),
        Column("author_id", Integer, nullable=False),
        Column("created", TIMESTAMP, nullable=False, server_default=func.now()),
        Column(
            "last_updated",
            TIMESTAMP,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
    )
