import asyncio
import base64
import pickle
import random
import warnings
from os import environ
from typing import Any, Generic, List, Optional, Type, TypeVar, TypedDict

import factory
import factory.random
import pytest
from pytest_factoryboy import LazyFixture, register
from pytest_mock import MockerFixture
from starlette.testclient import TestClient
import strawberry

from blog_app import app, BlogApp
from blog_app.core import Result
from blog_app.core.model import ModelMap
from blog_app.auth.types import AuthError
from blog_app.database import DatabaseSettings, create_metadata, create_model_map
from blog_app.posts.types import Post

from .factories import FakeUser, FakePost, PostFactory, UserFactory


T = TypeVar("T", bound=Post)


class Fetcher(Generic[T]):
    """Protocol for an object that allows fetching a model instance by id, directly from the DB."""

    def fetch(self, id: int) -> Optional[T]:
        ...


class GraphQLResponse(TypedDict):
    data: Any
    errors: Optional[List[Any]]


class GraphQLClient(TestClient):
    def execute(
        self, query: str, *, variables: Optional[dict] = None, access_token: str = None
    ) -> GraphQLResponse:
        headers = {}
        data = {"query": query, "variables": {} if variables is None else variables}

        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        response = self.post("/graphql", json=data, headers=headers)
        return response.json()


@pytest.fixture
def blog_app(model_map):
    app = BlogApp(debug=True, graphiql=False)
    app.model_map = model_map
    yield app


@pytest.fixture
def client(blog_app: BlogApp, event_loop):
    with GraphQLClient(blog_app) as client:
        yield client


@pytest.fixture
def post_fetcher(post_factory):
    return post_factory


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def database_settings():
    return DatabaseSettings(
        connection_url=environ.get(
            "TEST_DATABASE_URL",
            "mysql+aiomysql://blog_app:5678@127.0.0.1:3306/blog_app_test",
        ),
        echo_statements=False,
    )


@pytest.fixture(scope="session")
async def model_map(database_settings):
    # one engine per testing session is enough; we will
    # purge and drop records automatically with other
    # fixtures.
    metadata, model_map = create_metadata(database_settings)
    engine: Any = metadata.bind

    async with engine.connect() as conn:
        await conn.run_sync(metadata.drop_all)

    async with engine.connect() as conn:
        await conn.run_sync(metadata.create_all)

    yield model_map


@pytest.fixture(scope="session")
def _state():
    state = environ.get("TEST_STATE")
    random_state, locale = (None, None)
    if state:
        try:
            random_state, locale = pickle.loads(base64.b64decode(state.encode("ascii")))
        except:
            warnings.warn(
                f"Supplied testing state is invalid. Regenerating a new test state."
            )

    if not (random_state and locale):
        random_state = factory.random.get_random_state()
        locale = random.choice(["de_AT", "en_US"])
        state = base64.b64encode(pickle.dumps((random_state, locale))).decode("ascii")

    else:
        factory.random.set_random_state(random_state)

    yield (state, locale)


@pytest.fixture
def locale(_state):
    _, locale = _state
    print(f"Locale: {locale}")
    yield locale


@pytest.fixture(autouse=True)
def state(_state):
    state, _ = _state
    yield
    print("To reproduce this exact test run, set your environment:\n")
    print(f"TEST_STATE={state}")


@pytest.fixture(autouse=True)
def fakersettings(locale):
    with factory.Faker.override_default_locale(locale):
        yield


@pytest.fixture(autouse=True)
def allow_fake_user_login(mocker: MockerFixture):
    # reset the registry, so that user fixtures from
    # the last tests are not allowed to login during this test
    FakeUser.registry = []

    async def get_verified_user_stub(token: str):
        matching_user = next(
            (user for user in FakeUser.registry if user.access_token == token), None
        )
        return (
            Result(value=matching_user)
            if matching_user
            else Result(error=AuthError.invalid_token("invalid access token"))
        )

    async def get_users_by_ids_stub(ids: List[strawberry.ID]):
        users_by_id = {}

        for user in FakeUser.registry:
            users_by_id[user.id] = user

        return [users_by_id.get(user_id) for user_id in ids]

    get_users_by_ids_mock = mocker.patch(
        "blog_app.adapters.auth0.Auth0Authenticator.get_users_by_ids",
        wraps=get_users_by_ids_stub,
    )
    get_verified_user_mock = mocker.patch(
        "blog_app.adapters.auth0.Auth0Authenticator.get_verified_user",
        wraps=get_verified_user_stub,
    )


@pytest.fixture(autouse=True)
def setup_auto_insert_model_factory_instances(
    post_factory: Type[PostFactory],
    model_map: ModelMap,
    event_loop: asyncio.AbstractEventLoop,
):

    post_model = model_map["post"]
    post_factory.engine = post_model.engine
    post_factory.table = post_model.table
    post_factory.event_loop = event_loop


register(UserFactory)
register(PostFactory)
register(UserFactory, "user")
register(PostFactory, "post")