"""Common commands and flags."""

# TODO: list common prints table with each category

from __future__ import annotations

__all__ = [
    "HelpCommand",
    "HelpFlag",
    "VersionCommand",
    "VersionFlag",
    "ListCommand",
    "ListFlag",
]


import sys
from typing import Any, NoReturn, cast

from ._help_utils import help_message
from .args import Flag
from .command import Command
from .methods import Switch
from .utils import static


class HelpCommand[FV, PV](Command[FV, PV]):
    """A help command."""

    def __init__(
        self,
        status: int = 0,
        name: str = "help",
        description: str = "Prints a help message for the given command",
        hidden_aliases: set[str] = {"?"},
        **kwargs: Any,
    ):
        """Initializes the help command.

        # Parameters

        * `status` - The status the program exits with when the help command is invoked.

        All other arguments are passed to {py:class}`powercli.command.Command` with some defaults.
        """
        super().__init__(
            name=name,
            description=description,
            hidden_aliases=hidden_aliases,
            add_common_flags=False,
            add_common_subcommands=False,
            **kwargs,
        )

        self.pos(
            identifier="command",
            name="COMMAND",
            description="The name of the subcommand",
            into=self._subcommand_of_parent,
            default=static(None),
        )

        self.status = status

    def _subcommand_of_parent(self, name: str) -> Command[FV, PV]:
        """Returns the subcommand named `name` of the parent command."""
        assert self.parent is not None, "help command must be subcommand"
        for cmd in self.parent._subcommands.values():
            if cmd.name == name:
                return cmd
        raise RuntimeError(f"no command name {name!r}")

    def parse_args(self, args: list[str] | None = None) -> NoReturn:
        """Parses arguments like {py:meth}`powercli.command.Command.parse_args`.

        This function will print a help message and exit.
        """
        pargs = super().parse_args(args)
        target: Command[Any, Any] | None
        if pargs.is_present("command"):
            target = cast(
                Command[Any, Any] | None, pargs.value_of_positional("command")
            )
        target = target or self.parent
        assert target is not None
        _print_and_exit(help_message(target), status=self.status, file=self.file)


def _print_and_exit(*args: Any, status: int = 0, **kwargs: Any) -> NoReturn:
    """Prints text and exits with `status`."""
    print(*args, **kwargs)
    sys.exit(status)


class HelpFlag(Flag[Any, Any, None]):
    """A help flag which on presence prints a help message and exits."""

    def __init__(
        self,
        status: int = 0,
        short: str | None = "h",
        long: str | None = "help",
        short_hidden_aliases: set[str] = {"?"},
        description: str | None = "Prints a help message and exits",
        **kwargs: Any,
    ) -> None:
        """Initializes the help flag.

        # Parameters

        * `status` - The status the program exits with when the help command is invoked.

        All other arguments are passed to {py:class}`powercli.args.Flag` with some defaults.
        """
        super().__init__(
            short=short,
            long=long,
            short_hidden_aliases=short_hidden_aliases,
            description=description,
            method=Switch[Any, Any, NoReturn, None](
                on_presence=lambda ctx: _print_and_exit(
                    help_message(ctx.command), status=status, file=ctx.command.file
                ),
                on_absence=static(None),
            ),
            **kwargs,
        )


class VersionCommand(Command[Any, Any]):
    """A version command."""

    def __init__(
        self,
        version: str,
        name: str = "version",
        description: str | None = "Prints the version and exits",
        **kwargs: Any,
    ) -> None:
        """Initializes the version command.

        # Parameters

        * `version` - The version to display.

        All other arguments are passed to {py:class}`powercli.command.Command` with some defaults.
        """
        super().__init__(name=name, description=description, **kwargs)
        self.version = version

    def parse_args(self, args: list[str] | None = None) -> NoReturn:
        """Parses arguments like {py:meth}`powercli.command.Command.parse_args`.

        This function will print the version and exit.
        """
        _pargs = super().parse_args(args)
        _print_and_exit(self.version, file=self.file)


class VersionFlag(Flag[Any, Any, None]):
    """A version flag which on presence prints the version and exits.."""

    def __init__(
        self,
        version: str,
        long: str | None = "version",
        description: str | None = "Prints the version and exits",
        **kwargs: Any,
    ) -> None:
        """Initializes the version flag.

        # Parameters

        * `version` - The version to display.

        All other arguments are passed to {py:class}`powercli.args.Flag` with some defaults.
        """
        super().__init__(
            long=long,
            description=description,
            method=Switch[Any, Any, NoReturn, None](
                on_presence=lambda ctx: _print_and_exit(version, file=ctx.command.file),
                on_absence=static(None),
            ),
            **kwargs,
        )
        self.version = version


def _list_message(cmd: Command[Any, Any]) -> str:
    """Creates a string representation that lists every subcommand of `cmd`."""
    lines = []
    for subcommand in cmd._subcommands.values():
        names: list[str] = []
        names.append(subcommand.name)
        names.extend(subcommand.aliases)
        names.extend(subcommand.hidden_aliases)
        lines.append(", ".join(names))
    return "\n".join(lines)


class ListCommand(Command[Any, Any]):
    """A list command."""

    def __init__(
        self,
        name: str = "list",
        description: str | None = "Lists all subcommands",
        **kwargs: Any,
    ) -> None:
        """Initializes the list command."""
        super().__init__(name=name, description=description, **kwargs)

    def parse_args(self, args: list[str] | None = None) -> NoReturn:
        """Parses arguments like {py:meth}`powercli.command.Command.parse_args`.

        This function will print a list of subcommands and exit.
        """
        _pargs = super().parse_args(args)
        assert self.parent is not None
        _print_and_exit(_list_message(self.parent), file=self.file)


class ListFlag(Flag[Any, Any, None]):
    """A list flag which on presence prints all available subcommands."""

    def __init__(
        self,
        short: str | None = "l",
        long: str | None = "list",
        description: str | None = "Lists all subcommands and exits",
        **kwargs: Any,
    ) -> None:
        """Initializes the list flag."""
        super().__init__(
            short=short,
            long=long,
            description=description,
            method=Switch[Any, Any, NoReturn, None](
                on_presence=lambda ctx: _print_and_exit(
                    _list_message(ctx.command), file=ctx.command.file
                ),
                on_absence=static(None),
            ),
            **kwargs,
        )
