from dataclasses import dataclass
from typing import Optional

from .core.protocols import AppRequest, AppContext, AuthContext
from .auth import Authenticator, build_auth_context


@dataclass
class Context(AppContext):
    request: AppRequest
    auth: AuthContext


async def build_context(request: AppRequest, authenticator: Authenticator):
    return Context(request=request, auth=await build_auth_context(authenticator))
