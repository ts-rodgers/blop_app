import pytest
from unittest.mock import Mock

from blog_app.core.types import GraphQLResult
from blog_app.auth.protocols import Authenticator


class MockAuthenticator(Mock):
    """Fake Authenticator for testing with."""

    def __init__(self):
        super().__init__(spec=Authenticator)


@pytest.fixture
def authenticator():
    return MockAuthenticator()
