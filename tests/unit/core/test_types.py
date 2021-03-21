import asyncio
import logging

import pytest
from blog_app.core.types import InternalError


@pytest.mark.asyncio
async def test_internal_error_logs_exception_message(caplog):
    async def failing_operation():
        await asyncio.sleep(0)
        raise Exception("something bad happened")

    with caplog.at_level(logging.ERROR):
        result = await InternalError.wrap(failing_operation)

    assert f"Operation failed: something bad happened" in caplog.text

    assert result.is_failed
    assert isinstance(result.collapse(), InternalError)