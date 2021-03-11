from functools import partial
from os import SEEK_CUR
from typing import Callable

from typed_settings import load_settings, settings
from blog_app.adapters.auth0 import Auth0AuthenticatorSettings


SETTINGS_FILE_NAME = "blog-app.toml"


@settings
class Settings:
    auth: Auth0AuthenticatorSettings = Auth0AuthenticatorSettings()


load: Callable[..., Settings] = partial(  # type: ignore
    load_settings, Settings, "blog-app", config_files=[SETTINGS_FILE_NAME]
)


__all__ = ["Settings", "load"]
