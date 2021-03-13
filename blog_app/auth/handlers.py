import re

from strawberry.asgi import Request, WebSocket

from blog_app.core import AppRequest, Result
from .protocols import Authenticator
from .types import AuthError


auth_header_regex = re.compile(r"Bearer\s+(?P<token>.+)")


def extract_auth_token(request: AppRequest) -> Result[str, AuthError]:
    """
    Extract and return an auth token from a request if present,
    otherwise return an UNAUTHORIZED AuthError.
    """
    if "Authorization" in request.headers:
        m = auth_header_regex.match(request.headers["Authorization"])
        return (
            Result(value=m.group("token"))
            if m
            else Result(
                error=AuthError.unauthorized(
                    "Authorization header is incorrectly formatted"
                )
            )
        )

    if "access_token" in request.query_params:
        return Result(value=request.query_params["access_token"])

    return Result(
        error=AuthError.unauthorized("An access token is required for this request.")
    )