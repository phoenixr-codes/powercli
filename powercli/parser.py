"""Classes returned when parsing a command.

The actual parsing logic happens in {py:meth}`powercli.command.Command.parse_args`.
"""

from __future__ import annotations

__all__ = ["ParsedCommand", "ParsedArgument", "ParsedFlag", "ParsedPositional"]

from abc import ABCMeta
from collections.abc import Collection
from typing import TYPE_CHECKING, Any

from attrs import define

if TYPE_CHECKING:
    from .args import Argument, Flag, Positional
    from .command import Command
    from .typedefs import Identifier


@define(kw_only=True)
class ParsedCommand[FV, PV]:
    """The result of a parsed command."""

    command: Command[FV, PV]
    """The command that got parsed."""

    raw_args: list[str]
    """The raw arguments passed to invoke the command."""

    _parsed_flags: list[ParsedFlag[FV]]
    """The flags that have been parsed."""

    _parsed_positionals: list[ParsedPositional[PV]]
    """The positionals that have been parsed."""

    _parsed_commands: list[ParsedCommand[FV, PV]]
    """The subcommands that have been parsed."""

    def _all_args(self) -> list[ParsedFlag[FV] | ParsedPositional[PV]]:
        """Returns a list of all parsed arguments."""
        return [
            *self._parsed_flags,
            *self._parsed_positionals,
        ]

    def is_present(self, identifier: Identifier, /) -> bool:
        """Returns `True` when an argument with a certain identifier has been parsed."""
        return identifier in {a.arg.identifier for a in self._all_args()}

    def is_absent(self, identifier: Identifier, /) -> bool:
        """Returns `True` when an argument with a certain identifier has not been parsed."""
        return not self.is_present(identifier)

    def value_of_positional(self, identifier: Identifier, /) -> PV | str:
        """Returns the value the positional with a certain identifier holds."""
        for arg in self._parsed_positionals:
            if arg.arg.identifier == identifier:
                return arg.value
        raise RuntimeError(f"no such positional {identifier}")

    def value_of_flag(self, identifier: Identifier, /) -> Collection[FV | int] | None:
        """Returns the value the flag with a certain identifier holds."""
        for arg in self._parsed_flags:
            if arg.arg.identifier == identifier:
                return arg.values
        raise RuntimeError(f"no such flag {identifier}")

    def value_of(
        self, identifier: Identifier, /
    ) -> PV | str | Collection[FV | int] | None:
        """Returns the value the argument with a certain identifier holds."""
        for arg in self._all_args():
            if arg.arg.identifier == identifier:
                if isinstance(arg, ParsedFlag):
                    return arg.values
                elif isinstance(arg, ParsedPositional):
                    return arg.value
        raise RuntimeError(f"no such argument {identifier}")


@define(kw_only=True)
class ParsedArgument(metaclass=ABCMeta):
    """A parsed argument."""

    arg: Argument
    """The argument object that has been parsed."""


@define(kw_only=True)
class ParsedFlag[T](ParsedArgument):
    """A parsed flag."""

    arg: Flag[Any, Any, T]
    """The flag that got parsed."""

    raw_values: list[str] | None
    """
    The raw values that were supplied in the command-line or in the
    {py:meth}`powercli.command.Command.parse_args` method.

    This may be `None` when the flag was not specified.
    """

    values: Collection[T | int] | None
    """The converted parsed values."""


@define(kw_only=True)
class ParsedPositional[T](ParsedArgument):
    """A parsed positional."""

    arg: Positional[Any, Any, T]
    """The positional that got parsed."""

    raw_value: str | None
    """
    The raw value that was supplied in the command-line or in the
    {py:meth}`powercli.command.Command.parse_args` method.

    This may be `None` when the positional was not specified.
    """

    value: T | str
    """The converted parsed value."""
