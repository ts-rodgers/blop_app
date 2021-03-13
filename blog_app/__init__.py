import logging
from blog_app.posts.types import Post
from typing import Any, List, Optional, Union

import strawberry
from strawberry.asgi import GraphQL, ExecutionResult, GraphQLHTTPResponse

from .core import AppRequest, AppError
from .adapters.auth0 import Auth0Authenticator
from .auth.resolvers import send_login_code, login_with_code
from .posts.resolvers import get_posts
from .context import build_context
from .database import create_database_helpers
from .settings import load, Settings


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "world"

    posts = strawberry.field(get_posts)


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
        self.db_helpers = create_database_helpers(self.settings.database)

    async def get_context(
        self, request: AppRequest, response: Optional[Any] = None
    ) -> Optional[Any]:
        authenticator = Auth0Authenticator(self.settings.auth)
        return await build_context(
            request=request,
            authenticator=authenticator,
            engine=self.db_helpers.engine,
            table_map=self.db_helpers.table_map,
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
