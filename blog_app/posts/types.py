from typing import TypedDict
from datetime import datetime

import strawberry


@strawberry.type
class Post:
    id: int
    author_id: strawberry.ID
    title: str
    content: str
    created: datetime
    updated: datetime


@strawberry.type
class PostRetrievalError:
    message: str