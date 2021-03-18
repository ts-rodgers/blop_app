import logging
from typing import Optional, Union, cast

from strawberry.types import Info

from blog_app.core import (
    AppContext,
    AppRequest,
    AppError,
    InternalError,
    ItemNotFoundError,
)
from blog_app.core.helpers import Collection
from blog_app.auth.types import AuthError
from blog_app.common.logic import Unauthorized
from .context import Context
from .types import (
    Post,
    PostCreationResponse,
    PostDeletionResponse,
    PostTitle,
    PostUpdateResponse,
)
from .logic import create_post_handler, delete_post_handler, update_post_handler


def get_loader(info: Info[AppContext, AppRequest]):
    # The implementation of the PostContext protocol is provided by the
    # posts (this) package, and is guaranteed to be a Context.
    return cast(Context, info.context.posts).loader


def get_posts_model(info: Info[AppContext, AppRequest]):
    return cast(Context, info.context.posts).model


def coerce_error(err: AppError) -> Union[AuthError, ItemNotFoundError, InternalError]:
    if isinstance(err, (AuthError, InternalError)):
        return err
    if isinstance(err, Unauthorized):
        return AuthError.unauthorized("No authority to edit this post.")
    if isinstance(err, ItemNotFoundError):
        return ItemNotFoundError("No such post.")
    else:
        logging.error("Unexpect app error: '%s'", err.message)
        return InternalError()


async def get_posts(info: Info[AppContext, AppRequest]) -> Collection[Post]:
    return Collection(loader=get_loader(info))


async def create_post(
    title: PostTitle, content: str, info: Info[AppContext, AppRequest]
) -> Union[PostCreationResponse, AuthError, ItemNotFoundError, InternalError]:
    return (
        (
            await create_post_handler(
                {"title": title, "content": content},
                info.context.auth,
                get_loader(info),
            )
        )
        .map(lambda id: PostCreationResponse(id=id, title=title))
        .map_err(coerce_error)
        .collapse()
    )


async def update_post(
    id: int,
    info: Info[AppContext, AppRequest],
    *,
    title: Optional[PostTitle] = None,
    content: Optional[str] = None,
) -> Union[PostUpdateResponse, AuthError, ItemNotFoundError, InternalError]:
    return (
        (
            await update_post_handler(
                {"title": title, "content": content, "id": id},
                info.context.auth,
                get_loader(info),
            )
        )
        .map(lambda change_values: PostUpdateResponse(id=id, **change_values))
        .map_err(coerce_error)
        .collapse()
    )


async def delete_post(
    id: int,
    info: Info[AppContext, AppRequest],
) -> Union[PostDeletionResponse, AuthError, ItemNotFoundError, InternalError]:
    return (
        (await delete_post_handler({"id": id}, info.context.auth, get_loader(info)))
        .map(lambda _: PostDeletionResponse(id=id))
        .map_err(coerce_error)
        .collapse()
    )


__all__ = ["get_posts"]
