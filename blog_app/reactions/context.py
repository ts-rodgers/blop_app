from dataclasses import dataclass

from blog_app.core.helpers import Loader
from blog_app.core.model import ModelHelper, ModelMap
from blog_app.core.protocols import ReactionContext

from .types import Reaction


@dataclass
class Context:
    loader: Loader[Reaction]
    model: ModelHelper

    @property
    def by_comment_id(self):
        return self.loader.get_group_dataloader("comment_id")


async def build_reaction_context(model_map: ModelMap) -> ReactionContext:
    loader = Loader(constructor=Reaction, model=model_map["reaction"])
    return Context(loader=loader, model=model_map["reaction"])
