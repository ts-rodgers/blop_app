from enum import Enum
from typing import Protocol

import strawberry

from blog_app.core import GraphQLError


class LoginCodeTransport(Enum):
    EMAIL = "email"
    SMS = "sms"


class AuthErrorReason(Enum):
    INVALID_REQUEST = "invalid_request"
    TEMPORARY_FAILURE = "temporoary_auth_failure"


@strawberry.type
class AuthError(GraphQLError):
    reason: AuthErrorReason


@strawberry.type
class User:
    id: strawberry.ID
    name: str


@strawberry.type
class Authentication:
    user: User
    token: str
    refresh_token: str


@strawberry.type
class SendLoginCodeResponse:
    email_address: str


__all__ = ["AuthError", "AuthErrorReason", "LoginCodeTransport", "User"]
