from typing import TypeVar

import strawberry

from .result import Result


@strawberry.interface
class AppError:
    message: str


GraphQLErrorType = TypeVar("GraphQLErrorType", bound=AppError)
ValueType = TypeVar("ValueType")
GraphQLResult = Result[ValueType, GraphQLErrorType]


__all__ = ["AppError", "GraphQLResult"]
