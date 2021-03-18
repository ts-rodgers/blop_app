import logging
from typing import Union, cast

import strawberry
from strawberry.types import Info

from blog_app.core import (
    AppContext,
    AppRequest,
    AppError,
    InternalError,
    ItemNotFoundError,
)
from blog_app.common.logic import EditType, handle_create, handle_edit, Unauthorized
from blog_app.auth.types import AuthError
from .context import Context as LocalContext
from .types import CommentResponse, CommentDeletionResponse

CommentError = Union[AuthError, InternalError]
CommentEditError = Union[CommentError, ItemNotFoundError]


def coerce_error(err: AppError) -> CommentError:
    if isinstance(err, (AuthError, InternalError)):
        return err
    else:
        logging.error("Unexpect app error: '%s'", err.message)
        return InternalError()


def coerce_edit_error(err: AppError) -> CommentEditError:
    if isinstance(err, Unauthorized):
        return AuthError.unauthorized("No authority to edit this comment.")
    if isinstance(err, ItemNotFoundError):
        return ItemNotFoundError("No such comment.")
    else:
        return coerce_error(err)


def get_loader(info: Info[AppContext, AppRequest]):
    # The implementation of the PostContext protocol is provided by the
    # posts (this) package, and is guaranteed to be a Context.
    return cast(LocalContext, info.context.comments).loader


def get_comments_model(info: Info[AppContext, AppRequest]):
    return cast(LocalContext, info.context.comments).model


async def add_comment(
    post_id: int, content: str, info: Info[AppContext, AppRequest]
) -> Union[CommentResponse, CommentError]:
    return (
        (
            await handle_create(
                {"post_id": post_id, "content": content},
                "author_id",
                info.context.auth,
                get_comments_model(info),
            )
        )
        .map(lambda comment_id: CommentResponse(id=comment_id, content=content))
        .map_err(coerce_error)
        .collapse()
    )


async def update_comment(
    id: int, content: str, info: Info[AppContext, AppRequest]
) -> Union[CommentResponse, CommentEditError]:
    return (
        (
            await handle_edit(
                id,
                "author_id",
                info.context.auth,
                get_loader(info),
                EditType.UPDATE,
                **{"content": content}
            )
        )
        .map(lambda _: CommentResponse(id=id, content=content))
        .map_err(coerce_edit_error)
        .collapse()
    )


async def delete_comment(
    id: int, info: Info[AppContext, AppRequest]
) -> Union[CommentDeletionResponse, CommentEditError]:
    return (
        (
            await handle_edit(
                id,
                "author_id",
                info.context.auth,
                get_loader(info),
                EditType.DELETE,
            )
        )
        .map(lambda _: CommentDeletionResponse(id=id))
        .map_err(coerce_edit_error)
        .collapse()
    )
