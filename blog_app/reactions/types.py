from datetime import datetime


import strawberry
from strawberry.types import Info

from blog_app.core import AppReaction, AppReactionType, AppContext, AppRequest, Person


@strawberry.type(name="Reaction_")
class Reaction(AppReaction):
    id: int
    comment_id: int
    author_id: strawberry.ID
    reaction_type: AppReactionType
    updated: datetime

    @strawberry.field()
    async def author(self, info: Info[AppContext, AppRequest]) -> Person:
        # ignore type error because we don't expect this to resolve
        # null; this should trigger a resolver error instead if it does
        return await info.context.auth.users.load(self.author_id)  # type: ignore


@strawberry.type
class ReactionSetResponse:
    id: int
    reaction_type: AppReactionType


@strawberry.type
class ReactionDeletionResponse:
    id: int
