import base64
import logging
import traceback
from contextlib import contextmanager
from typing import Any, Awaitable, Callable, NewType, Optional, TypeVar


import strawberry

from .result import Result


@strawberry.interface
class AppError:
    message: str


GraphQLErrorType = TypeVar("GraphQLErrorType", bound=AppError)
ValueType = TypeVar("ValueType")
GraphQLResult = Result[ValueType, GraphQLErrorType]


ID = strawberry.scalar(
    NewType("ID", str),
    serialize=lambda v: base64.b64encode(v.encode("utf-8")).decode("utf-8"),
    parse_value=lambda v: base64.b64decode(v.encode("utf-8")).decode("utf-8"),
)


@strawberry.type
class InternalError(AppError):
    def __init__(self, original_exception: Optional[Exception] = None):
        self.original_exception = original_exception

        if original_exception:
            logging.error(f"Operation failed: {str(original_exception)}")
            logging.error(
                "".join(traceback.format_tb(original_exception.__traceback__))
            )

    @strawberry.field()
    def message(self) -> str:
        return "An internal error has occurred."

    @staticmethod
    async def wrap(
        func: Callable[..., Awaitable[ValueType]], *args, **kwargs
    ) -> Result[ValueType, "InternalError"]:
        return (await Result.wait_and_wrap(Exception, func, *args, **kwargs)).map_err(
            InternalError
        )


@strawberry.type
class ItemNotFoundError(AppError):
    id: int

    def __init__(self, id=int, message: str = "The requested item could not be found."):
        self.id = id
        self.message = message


__all__ = ["AppError", "InternalError", "ItemNotFoundError", "GraphQLResult"]
