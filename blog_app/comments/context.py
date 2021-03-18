from dataclasses import dataclass
from typing import Any, List, Optional

from strawberry.dataloader import DataLoader

from blog_app.core.helpers import Loader
from blog_app.core.model import ModelMap
from blog_app.core.protocols import CommentContext
from blog_app.common import ModelHelper

from .types import Comment


@dataclass
class Context:
    loader: Loader[Comment]
    model: ModelHelper

    @property
    def dataloader(self):
        return self.loader.get_dataloader("id")

    @property
    def by_post_id(self):
        return self.loader.get_group_dataloader("post_id")


async def build_comment_context(model_map: ModelMap) -> CommentContext:
    loader = Loader(constructor=Comment, model=model_map["comment"])
    return Context(loader=loader, model=model_map["comment"])
