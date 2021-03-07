import pytest

from blog_app.core.protocols import AuthContext
from blog_app.auth.context import build_auth_context

from .conftest import MockAuthenticator


@pytest.mark.asyncio
async def test_build_auth_context_returns_auth_context(
    authenticator: MockAuthenticator,
):
    assert isinstance((await build_auth_context(authenticator)), AuthContext)