import logging
from typing import Union, cast
from strawberry.types import Info

from blog_app.core import Result, AppContext, AppRequest
from .types import (
    AuthError,
    AuthErrorReason,
    Authorization,
    LoginCodeTransport,
    SendLoginCodeResponse,
)
from .context import Context


def get_authenticator(info: Info[AppContext, AppRequest]):
    # The implementation of the AuthContext protocol is provided by the
    # auth (this) package, and is guaranteed to be a Context.
    return cast(Context, info.context.auth).authenticator


async def send_login_code(
    email_address: str, info: Info[AppContext, AppRequest]
) -> Union[SendLoginCodeResponse, AuthError]:
    try:
        result = await get_authenticator(info).send_login_code(
            email_address, LoginCodeTransport.EMAIL
        )
    except Exception:  # unexpected error which cannot be recovered
        logging.exception("An internal application error has occurred.")
        return AuthError(
            reason=AuthErrorReason.INTERNAL_ERROR, message="Internal error."
        )
    else:
        return result.map(
            lambda _: SendLoginCodeResponse(email_address=email_address)
        ).collapse()


async def login_with_code(
    code: str, email_address: str, info: Info[AppContext, AppRequest]
) -> Union[Authorization, AuthError]:
    try:
        return (
            await get_authenticator(info).login_with_code(
                code, email_address, LoginCodeTransport.EMAIL
            )
        ).collapse()
    except Exception:  # unexpected error which cannot be recovered
        return AuthError(
            reason=AuthErrorReason.INTERNAL_ERROR, message="Internal error."
        )
