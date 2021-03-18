from dataclasses import dataclass
from typing import Any, Optional

from .core.model import ModelMap
from .core.protocols import (
    AppRequest,
    AppContext,
    AuthContext,
    CommentContext,
    PostContext,
)
from .auth import Authenticator, build_auth_context
from .comments import build_comment_context
from .posts import build_post_context


@dataclass
class Context(AppContext):
    request: AppRequest
    auth: AuthContext
    posts: PostContext
    comments: CommentContext


async def build_context(
    request: AppRequest, authenticator: Authenticator, model_map: ModelMap
):
    return Context(
        request=request,
        auth=await build_auth_context(authenticator, request),
        posts=await build_post_context(model_map),
        comments=await build_comment_context(model_map),
    )
