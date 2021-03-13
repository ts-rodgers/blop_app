from dataclasses import dataclass
from typing import Any, Optional

from .core.model import ModelMap
from .core.protocols import AppRequest, AppContext, AuthContext, PostContext
from .auth import Authenticator, build_auth_context
from .posts import build_post_context


@dataclass
class Context(AppContext):
    request: AppRequest
    auth: AuthContext
    posts: PostContext


async def build_context(
    request: AppRequest, authenticator: Authenticator, engine: Any, table_map: ModelMap
):
    return Context(
        request=request,
        auth=await build_auth_context(authenticator, request),
        posts=await build_post_context(engine, table_map),
    )
