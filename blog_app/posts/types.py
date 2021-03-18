from typing import List, NewType, Optional
from datetime import datetime

import strawberry
from strawberry.types import Info

from blog_app.core import AppComment, AppContext, AppRequest, Person, AppPost
from .logic import coerce_title


def parse_title(s: str):
    result = coerce_title(s)

    if result.is_failed:
        raise ValueError(result.collapse())
    else:
        return result.collapse()


PostTitle = strawberry.scalar(
    NewType("PostTitle", str),
    description="A post title, within which all whitespace is collapsed: e.g. '  foo    bar   ' -> 'foo bar'",
    parse_value=parse_title,
)


@strawberry.type(name="Post_")
class Post(AppPost):
    id: int
    author_id: strawberry.ID
    title: PostTitle  # type: ignore[valid-type]
    content: str
    created: datetime
    updated: datetime

    @strawberry.field()
    async def author(self, info: Info[AppContext, AppRequest]) -> Person:
        # ignore type error because we don't expect this to resolve
        # null; this should trigger a low-level gql error instead if this does
        # happen.
        return await info.context.auth.users.load(self.author_id)  # type: ignore

    @strawberry.field
    async def comments(self, info: Info[AppContext, AppRequest]) -> List[AppComment]:
        return await info.context.comments.by_post_id.load(self.id)


@strawberry.type
class PostRetrievalError:
    message: str


@strawberry.type
class PostCreationResponse:
    id: int
    title: PostTitle  # type: ignore[valid-type]


@strawberry.type
class PostUpdateResponse:
    id: int
    title: Optional[PostTitle] = None  # type: ignore[valid-type]
    content: Optional[str] = None


@strawberry.type
class PostDeletionResponse:
    id: int
