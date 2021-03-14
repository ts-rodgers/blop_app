from typing import Optional
from datetime import datetime

import strawberry
from strawberry.types import Info

from blog_app.core import AppContext, AppRequest
from blog_app.auth import User


@strawberry.type
class Post:
    id: int
    author_id: strawberry.ID
    title: str
    content: str
    created: datetime
    updated: datetime

    @strawberry.field()
    async def author(self, info: Info[AppContext, AppRequest]) -> Optional[User]:
        app_user = await info.context.auth.users.load(self.author_id)
        return User.marshal(app_user) if app_user else None


@strawberry.type
class PostRetrievalError:
    message: str
