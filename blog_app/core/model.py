import enum
from typing import TypedDict

from sqlalchemy.schema import Column, MetaData, Table
from sqlalchemy.sql import func, text
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import Enum, Integer, String, Text, TIMESTAMP


class ReactionType(enum.Enum):
    like = "like"
    thumbs_up = "thumbs_up"
    smile = "smile"


class ModelMap(TypedDict):
    post: Table
    comment: Table
    reaction: Table


def register_tables(metadata: MetaData) -> ModelMap:
    return ModelMap(
        post=Table(
            "post",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("title", String(150), nullable=False),
            Column("author_id", String(32), nullable=False, index=True),
            Column("content", Text),
            Column("created", TIMESTAMP, nullable=False, server_default=func.now()),
            Column(
                "updated",
                TIMESTAMP,
                nullable=False,
                server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            ),
        ),
        comment=Table(
            "comment",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column(
                "post_id", Integer, ForeignKey("post.id"), nullable=False, index=True
            ),
            Column("author_id", String(32), nullable=False),
            Column("content", Text),
            Column("created", TIMESTAMP, nullable=False, server_default=func.now()),
            Column(
                "updated",
                TIMESTAMP,
                nullable=False,
                server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            ),
        ),
        reaction=Table(
            "reaction",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column(
                "comment_id",
                Integer,
                ForeignKey("comment.id"),
                nullable=False,
                index=True,
            ),
            Column("author_id", String(32), nullable=False),
            Column("reaction_type", Enum(ReactionType), nullable=False),
            Column(
                "updated",
                TIMESTAMP,
                nullable=False,
                server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            ),
        ),
    )
