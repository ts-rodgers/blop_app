from dataclasses import dataclass

from blog_app.core.protocols import AuthContext
from .protocols import Authenticator


@dataclass
class Context(AuthContext):
    authenticator: Authenticator


async def build_auth_context(authenticator: Authenticator) -> AuthContext:
    return Context(authenticator=authenticator)
