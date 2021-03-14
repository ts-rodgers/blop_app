from typing import Optional
from datetime import datetime

import strawberry
from strawberry.types import Info

from blog_app.core import AppContext, AppRequest, Person, AppPost


@strawberry.type(name="Post_")
class Post(AppPost):
    id: int
    author_id: strawberry.ID
    title: str
    content: str
    created: datetime
    updated: datetime

    @strawberry.field()
    async def author(self, info: Info[AppContext, AppRequest]) -> Person:
        # ignore type error because we don't expect this to resolve
        # null; this should trigger a low-level gql error instead.
        return await info.context.auth.users.load(self.author_id)  # type: ignore


@strawberry.type
class PostRetrievalError:
    message: str
