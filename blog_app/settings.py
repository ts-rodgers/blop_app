from functools import partial
from typing import Callable

from typed_settings import load_settings, settings
from blog_app.adapters.auth0 import Auth0AuthenticatorSettings
from blog_app.database import DatabaseSettings


SETTINGS_FILE_NAME = "blog-app.toml"


@settings
class Settings:
    auth: Auth0AuthenticatorSettings = Auth0AuthenticatorSettings()
    database: DatabaseSettings = DatabaseSettings()


load: Callable[..., Settings] = partial(  # type: ignore
    load_settings, Settings, "blog-app", config_files=[SETTINGS_FILE_NAME]
)


__all__ = ["Settings", "load"]
