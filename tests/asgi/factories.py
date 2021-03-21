import asyncio
from typing import Any, ClassVar, List, Optional

import factory
from sqlalchemy.schema import Table
import strawberry

from blog_app.auth.types import User
from blog_app.posts.types import Post


class FakeUser(User):
    # keeps a registry of all mocked users for the current test scope
    # used stub Authenticator, so that all mock users created
    # from this factory will have access tokens that can be
    # used to authenticate during tests.
    registry: ClassVar[List["FakeUser"]] = []
    access_token: str

    def __init__(self, access_token, **kwargs):
        self.access_token = access_token
        super().__init__(**kwargs)

    @classmethod
    def find(cls, user_id: str):
        return next((user for user in cls.registry if str(user.id) == user_id), None)


class FakePost(Post):
    author: FakeUser  # type: ignore

    def __init__(self, author, **kwargs):
        self.author = author
        ModelFactory.sanitize_args(kwargs)
        super().__init__(**kwargs)


class UserFactory(factory.Factory):
    class Meta:
        model = FakeUser

    id = factory.Faker("md5")
    name = factory.Faker("name")
    access_token = factory.Faker("sha1")

    @factory.post_generation
    def post(user: FakeUser, create, value, **kwargs):
        user.registry.append(user)


class ModelFactory(factory.Factory):
    engine: ClassVar[Any] = None
    table: ClassVar[Optional[Table]] = None
    event_loop: ClassVar[Optional[asyncio.AbstractEventLoop]] = None

    id = None

    @classmethod
    def create_db_row(cls, args: dict):
        assert cls.event_loop is not None
        cls.event_loop.run_until_complete(cls.create_db_row_async(args))

    @classmethod
    async def create_db_row_async(cls, args: dict):
        assert cls.engine is not None
        assert cls.table is not None

        values = {}
        for key in args:
            if key in cls.table.c:
                values[key] = args[key]

        stmt = cls.table.insert().values(**values)
        async with cls.engine.connect() as conn:
            cursor = await conn.execute(stmt)
            await conn.commit()
            args["id"] = cursor.lastrowid

    @staticmethod
    def sanitize_args(args: dict):
        args.pop("engine", None)
        args.pop("table", None)
        args.pop("event_loop", None)

    @classmethod
    def _create(cls, model_class, **args):
        cls.sanitize_args(args)
        cls.create_db_row(args)
        return model_class(**args)

    @classmethod
    def fetch(cls, id: int):
        # Fetch an item from the db and return a matching
        # model
        assert cls.engine is not None
        assert cls.table is not None

        async def fetch_coro():
            stmt = cls.table.select().where(cls.table.c.id == id)

            async with cls.engine.connect() as conn:
                cursor = await conn.execute(stmt)
                row = cursor.fetchone()

            if row is None:
                return row

            row_dict = row._asdict()
            author = FakeUser.find(row_dict.pop("author_id"))
            assert author is not None

            return cls.build(author=author, **row)

        assert cls.event_loop is not None
        return cls.event_loop.run_until_complete(fetch_coro())


class PostFactory(ModelFactory):
    class Meta:
        model = FakePost

    title = factory.Faker("sentence", nb_words=6)
    content = factory.Faker("text", max_nb_chars=1500)
    created = factory.Faker("date_time")
    updated = factory.Faker("date_time")
    author = factory.SubFactory(UserFactory)
    author_id = factory.LazyAttribute(lambda self: self.author.id)
