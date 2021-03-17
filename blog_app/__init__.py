import logging
from typing import Any, List, Optional
from starlette.types import Receive, Scope, Send

import strawberry
from strawberry.asgi import GraphQL, ExecutionResult, GraphQLHTTPResponse

from .core import AppRequest
from .adapters.auth0 import Auth0Authenticator
from .auth.resolvers import send_login_code, login_with_code, refresh_login
from .posts.resolvers import get_posts, create_post, update_post, delete_post
from .context import build_context
from .database import create_model_map
from .settings import load, Settings


@strawberry.type
class Query:
    posts = strawberry.field(get_posts)


@strawberry.type
class Mutation:
    send_login_code = strawberry.field(send_login_code)
    login_with_code = strawberry.field(login_with_code)
    refresh_login = strawberry.field(refresh_login)
    create_post = strawberry.field(create_post)
    update_post = strawberry.field(update_post)
    delete_post = strawberry.field(delete_post)


class BlogApp(GraphQL):
    settings: Settings

    def __init__(self, **kwargs):
        kwargs.setdefault(
            "schema",
            strawberry.Schema(query=Query, mutation=Mutation),
        )
        super().__init__(**kwargs)

        self.settings = load()
        self.model_map = create_model_map(self.settings.database)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    await self.startup()
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    await self.shutdown()
                    await send({"type": "lifespan.shutdown.complete"})
                    return
        else:
            await super().__call__(scope, receive, send)

    async def startup(self):
        ...

    async def shutdown(self):
        # the same db engine is shared by all modules
        await self.model_map["post"].engine.dispose()

    async def get_context(
        self, request: AppRequest, response: Optional[Any] = None
    ) -> Optional[Any]:
        authenticator = Auth0Authenticator(self.settings.auth)
        return await build_context(
            request=request,
            authenticator=authenticator,
            model_map=self.model_map,
        )

    async def process_result(
        self, request: AppRequest, result: ExecutionResult
    ) -> GraphQLHTTPResponse:
        data: GraphQLHTTPResponse = {"data": result.data}

        if result.errors:
            data["errors"] = [err.formatted for err in result.errors]

            for error in result.errors:
                logging.exception(error.original_error)

        return data


app = BlogApp(graphiql=False)
_debug_app = BlogApp(debug=True, graphiql=True)
