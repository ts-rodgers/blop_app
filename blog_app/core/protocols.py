from typing import Protocol, Union, runtime_checkable

from strawberry.asgi import Request, WebSocket

AppRequest = Union[Request, WebSocket]


@runtime_checkable
class AuthContext(Protocol):
    ...


class AppContext(Protocol):
    request: AppRequest
    auth: AuthContext


__all__ = ["AppRequest", "AppContext", "AuthContext"]
