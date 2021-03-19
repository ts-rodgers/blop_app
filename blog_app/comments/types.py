from datetime import datetime


import strawberry
from strawberry.types import Info

from blog_app.core import AppComment, AppContext, AppRequest, Person, AppReaction
from blog_app.core.helpers import Collection


@strawberry.type(name="Comment_")
class Comment(AppComment):
    id: int
    post_id: int
    author_id: strawberry.ID
    content: str
    created: datetime
    updated: datetime

    @strawberry.field
    async def author(self, info: Info[AppContext, AppRequest]) -> Person:
        # ignore type error because we don't expect this to resolve
        # null; this should trigger a resolver error instead if it does
        return await info.context.auth.users.load(self.author_id)  # type: ignore

    @strawberry.field
    async def reactions(
        self, info: Info[AppContext, AppRequest]
    ) -> Collection[AppReaction]:
        return Collection(lambda: info.context.reactions.by_comment_id.load(self.id))


@strawberry.type
class CommentResponse:
    id: int
    content: str


@strawberry.type
class CommentDeletionResponse:
    id: int
