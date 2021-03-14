import base64
from typing import NewType, TypeVar


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

__all__ = ["AppError", "GraphQLResult"]
