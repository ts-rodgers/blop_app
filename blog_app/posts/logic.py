import re
import enum

from blog_app.core import Result

whitespace_regex = re.compile(r"\s+")


def coerce_title(title: str) -> Result[str, str]:
    """
    Collapse whitespace within a string and trim both ends.

    If the string is empty afterward, a ValueError will be raised.
    (since this function is intended to be used as a scalar; strawberry
    will convert the value error into a validation error on the field)
    """
    fixed = whitespace_regex.sub(" ", title.strip())
    return (
        Result(value=fixed)
        if fixed
        else Result(error="PostTitle cannot contain only whitespace.")
    )
