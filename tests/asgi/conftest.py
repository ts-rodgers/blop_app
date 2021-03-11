from typing import Any, List, Optional, TypedDict

from starlette.testclient import TestClient
import pytest

from blog_app import app, BlogApp


class GraphQLResponse(TypedDict):
    data: Any
    errors: Optional[List[Any]]


class GraphQLClient(TestClient):
    def execute(
        self, query: str, *, variables: Optional[dict] = None
    ) -> GraphQLResponse:
        data = {"query": query, "variables": {} if variables is None else variables}
        response = self.post("/graphql", json=data)
        return response.json()


@pytest.fixture
def blog_app():
    return app


@pytest.fixture
def client(blog_app: BlogApp):
    return GraphQLClient(blog_app)


@pytest.fixture
def auth0(mocker):
    return mocker.patch("blog_app.adapters.auth0.Auth0Authenticator")