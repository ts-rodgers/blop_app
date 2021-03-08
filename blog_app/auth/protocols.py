from typing import Protocol

from blog_app.core.types import GraphQLResult
from .types import AuthError, Authorization, LoginCodeTransport


class Authenticator(Protocol):
    async def send_login_code(
        self, login: str, login_type: LoginCodeTransport
    ) -> GraphQLResult[None, AuthError]:
        """
        Send a login code to a user using the specified transport.

        :param login: The target for the login code. If `login_type=="email"`
                      then this should be an email address. Likewise, it
                      should be a phone number if `login_type=="sms"`

        :param login_type: Indicates whether the login code should be
                           sent via `"email"` or `"sms"`.
                           if an unsupported value is received, then
                           `Result.err(UnsupportedLoginCodeTransport(...))`
                           ought to be returned.

        :returns: A `Result[Any, AuthError]` which should be used to indicate
                  failure.

        """

    async def login_with_code(
        self, code: str, login: str, login_type: LoginCodeTransport
    ) -> GraphQLResult[Authorization, AuthError]:
        """
        Verify a login code and return an Authentication.

        :param code: A code to be verified.

        :param login: This is where the login code was originally sent.

        :param login_type: Indicates whether the login code was
                           sent via `"email"` or `"sms"`.

        :returns: A `Result[Authentication, AuthError]` which should
                  also be used to indicate failure.

        """


__all__ = ["Authenticator"]
