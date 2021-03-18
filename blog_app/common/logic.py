from enum import Enum
from typing import Iterable, Mapping, NewType, Union

from blog_app.core import Result, AppError, InternalError, ItemNotFoundError
from blog_app.core.helpers import Loader
from blog_app.core.protocols import AuthContext, Person
from .model_helper import ModelHelper


class Unauthorized(AppError):
    def __init__(self, message="No authority to change this."):
        super().__init__(message=message)


class EditType(Enum):
    UPDATE = "update"
    DELETE = "delete"


def remove_falsy_values(
    from_dict: dict, *, restrict_keys: Iterable[str] = None
) -> dict:
    """
    Return a new dict with falsy values removed.
    If `restrict_keys` is given, then any keys not present in this
    iteration will be dropped.
    """
    restrict_keys = restrict_keys or from_dict.keys()
    return {
        key: from_dict[key]
        for key in restrict_keys
        if key in from_dict and from_dict[key]
    }


async def handle_create(
    args: dict,
    auth: AuthContext,
    model: ModelHelper,
):
    return await (await auth.get_logged_in_user()).and_then(
        lambda user: model.create(**_update_dict(args, {model.author_key: user.id}))
    )


async def handle_edit(
    item_id: int, auth: AuthContext, loader: Loader, edit: EditType, **args
) -> Result[None, Union[AppError, ItemNotFoundError, Unauthorized, InternalError]]:
    user_result = await (await auth.get_logged_in_user()).and_then(
        lambda user: _validate_edit_authority(item_id, user, loader)
    )
    db_result = await user_result.and_then(
        lambda user: getattr(loader.model, edit.value)(
            item_id, where={loader.model.author_key: user.id}, **args
        )
    )
    return db_result.map(lambda _: None)


async def _validate_edit_authority(
    item_id: int, user: Person, loader: Loader
) -> Result[Person, Union[ItemNotFoundError, Unauthorized]]:
    unauthorized = Unauthorized("No authority to edit this")
    row = await loader.load(item_id)

    if row is None:
        return Result(error=ItemNotFoundError(id=item_id))

    author_id = getattr(row, loader.model.author_key, None)

    if author_id is None:
        return Result(error=unauthorized)

    return Result(value=user) if (author_id == user.id) else Result(error=unauthorized)


def _update_dict(d: dict, values: Mapping):
    d.update(values)
    return d


__all__ = ["remove_falsy_values", "check_edit_authority"]
