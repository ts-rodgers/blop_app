import os
from contextlib import contextmanager
from pathlib import Path

import pytest
import toml

from blog_app.adapters.auth0 import Auth0AuthenticatorSettings
from blog_app.settings import load, SETTINGS_FILE_NAME, Settings


@pytest.fixture
def good_settings():
    return {
        "blog-app": {
            "auth": {
                "domain": "test.example.com",
                "client_id": "foo-bar-client",
                "client_secret": "my-super-super-secret",
            }
        }
    }


@pytest.fixture
def good_settings_path(tmp_path: Path, good_settings):
    settings_path = tmp_path / "blog-app.toml"
    settings_path.write_text(toml.dumps(good_settings))
    return settings_path


@contextmanager
def chdir(path: Path):
    cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(cwd)


@contextmanager
def setenv(key: str, val: str):
    old_val = os.environ.get(key)
    os.environ[key] = val
    yield

    if old_val is None:
        del os.environ[key]
    else:
        os.environ[key] = old_val


@pytest.mark.parametrize(
    "settings_file_context",
    [
        # load settings from current directory
        lambda p: chdir(p.parent),
        # load settings from BLOG_APP_SETTINGS env var
        lambda p: setenv("BLOG_APP_SETTINGS", str(p)),
    ],
)
def test_settings_load_with_valid_data(
    good_settings_path: Path, good_settings: dict, settings_file_context
):
    """Check that loading settings works as expected with valid data."""

    with settings_file_context(good_settings_path):
        settings = load()

    assert isinstance(settings, Settings)
    assert isinstance(settings.auth, Auth0AuthenticatorSettings)
    assert settings.auth.domain == good_settings["blog-app"]["auth"]["domain"]
    assert settings.auth.client_id == good_settings["blog-app"]["auth"]["client_id"]
    assert (
        settings.auth.client_secret
        == good_settings["blog-app"]["auth"]["client_secret"]
    )
