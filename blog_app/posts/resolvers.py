import asyncio

import strawberry
from blog_app.core.types import AppError
from typing import List, Optional, Union, NewType, cast


from strawberry.types import Info

from blog_app.core import Result, AppContext, AppRequest
from .types import Post, PostRetrievalError
from .context import Context


def get_loader(info: Info[AppContext, AppRequest]):
    # The implementation of the PostContext protocol is provided by the
    # posts (this) package, and is guaranteed to be a Context.
    return cast(Context, info.context.posts).loader


async def get_posts(
    info: Info[AppContext, AppRequest],
    *,
    ids: Optional[List[int]] = None,
) -> List[Post]:
    loader = get_loader(info)
    if ids:
        results = await asyncio.gather(*(loader.load(id) for id in ids))
        return [post for post in results if post is not None]
    return [x async for x in loader.all()]


__all__ = ["get_posts"]