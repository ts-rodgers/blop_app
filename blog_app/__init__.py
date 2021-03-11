from typing import Any, Optional

import strawberry
from strawberry.asgi import GraphQL

from .core import AppRequest
from .adapters.auth0 import Auth0Authenticator
from .auth.resolvers import send_login_code, login_with_code
from .context import build_context
from .settings import load, Settings


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "world"


@strawberry.type
class Mutation:
    send_login_code = strawberry.field(send_login_code)
    login_with_code = strawberry.field(login_with_code)


class BlogApp(GraphQL):
    settings: Settings

    def __init__(self, **kwargs):
        kwargs.setdefault(
            "schema",
            strawberry.Schema(query=Query, mutation=Mutation),
        )
        super().__init__(**kwargs)

        self.settings = load()

    async def get_context(
        self, request: AppRequest, response: Optional[Any] = None
    ) -> Optional[Any]:
        authenticator = Auth0Authenticator(self.settings.auth)
        return await build_context(request=request, authenticator=authenticator)


app = BlogApp(graphiql=False)
_debug_app = BlogApp(debug=True, graphiql=True)
