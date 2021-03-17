import re
from typing import List, TypeVar

from blog_app.core import Result, AppError, Person
from blog_app.core.helpers import Loader
from blog_app.core.protocols import AuthContext
from blog_app.common.logic import (
    EditType,
    handle_create,
    handle_edit,
    remove_falsy_values,
)


WHITESPACE_REGEX = re.compile(r"\s+")
AUTHOR_KEY = "author_id"
T = TypeVar("T")


def coerce_title(title: str) -> Result[str, str]:
    """
    Collapse whitespace within a string and trim both ends.

    If the string is empty afterward, a ValueError will be raised.
    (since this function is intended to be used as a scalar; strawberry
    will convert the value error into a validation error on the field)
    """
    fixed = WHITESPACE_REGEX.sub(" ", title.strip())
    return (
        Result(value=fixed)
        if fixed
        else Result(error="PostTitle cannot contain only whitespace.")
    )


# fixme: type 'args' for handlers


async def create_post_handler(
    args: dict, auth: AuthContext, loader: Loader
) -> Result[int, AppError]:
    return await handle_create(args, AUTHOR_KEY, auth, loader.model)


async def update_post_handler(
    args: dict, auth: AuthContext, loader: Loader
) -> Result[dict, AppError]:
    post_id: int = args.pop("id")
    args = remove_falsy_values(args, restrict_keys={"title", "content"})
    return (
        await handle_edit(post_id, AUTHOR_KEY, auth, loader, EditType.UPDATE, **args)
    ).map(lambda _: args)


async def delete_post_handler(
    args: dict, auth: AuthContext, loader: Loader
) -> Result[None, AppError]:
    post_id: int = args.pop("id")
    return await handle_edit(post_id, AUTHOR_KEY, auth, loader, EditType.DELETE)