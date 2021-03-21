import pytest
from pytest_mock import MockerFixture

from blog_app.core import InvalidResult, Result


def test_construct_result_without_args_is_invalid():
    """Ensure Result() will raise an error."""
    with pytest.raises(InvalidResult):
        Result()  # type: ignore
        # small joys in life: when your type checker lints invalid constructs,
        # so you have to skip the linting in order to test correct behavior
        # on invalid constucts.


def test_construct_result_with_value_and_error_is_invalid():
    """Ensure Result(value=v, error=e) will raise an error."""
    with pytest.raises(InvalidResult):
        Result(value=10, error=ValueError("an error"))  # type: ignore


def test_wrap_catches_expected_errors():
    """Ensure that `Result.wrap` catches the error type it's supposed to."""
    assert Result.wrap(ValueError, int, "foo").is_failed


def test_wrap_raises_unexpected_errors():
    """Ensure that `Result.wrap` does not catch errors it does not expect."""
    with pytest.raises(ValueError):
        result = Result.wrap(TypeError, int, "foo")


def test_wrap_on_sunny_day():
    """Ensure that `Result.wrap` wraps the return value when there are no errors."""
    value, _ = Result.wrap(ValueError, int, "100").as_tuple()
    assert value == 100


@pytest.mark.asyncio
async def test_async_wrap_catches_expected_errors():
    """Ensure that `Result.wait_and_wrap` catches the error type it's supposed to."""

    async def convert_value(val):
        return int(val)

    result = await Result.wait_and_wrap(ValueError, convert_value, "foo")
    _, error = result.as_tuple()
    assert isinstance(error, ValueError)


@pytest.mark.asyncio
async def test_async_wrap_ignores_unexpected_errors():
    """Ensure that `Result.wait_and_wrap` catches the error type it's supposed to."""

    async def convert_value(val):
        return int(val)

    with pytest.raises(ValueError):
        result = await Result.wait_and_wrap(TypeError, convert_value, "foo")


@pytest.mark.asyncio
async def test_async_wrap_on_sunny_day():
    """Ensure that `Result.wait_and_wrap` wraps return value when there are no errors."""

    async def convert_value(val):
        return int(val)

    result = await Result.wait_and_wrap(TypeError, convert_value, "100")
    value, _ = result.as_tuple()
    assert value == 100


@pytest.mark.parametrize("value", [0, None, "foo", [28, 3]])
def test_ok_marks_success(value):
    """Ensure that `Result(value=v)` produces 'ok' Results."""
    assert Result(value=value).is_ok


@pytest.mark.parametrize("err", [ValueError("Foo"), TypeError("Bar"), None, 10])
def test_err_marks_failure(err):
    """Ensure that `Result(error=e)` produces 'failed' Results."""
    assert Result(error=err).is_failed
