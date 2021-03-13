from typing import Protocol, Union, runtime_checkable

from strawberry.asgi import Request, WebSocket

from blog_app.core.loader import Loader
from blog_app.core.result import Result
from blog_app.core.types import AppError

AppRequest = Union[Request, WebSocket]


class AppPost(Protocol):
    id: int


@runtime_checkable
class AuthContext(Protocol):
    async def get_logged_in_user_id(self) -> Result[str, AppError]:
        """
        Get the currently logged in user's id.

        The operation returns a Result, which can be useful to chain
        additional operations onto a successful retrieval of a user
        id:

        ```
        result = await ctx.auth.get_logged_in_user_id()
        result = await result.and_then(getUserPostsAsync)
        result = result.and_then(filterPostsByCriteria)
        ```

        If there is no properly verified logged in user, then a
        GraphQLError is returned in the result instead. This can either
        by mapped to a more specific error, or returned directly from a
        resolver to be rendered in GraphQL.
        """


@runtime_checkable
class PostContext(Protocol):
    loader: Loader[AppPost]


class AppContext(Protocol):
    request: AppRequest
    auth: AuthContext
    posts: PostContext


__all__ = ["AppRequest", "AppContext", "AuthContext"]
