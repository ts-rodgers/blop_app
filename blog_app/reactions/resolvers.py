import logging
from typing import Union, cast

import strawberry
from strawberry.types import Info

from blog_app.core import (
    AppContext,
    AppRequest,
    AppReactionType,
    AppError,
    InternalError,
    ItemNotFoundError,
)
from blog_app.common.logic import EditType, handle_create, handle_edit, Unauthorized
from blog_app.auth.types import AuthError
from .context import Context as LocalContext
from .types import ReactionSetResponse, ReactionDeletionResponse

ReactionError = Union[AuthError, InternalError]
ReactionEditError = Union[ReactionError, ItemNotFoundError]


def coerce_error(err: AppError) -> ReactionError:
    if isinstance(err, (AuthError, InternalError)):
        return err
    else:
        logging.error("Unexpect app error: '%s'", err.message)
        return InternalError()


def coerce_edit_error(err: AppError) -> ReactionEditError:
    if isinstance(err, Unauthorized):
        return AuthError.unauthorized("No authority to edit this reaction.")
    if isinstance(err, ItemNotFoundError):
        return ItemNotFoundError("No such reaction.")
    else:
        return coerce_error(err)


def get_loader(info: Info[AppContext, AppRequest]):
    # The implementation of the PostContext protocol is provided by the
    # posts (this) package, and is guaranteed to be a Context.
    return cast(LocalContext, info.context.reactions).loader


def get_comments_model(info: Info[AppContext, AppRequest]):
    return cast(LocalContext, info.context.reactions).model


async def set_reaction(
    comment_id: int, reaction_type: AppReactionType, info: Info[AppContext, AppRequest]
) -> Union[ReactionSetResponse, ReactionError]:
    return (
        (
            await handle_create(
                {"comment_id": comment_id, "reaction_type": reaction_type},
                info.context.auth,
                get_comments_model(info),
                on_conflict_set={"reaction_type": reaction_type},
            )
        )
        .map(
            lambda reaction_id: ReactionSetResponse(
                id=reaction_id, reaction_type=reaction_type
            )
        )
        .map_err(coerce_error)
        .collapse()
    )


async def delete_reaction(
    id: int, info: Info[AppContext, AppRequest]
) -> Union[ReactionDeletionResponse, ReactionEditError]:
    return (
        (
            await handle_edit(
                id,
                info.context.auth,
                get_loader(info),
                EditType.DELETE,
            )
        )
        .map(lambda _: ReactionDeletionResponse(id=id))
        .map_err(coerce_edit_error)
        .collapse()
    )
