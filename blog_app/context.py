from dataclasses import dataclass
from typing import Any, Optional

from .core.model import ModelMap
from .core.protocols import (
    AppRequest,
    AppContext,
    AuthContext,
    CommentContext,
    PostContext,
    ReactionContext,
)
from .auth import Authenticator, build_auth_context
from .comments import build_comment_context
from .posts import build_post_context
from .reactions import build_reaction_context
from blog_app import reactions


@dataclass
class Context(AppContext):
    request: AppRequest
    auth: AuthContext
    posts: PostContext
    comments: CommentContext
    reactions: ReactionContext


async def build_context(
    request: AppRequest, authenticator: Authenticator, model_map: ModelMap
):
    return Context(
        request=request,
        auth=await build_auth_context(authenticator, request),
        posts=await build_post_context(model_map),
        comments=await build_comment_context(model_map),
        reactions=await build_reaction_context(model_map),
    )
