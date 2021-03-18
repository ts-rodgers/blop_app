"""
blog_app.core.result - contains a generic Result[V,E] type which
is returned from a failable operation. The Result type wraps
either a successful result (V), or an error (E). It can be used
to gracefully recover from errors without using try/except 
blocks.

>>> r1 = Result(value=10)
>>> r2 = Result(error=ValueError("an error"))
>>> r1.is_ok
True
>>> r1.is_failed
False
>>> r2.is_ok
False
>>> r2.is_failed
True
>>> r1.as_tuple()
(10, None)
>>> r2.as_tuple()
(None, ValueError(...))
"""

from dataclasses import dataclass
from collections.abc import Awaitable
from typing import (
    Any,
    Callable,
    Generic,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)


ValueType = TypeVar("ValueType", covariant=True)
ErrorType = TypeVar("ErrorType", covariant=True)
MappedType = TypeVar("MappedType")
ExceptionType = TypeVar("ExceptionType", bound=Exception)


class Result(Generic[ValueType, ErrorType]):
    """
    A Pythonic Result generic, inspired by Rust.

    The goal of this type is to act as a return type from an
    endpoint.

    The goal of this type is to help ensure that you
    always handle expected errors, using the type system
    to guard access to process results.

    >>> Result(value=10).is_ok
    True
    >>> Result(error="An error").is_ok
    False
    >>> Result.wrap(ValueError, int, "10").is_ok
    True

    """

    @classmethod
    def wrap(
        cls,
        exc_type: Type[ExceptionType],
        func: Callable[..., ValueType],
        *args,
        **kwargs,
    ) -> "Result[ValueType, ExceptionType]":
        """
        Wrap an operation with an expected exception and return a result.

        >>> Result.wrap(ValueError, int, "10")
        Result(value=10)
        >>> Result.wrap(ValueError, int, "foo")
        Result(error=ValueError(...))
        >>> Result.wrap(TypeError, int, "foo")
        Traceback (most recent call last):
            ...
        ValueError: invalid literal for int() with base 10: 'foo'
        """
        try:
            return Result(value=func(*args, **kwargs))
        except exc_type as err:
            return Result(error=err)
        except:
            raise

    _value: ValueType
    _error: ErrorType

    @overload
    def __init__(self, *, value: ValueType):
        ...

    @overload
    def __init__(self, *, error: ErrorType):
        ...

    def __init__(self, **kwargs):
        """
        Construct a new Result that contains at least a value or an
        error.

        `Result(value=v)` represents a successful operation, where the
        resulting value of the operation is `v`. It is analagous to
        `Ok(v)` in Rust.

        `Result(error=e)` represents a failured operation, where the
        failure is represented by an error value `e`. It is analagous to
        `Err(e)` in Rust.

        No other constructions of `Result` are allowed; they will raise
        an `InvalidResult` error.
        """
        if len(kwargs) == 1 and "value" in kwargs:
            self._value = kwargs["value"]

        elif len(kwargs) == 1 and "error" in kwargs:
            self._error = kwargs["error"]

        else:
            raise InvalidResult(
                "Result(value=v) and Result(error=e) the only valid constructions of this type."
            )

    def as_tuple(self) -> Union[Tuple[ValueType, None], Tuple[None, ErrorType]]:
        """
        Retrieve a tuple containing (value, error). for this result.        I

        When the result has a value, then the returned tuple is
        `(value, None)`. Similarly, when the result has an error,
        then the tuple is `(None, error)`.

        >>> Result(value=10).as_tuple()
        (10, None)
        >>> Result(error="This is an error").as_tuple()
        (None, 'This is an error')

        Pay special care to these scenarios:
        >>> Result(value=None).as_tuple()
        (None, None)
        >>> Result(error=None).as_tuple()
        (None, None)
        """
        return (self._value, None) if self.is_ok else (None, self._error)

    def collapse(self) -> Union[ValueType, ErrorType]:
        """
        Retrieve the inner value of the result, whether failed or not.

        >>> Result(value=10).collapse()
        10
        >>> Result(error="This is an error").collapse()
        'This is an error'

        This is useful in graphql resolvers which return either a success
        value or a strongly-typed error. An example of such an resolver:

        ```
        union BookResult = Book | BookRetrievalError

        type Query {
            lastBook: BookResult
        }
        ```

        ```
        @strawberry.type
        class Query:
            @strawberry.field
            async def last_book() -> Union[Book, BookRetrievalError]:
                result: Result[Book, BookRetrievalError] = await some_operation()
                return result.collapse()
        ```

        """
        return self._value if self.is_ok else self._error

    def map(
        self, func: Callable[[ValueType], MappedType]
    ) -> "Result[MappedType, ErrorType]":
        """
        Map from Result[T, E] to Result[U, E] by applying a function T -> U on
        the inner "ok" value, leaving error value untouched.


        >>> Result(value=10).map(str)
        Result(value='10')
        >>> Result(error=ValueError("Foo error")).map(int)
        Result(error=ValueError('Foo error'))

        """
        return (
            Result(value=func(self._value))
            if self.is_ok
            else cast(Result[MappedType, ErrorType], self)
        )

    def map_err(
        self, func: Callable[[ErrorType], MappedType]
    ) -> "Result[ValueType, MappedType]":
        """
        Map from Result[T, E] to Result[T, F] by applying a function E -> F on
        an inner "error" value, leaving an "ok" value untouched.


        >>> Result(value=10).map_err(str)
        Result(value=10)
        >>> Result(error=ValueError("Foo error")).map_err(str)
        Result(error='Foo error')

        """
        return (
            Result(error=func(self._error))
            if self.is_failed
            else cast(Result[ValueType, MappedType], self)
        )

    def reject(
        self, func: Callable[[ValueType], bool], error: MappedType
    ) -> "Result[ValueType, Union[ErrorType, MappedType]]":
        return (
            (Result(error=error) if func(self._value) else self) if self.is_ok else self
        )

    def set_failed(self, error: Any):
        """
        Set the result to failed with the given error. This method
        is different from others in that it does not return a new
        result, but mutates this one instead.
        """
        # fixme: refactor to eliminate this function. this scenario cannot
        # be accurately typed due to faulty logic: https://github.com/python/mypy/issues/7049

        self._error = error
        del self._value

    @overload
    def and_then(
        self, func: Callable[[ValueType], Awaitable["Result[MappedType, ErrorType]"]]
    ) -> Awaitable["Result[MappedType, ErrorType]"]:
        ...

    @overload
    def and_then(
        self, func: Callable[[ValueType], "Result[MappedType, ErrorType]"]
    ) -> "Result[MappedType, ErrorType]":
        ...

    def and_then(
        self,
        func: Union[
            Callable[[ValueType], "Result[MappedType, ErrorType]"],
            Callable[[ValueType], Awaitable["Result[MappedType, ErrorType]"]],
        ],
    ):
        """
        Calls func if the result is "ok", otherwise return the errored result.

        This function can be used to failable chain operations together:

        >>> def sq(x: int) -> Result[int, str]:
        ...     return Result(value=(x * x))

        >>> def err(x: int) -> Result[int, str]:
        ...     return Result(error=str(x))

        >>> Result(value=2).and_then(sq).and_then(sq)
        Result(value=16)
        >>> Result(value=2).and_then(sq).and_then(err)
        Result(error='4')
        >>> Result(value=2).and_then(err).and_then(sq)
        Result(error='2')
        >>> Result(error='3').and_then(sq).and_then(sq)
        Result(error='3')

        """
        if self.is_ok:
            return func(self._value)
        else:
            return _AwaitableResult(self)

    def __repr__(self):
        return (
            f"Result(value={repr(self._value)})"
            if self.is_ok
            else f"Result(error={repr(self._error)})"
        )

    @property
    def is_ok(self) -> bool:
        """Return True if this result has a value, else False."""
        return hasattr(self, "_value")

    @property
    def is_failed(self) -> bool:
        """Return True if this result has an error, else False."""
        return hasattr(self, "_error")


class _AwaitableResult(Result):
    """Awaitable proxy to a result object."""

    def __await__(self):
        yield
        return self

    def __init__(self, result):
        if result.is_ok:
            self._value = result._value

        if result.is_failed:
            self._error = result._error


class InvalidResult(TypeError):
    """Raised when attempting to operate on a `Result` that is not valid."""

    ...


__all__ = ["Result", "InvalidResult"]
