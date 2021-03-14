from typing import cast


from strawberry.types import Info

from blog_app.core import AppContext, AppRequest
from blog_app.core.helpers import Collection
from .types import Post
from .context import Context


def get_loader(info: Info[AppContext, AppRequest]):
    # The implementation of the PostContext protocol is provided by the
    # posts (this) package, and is guaranteed to be a Context.
    return cast(Context, info.context.posts).loader


async def get_posts(info: Info[AppContext, AppRequest]) -> Collection[Post]:
    loader = get_loader(info)
    return Collection(loader=loader)


__all__ = ["get_posts"]
