"""Utilities related to commands and arguments."""

from __future__ import annotations

__all__ = ["static", "member_of", "one_of", "ArgIterator"]
import difflib
from collections import deque
from collections.abc import Iterable, Iterator, Sequence
from enum import StrEnum
from typing import TYPE_CHECKING
from warnings import deprecated

from attrs import define

from .static import Static

if TYPE_CHECKING:
    from .args import Argument, Flag
    from .typedefs import Context, Converter, WithContext


@deprecated("powercli.utils.static is deprecated in favor of powercli.static.Static")
def static[T](value: T, /) -> Static[T]:
    """
    Returns a callable which depends the provided value ignoring the supplied
    arguments.

    ```{deprecated} 0.2.0
    Deprecated in favor of {py:obj}`powercli.static.Static`.
    ```

    # Examples

    ```python
    from powercli import Flag

    Flag(
        # ...
        required=static(True)
    )
    ```
    """
    return Static(value)


def member_of(enum: type[StrEnum], *, ignore_case: bool = True) -> Converter[str]:
    """
    Creates a converter for an enum type.

    # Parameters

    * `enum` - The enum type with the members' values being the possible
      values.
    * `ignore_case` - Ignore case when finding enum member.
    """

    def to_enum_member(raw: str) -> str:
        """Converts a raw value into the according enum member."""
        for member in enum:
            if ignore_case and member.casefold() == raw.casefold():
                return member
            elif member == raw:
                return member
        raise ValueError(f"{raw!r} is not a possible value for {enum!r}")

    return to_enum_member


def one_of[FV, PV](
    *flags: Flag[FV, PV, FV],
    required: WithContext[FV, PV, bool] = Static(False),
) -> Iterable[Flag[FV, PV, FV]]:
    """
    Modifies each flag to only be allowed when all other flags are absent.

    # Parameters

    * `required` - Whether any of the flags is required.
    """
    for flag in flags:
        others: set[str] = {
            f.identifier for f in flags if f.identifier != flag.identifier
        }

        def is_allowed(
            ctx: Context[FV, PV],
            flag: Flag[FV, PV, FV] = flag,
            others: set[str] = others,
            allowed: WithContext[FV, PV, str | bool] = flag.allowed,
        ) -> str | bool:
            """Determines whether a mutually exclusive flag is allowed."""
            unique = all(ctx.is_absent(f) for f in others)
            if not unique:
                return f"{flag} conflicts with {others}"
            return allowed(ctx)

        def is_required(
            ctx: Context[FV, PV],
            flag: Flag[FV, PV, FV] = flag,
            others: set[str] = others,
            required: WithContext[FV, PV, str | bool] = flag.required,
            any_required: WithContext[FV, PV, str | bool] = required,
        ) -> str | bool:
            """Determines whether a mutually exclusive flag is required."""
            req = any_required(ctx)
            message = f"{_enumerate(list(map(repr, flags)), join_last='or', multi_prefix='exactly one of ')} is required"
            if isinstance(req, str):
                message = f"{message}; {req}"
                req = True
            if req:
                all_absent = all(ctx.is_absent(f.identifier) for f in flags)
                if all_absent:
                    return message
            return required(ctx)

        flag.allowed = is_allowed
        flag.required = is_required
    return flags


def _not_unique[T](*sets: set[T]) -> T | None:
    """
    Returns an item that is present in at least two of the given sets.
    """
    items = []
    for s in sets:
        for item in s:
            if item in items:
                return item
            items.append(item)
    return None


def _did_you_mean(word: str, possibilities: Iterable[str]) -> str | None:
    """
    Returns a message suggesting commands with a similar name or `None` if there
    was no command with a similar name.
    """
    similar = difflib.get_close_matches(word, possibilities)
    return (
        f"did you mean {_enumerate(list(map(repr, similar)), join_last='or', multi_prefix='one of ')}?"
        if similar
        else None
    )


def _enumerate(
    seq: Sequence[str], *, join: str = ", ", join_last: str, multi_prefix: str = ""
) -> str:
    """Returns a enumerated representation of a sequence.

    # Parameters

    * `seq`
    * `join` - A string inserted between instances of `seq`.
    * `join_last` - A string inserted between the two last instances of `seq`.
    * `multi_prefix` - A string prepended if `seq` contains multiple instances.
    """
    match seq:
        case [x]:
            return x
        case [*x]:
            return multi_prefix + join.join(seq[:-1]) + f" {join_last} {seq[-1]}"
        case _:
            raise NotImplementedError(f"invalid length {len(seq)}")


def _single_name_of_arg(arg: Argument) -> str:
    """Returns the preferred name of an argument.

    For a flag this is the long variant if set otherwise the short variant.
    """
    from .args import Flag, Positional

    if isinstance(arg, Flag):
        if arg.long is not None:
            return arg.long
        if arg.short is not None:
            return arg.short
        assert False
    if isinstance(arg, Positional):
        return arg.name
    assert False


@define
class ArgIterator(Iterator[str]):
    """An iterator over raw arguments."""

    _data: deque[str]

    def __next__(self) -> str:
        """Yields the next raw argument."""
        if not self._data:
            raise StopIteration
        return self._data.popleft()

    def prepend(self, value: str) -> None:
        """
        Prepends the iterator with a value.

        This makes it possible to peek the iterator.
        """
        self._data.appendleft(value)
