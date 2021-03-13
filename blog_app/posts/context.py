from dataclasses import dataclass
from typing import Any

from blog_app.core import Loader
from blog_app.core.model import ModelMap
from blog_app.core.protocols import AppRequest, PostContext
from .types import Post


@dataclass
class Context:
    loader: Loader[Post]


async def build_post_context(engine: Any, table_map: ModelMap) -> PostContext:
    loader = Loader(constructor=Post, engine=engine, table=table_map["post"])
    return Context(loader=loader)  # type: ignore
