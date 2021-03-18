import base64
import logging
from contextlib import contextmanager
from typing import Any, NewType, TypeVar


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
    def __init__(self, message: str = None):
        self.original_message = message

    @strawberry.field()
    def message(self) -> str:
        return "An internal error has occurred."

    @staticmethod
    @contextmanager
    def from_exception():
        """
        A context manager that lets wrap a failable operation in
        a Result[None, InternalError], such that when code ran within
        the context throws an Exception, an application error is logged
        and the Result is set to failed with an InternalError.

        >>> with InternalError.from_exception() as result:
        ...     raise ValueError()
        >>> result
        Result(error=InternalError(...))

        Since InternalError is a graphql type, the result can be collapsed
        into a possible InternalError and returned directly from the resolver.

        >>  with InternalError.from_exception() as result:
        ..      result = result.and_then(...).map(...).etc()
        >>  return result

        Note: it is important to make only one reassignment of the result
        within the context for this pattern to work. This is because the
        error is only set on the originally yielded result; if you manage
        to successfully reassign the name, then you will have thrown away
        the result upon which any future error will be set. If you need
        to make multiple reassignments, use this pattern instead:

        >>  with InternalError.from_exception() as result:
        ..      user_result = result.and_then(...).map(...)
        >>  return result.and_then(lambda _: user_result)

        Note how this pattern leaves the original result which might have
        an error in tact. In case of an error, result.and_then() would resolve to a
        result which contains the error.

        """
        result = Result[None, InternalError](value=None)
        try:
            yield result
        except:
            logging.exception("Operation failed")
            result.set_failed(InternalError())


@strawberry.type
class ItemNotFoundError(AppError):
    id: int

    def __init__(self, id=int, message: str = "The requested item could not be found."):
        self.id = id
        self.message = message


__all__ = ["AppError", "InternalError", "ItemNotFoundError", "GraphQLResult"]
