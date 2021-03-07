import strawberry
from strawberry.asgi import GraphQL


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "world"


class BlogApp(GraphQL):
    def __init__(self, **kwargs):
        kwargs.setdefault(
            "schema",
            strawberry.Schema(query=Query),
        )
        super().__init__(**kwargs)


app = BlogApp(graphiql=False)
_debug_app = BlogApp(debug=True, graphiql=True)
