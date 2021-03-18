"""
blog_app.core.protocols -- interfaces for inter-module communication 

"""

from typing import (
    Awaitable,
    Hashable,
    List,
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


@strawberry.interface
class Person:
    id: strawberry.ID
    name: str


@strawberry.interface(name="Post")
class AppPost:
    id: int


@strawberry.interface(name="AppComment")
class AppComment:
    id: int
    content: str
    author: Person


@runtime_checkable
class AuthContext(Protocol):
    @property
    def users(self) -> Dataloader[strawberry.ID, Optional[Person]]:
        ...

    async def get_logged_in_user(self) -> Result[Person, AppError]:
        ...


@runtime_checkable
class PostContext(Protocol):
    @property
    def dataloader(self) -> Dataloader[int, Optional[AppPost]]:
        ...


@runtime_checkable
class CommentContext(Protocol):
    @property
    def dataloader(self) -> Dataloader[int, Optional[AppComment]]:
        ...

    @property
    def by_post_id(self) -> Dataloader[int, List[AppComment]]:
        ...


class AppContext(Protocol):
    request: AppRequest
    auth: AuthContext
    posts: PostContext
    comments: CommentContext


__all__ = [
    "AppRequest",
    "AppContext",
    "AuthContext",
    "CommentContext",
    "PostContext",
    "Person",
    "AppPost",
    "AppComment",
]
