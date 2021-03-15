from blog_app.auth.types import AuthError
from typing import TypedDict, Union, cast

from strawberry.types import Info

from blog_app.core import AppContext, AppRequest, AppError
from blog_app.core.helpers import Collection
from blog_app.core.model import ModelHelper
from .context import Context
from .types import Post, PostCreationResponse, PostTitle


def get_loader(info: Info[AppContext, AppRequest]):
    # The implementation of the PostContext protocol is provided by the
    # posts (this) package, and is guaranteed to be a Context.
    return cast(Context, info.context.posts).loader


def get_posts_model(info: Info[AppContext, AppRequest]):
    return get_loader(info).model


async def get_posts(info: Info[AppContext, AppRequest]) -> Collection[Post]:
    return Collection(loader=get_loader(info))


async def create_post(
    title: PostTitle, content: str, info: Info[AppContext, AppRequest]
) -> Union[PostCreationResponse, AuthError]:
    model = get_posts_model(info)
    user_result = await info.context.auth.get_logged_in_user()
    metadata_result = await user_result.and_then(
        lambda user: model.create(
            returning=("id", "created"), author_id=user.id, title=title, content=content
        )
    )
    return metadata_result.map(
        lambda row: PostCreationResponse(id=row.id, title=title, created=row.created)
    ).collapse()


__all__ = ["get_posts"]
