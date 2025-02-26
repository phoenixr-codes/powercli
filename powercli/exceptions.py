"""Exceptions/Errors used by PowerCLI."""

from __future__ import annotations

__all__ = [
    "ConversionError",
    "MissingValueError",
    "MissingPositionalError",
    "MissingFlagError",
    "MissingDependencyError",
]
from typing import Any

from attrs import define

from .args import Argument, Flag, Positional
from .typedefs import Converter
from .utils import _enumerate, _single_name_of_arg


@define
class ConversionError(Exception):
    """An error that occurred while converting a value."""

    raw: str
    """The raw input value that could not be converted."""

    converter: Converter[Any]
    """The function that is supposed to convert the value."""

    def __str__(self) -> str:
        """Returns a string representation of the error."""
        return f"could not convert {self.raw!r} by using {self.converter.__name__!r}"


@define
class MissingValueError(Exception):
    """A flag expected a value that was not provided by the user."""

    flag: Flag[Any, Any, Any]
    """The flag that expected a value."""

    index: int
    """The index of the missing value."""

    name: str
    """The name of the missing value."""

    def __str__(self) -> str:
        """Returns a string representation of the error."""
        return f"flag {self.flag} expects {self.name} at index {self.index}"


@define
class MissingPositionalError(Exception):
    """The user did not provide a required positional."""

    positional: Positional[Any, Any, Any]
    """The positional that was missing."""

    def __str__(self) -> str:
        """Returns a string representation of the error."""
        return f"missing value for {self.positional}"


@define
class MissingFlagError(Exception):
    """The user did not provide a required flag."""

    flag: Flag[Any, Any, Any]
    """The flag that was missing."""

    def __str__(self) -> str:
        """Returns a string representation of the error."""
        return f"missing value for {self.flag}"


@define
class MissingDependencyError(Exception):
    """A dependency of an argument is missing."""

    arg: Argument
    """The argument with a dependency."""

    dependencies: set[str]
    """The set of identifiers which {py:attr}`arg` depends on."""

    def __str__(self) -> str:
        """Returns a string representation of the error."""
        return f"argument {_single_name_of_arg(self.arg)} depends on {_enumerate(sorted(self.dependencies), join_last='and')} which {'is' if len(self.dependencies) == 1 else 'are'} not specified"
