from typing import TypeVar

import strawberry

from .result import Result


@strawberry.interface
class GraphQLError:
    message: str


GraphQLErrorType = TypeVar("GraphQLErrorType", bound=GraphQLError)
ValueType = TypeVar("ValueType")
GraphQLResult = Result[ValueType, GraphQLErrorType]


__all__ = ["GraphQLError", "GraphQLResult"]
