from datetime import datetime
from enum import Enum

import strawberry

from blog_app.core import GraphQLError


class LoginCodeTransport(Enum):
    EMAIL = "email"
    SMS = "sms"


class AuthErrorReason(Enum):
    TEMPORARY_FAILURE = "temporary_failure"
    INVALID_REQUEST = "invalid_request"
    INTERNAL_ERROR = "internal_error"
    INVALID_TOKEN = "token_validation_failed"


@strawberry.type
class AuthError(GraphQLError):
    reason: AuthErrorReason
    originalMessage: strawberry.Private[str]

    def __init__(self, reason: AuthErrorReason, message: str):
        self.reason = reason
        self.originalMessage = message

    @strawberry.field
    def message(self) -> str:
        # when this is an internal error, hide the error
        # message.
        return (
            "An internal error has occurred"
            if self.reason == AuthErrorReason.INTERNAL_ERROR
            else self.originalMessage
        )


@strawberry.type
class User:
    id: strawberry.ID
    name: str


@strawberry.type
class Authorization:
    user: User
    access_token: str
    refresh_token: str
    expires_in: int

    @strawberry.field
    def token_type(self) -> str:
        return "Bearer"


@strawberry.type
class SendLoginCodeResponse:
    email_address: str


__all__ = ["AuthError", "AuthErrorReason", "LoginCodeTransport", "User"]
