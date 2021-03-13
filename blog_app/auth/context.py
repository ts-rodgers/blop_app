from dataclasses import dataclass
from typing import Callable

from blog_app.core.result import Result
from blog_app.core.protocols import AppRequest, AuthContext
from .handlers import extract_auth_token
from .protocols import Authenticator
from .types import AuthError, User


@dataclass
class Context:
    authenticator: Authenticator
    request: AppRequest

    async def get_logged_in_user_id(self) -> Result[str, AuthError]:
        token_result = extract_auth_token(self.request)
        user_result = await token_result.and_then(self.authenticator.get_verified_user)
        return user_result.and_then(lambda user: str(user.id))  # type: ignore


async def build_auth_context(
    authenticator: Authenticator, request: AppRequest
) -> AuthContext:
    return Context(authenticator=authenticator, request=request)
