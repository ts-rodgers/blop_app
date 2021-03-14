"""
blog_app.core.protocols -- interfaces for inter-module communication 

"""

from typing import (
    Awaitable,
    Hashable,
    Optional,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)
import strawberry

from strawberry.asgi import Request, WebSocket

from blog_app.core.result import Result
from blog_app.core.types import AppError

AppRequest = Union[Request, WebSocket]
KeyType = TypeVar("KeyType", contravariant=True, bound=Hashable)
LoaderType = TypeVar("LoaderType", covariant=True)


class Dataloader(Protocol[KeyType, LoaderType]):
    def load(self, key: KeyType) -> Awaitable[LoaderType]:
        ...


class AppUser(Protocol):
    id: strawberry.ID


class AppPost(Protocol):
    id: int


@runtime_checkable
class AuthContext(Protocol):
    async def get_logged_in_user(self) -> Result[AppUser, AppError]:
        ...


@runtime_checkable
class PostContext(Protocol):
    @property
    def dataloader(self) -> Dataloader[int, Optional[AppPost]]:
        ...


class AppContext(Protocol):
    request: AppRequest
    auth: AuthContext
    posts: PostContext


__all__ = ["AppRequest", "AppContext", "AuthContext"]
