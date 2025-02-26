"""The heart of PowerCLI - the command class."""

from __future__ import annotations

__all__ = ["Command"]
import sys
import typing
from collections import deque
from collections.abc import Generator, Iterable
from itertools import chain
from typing import Any

from attrs import Factory, define, field
from loguru import logger

from . import exceptions, methods, parser
from .args import Argument, Flag, Positional
from .category import Category
from .dependency import Resolver
from .typedefs import Converter, Identifier
from .utils import ArgIterator, _did_you_mean, _single_name_of_arg

logger.disable(__name__)


@define(kw_only=True)
class Command[FV, PV]:
    """A command which might contains arguments and subcommands.

    # Parameters

    * `name` - Sets the name of the command.

      Defaults to the first argument provided in the command-line
      (`sys.argv[0]`).

    * `aliases` - A set of aliases this command can be invoked with as well.

      ```{note}
      This only applies for subcommands.
      ```

    * `hidden_aliases` - Same as `aliases` but not shown in help messages.

    * `description` - A short description of the command.

    * `long_description` - A concise description of the command.

    * `prefix_short` - The prefix used to specify flags by their short name.

      Most command-line programs use dashes (`-`) for flags. This is the default
      and can be explicitly specified as shown below.

      ```python
      from powercli import Command

      Command(
          # ...
          prefix_short="-",
          prefix_long="--",
      )
      ```

      On Windows, command-line programs commonly use slashes (`/`) for flags.
      Each flag needs to be prefixed separately which means flags with both
      short and long names cannot be registered.

      ```python
      from powercli import Command

      Command(
          # ...
          prefix_long="/",
      )
      ```

    * `prefix_long` - The prefix used to specify flags by their long name.

      ```{seealso}
      {py:attr}`prefix_short`
      ```

    * `category` - An optional category used for grouping commands.

    * `file` - The file used for commands or arguments that display text.

    * `add_common_flags` - Adds `h`, `help`, `list` and `version` flags.

      This only has an effect when a prefix is defined for the command.

    * `add_common_subcommands` - Adds `help`, `list`, `version` subcommands.
    """

    name: str = Factory(lambda: sys.argv[0])
    """The name of the command."""

    aliases: set[str] = Factory(set)
    """A set of aliases this command can be invoked with if it's a subcommand."""

    hidden_aliases: set[str] = Factory(set)
    """A set of hidden aliases this command can be invoked with if it's a subcommand."""

    description: str | None = None
    """A short one-sentence description of this command."""

    long_description: str | None = None
    """A long multi-sentence description of this command."""

    epilog: str | None = None
    """Additional text displayed at the bottom."""

    prefix_short: str | None = "-"
    """The prefix this command uses for short flag names."""

    prefix_long: str | None = "--"
    """The prefix this command uses for long flag names."""

    category: Category | None = None
    """The optional category of this command."""

    file: typing.TextIO = Factory(lambda: sys.stdout)
    """The stream this command writes text to."""

    _add_common_flags: bool = True

    _add_common_subcommands: bool = False

    _args: dict[Identifier, Argument] = field(init=False, factory=dict)

    _subcommands: dict[str, Command[FV, PV]] = field(init=False, factory=dict)

    _parent: Command[FV, PV] | None = field(init=False, default=None)

    def __attrs_post_init__(self) -> None:
        if (
            self.prefix_short is not None
            and self.prefix_long is not None
            and self.prefix_short.startswith(self.prefix_long)
        ):
            raise ValueError("short prefix must not start with value of long prefix")
        if self.prefix_short == "" or self.prefix_long == "":
            raise ValueError("prefix must not be an empty string")

        self._add_common_helpers()

    def __str__(self) -> str:
        """Returns a string representation of the command."""
        return self.name

    def __repr__(self) -> str:
        return f"<Command{(' ' + self.name) if self.name else ''}>"

    def _add_common_helpers(self) -> None:
        """Adds common subcommands and flags (help and list) if possible."""
        from . import common

        if self.has_prefix() and self._add_common_flags:
            self.add_arg(common.HelpFlag())
            self.add_arg(common.ListFlag())
        if self._add_common_subcommands:
            self.add_subcommand(common.HelpCommand())
            self.add_subcommand(common.ListCommand())

    @property
    def parent(self) -> Command[FV, PV] | None:
        """Returns the parent command."""
        return self._parent

    @parent.setter
    def parent(self, cmd: Command[FV, PV]) -> None:
        if self.parent is not None:
            raise RuntimeError(f"command {self} already has a parent ({self.parent})")
        self._parent = cmd

    def parents(self) -> Generator[Command[FV, PV], None, None]:
        """Yields each parent command."""
        cmd = self
        while cmd.parent is not None:
            cmd = cmd.parent
            yield cmd

    def names(self) -> Generator[str, None, None]:
        """Yields all names this command can be invoked with."""
        yield self.name
        yield from self.aliases
        yield from self.hidden_aliases

    def _flag_by_name(self, name: str) -> Flag[FV, PV, FV] | None:
        for arg in self._args.values():
            if isinstance(arg, Flag) and name in arg.names():
                return arg
        return None

    def _arg_by_identifier(self, identifier: Identifier) -> Argument:
        for ident in self._args:
            if ident == identifier:
                return self._args[ident]
        raise KeyError(f"no such argument {identifier!r}")

    def _get_subcommand(self, name: str) -> Command[FV, PV] | None:
        for command in self._subcommands.values():
            if name in command.names():
                return command
        return None

    def has_prefix(self) -> bool:
        """
        Returns `True` when either a short or long prefix is specified for this
        command.
        """
        return self.has_prefix_short() or self.has_prefix_long()

    def has_prefix_short(self) -> bool:
        """Returns `True` when a short prefix is specified for this command."""
        return self.prefix_short is not None

    def has_prefix_long(self) -> bool:
        """Returns `True` when a long prefix is specified for this command."""
        return self.prefix_long is not None

    @property
    def _flags(self) -> list[Flag[FV, PV, FV]]:
        return [arg for arg in self._args.values() if isinstance(arg, Flag)]

    @property
    def _positionals(self) -> list[Positional[FV, PV, PV]]:
        return [arg for arg in self._args.values() if isinstance(arg, Positional)]

    def has_positional(self) -> bool:
        """Returns `True` when a positional is registered."""
        for arg in self._args.values():
            if isinstance(arg, Positional):
                return True
        return False

    def has_flag(self) -> bool:
        """Returns `True` when a flag is registered."""
        for arg in self._args.values():
            if isinstance(arg, Flag):
                return True
        return False

    def has_subcommand(self) -> bool:
        """Returns `True` when a subcommand is registered."""
        return bool(self._subcommands)

    def add_arg(self, arg: Argument, /) -> Command[FV, PV]:
        """Registers an argument to the command."""
        if isinstance(arg, Flag):
            if not self.has_prefix() and arg.has_short_name():
                raise ValueError(
                    "either short or long prefix must be set to add flags with "
                    "short name only"
                )
            elif (
                not self.has_prefix_long()
                and not arg.has_short_name()
                and arg.has_long_name()
            ):
                raise ValueError("long prefix is required for flag with long name only")
        if self.has_subcommand() and isinstance(arg, Positional):
            raise ValueError("subcommands and positionals cannot co-exist")
        if (old := self._args.get(arg.identifier)) is not None:
            raise ValueError(f"argument {old} with same id is already registered")
        self._args[arg.identifier] = arg
        return self

    def add_args(self, args: Iterable[Argument], /) -> Command[FV, PV]:
        """Registers multiple arguments to the command."""
        for arg in args:
            self.add_arg(arg)
        return self

    def add_subcommand(self, cmd: Command[FV, PV], /) -> Command[FV, PV]:
        """Registers a subcommand to the command."""
        if (old := self._subcommands.get(cmd.name)) is not None:
            raise ValueError(f"subcommand {old} with same name is already registered")
        if self.has_positional():
            raise ValueError("subcommands and positionals cannot co-exist")
        cmd.parent = self
        self._subcommands[cmd.name] = cmd
        return self

    def flag(self, *args: Any, **kwargs: Any) -> Command[FV, PV]:
        """Creates and registers a flag to the command."""
        arg: Flag[FV, PV, Any] = Flag(*args, **kwargs)
        self.add_arg(arg)
        return self

    def pos(self, *args: Any, **kwargs: Any) -> Command[FV, PV]:
        """Creates and registers a positional to the command."""
        arg: Positional[FV, PV, Any] = Positional(*args, **kwargs)
        self.add_arg(arg)
        return self

    def parse_args(self, args: list[str] | None = None) -> parser.ParsedCommand[FV, PV]:
        """Parses arguments from `args`, or, if `None` from `argv`."""
        if args is None:
            args = sys.argv[1:]

        parsed_flags: list[parser.ParsedFlag[FV]] = []
        parsed_positionals: list[parser.ParsedPositional[PV]] = []
        parsed_commands: list[parser.ParsedCommand[FV, PV]] = []
        parsed_command = parser.ParsedCommand(
            command=self,
            raw_args=args,
            parsed_flags=parsed_flags,
            parsed_positionals=parsed_positionals,
            parsed_commands=parsed_commands,
        )

        switches: dict[Identifier, bool] = {}

        # initially fill methods with certain methods
        for f in self._flags:
            if isinstance(f.method, methods.Count):
                parsed_flag: parser.ParsedFlag[FV]
                parsed_flag = parser.ParsedFlag(arg=f, raw_values=None, values=[0])
                parsed_flags.append(parsed_flag)
                continue
            if isinstance(f.method, methods.Repeat):
                parsed_flag = parser.ParsedFlag(arg=f, raw_values=[], values=[])
                parsed_flags.append(parsed_flag)
            if isinstance(f.method, methods.Switch):
                switches[f.identifier] = False

        position = 0

        parts = ArgIterator(deque(args))
        for part in parts:
            logger.debug(f"processing {part!r}")
            if self.has_prefix() and (self._is_long(part) or self._is_short(part)):
                names: list[str]
                if self._is_long(part):
                    logger.debug("detected long prefix")
                    assert self.prefix_long is not None
                    names = [part.removeprefix(self.prefix_long)]
                elif self._is_short(part):
                    logger.debug("detected short prefix")
                    assert self.prefix_short is not None
                    names = [*part.removeprefix(self.prefix_short)]
                else:
                    assert False, "unreachable"

                for name in names:
                    flag = self._flag_by_name(name)
                    if flag is None:
                        similar = _did_you_mean(
                            name,
                            chain.from_iterable(f.names() for f in self._flags),
                        )
                        raise RuntimeError(
                            f"there is no such flag {name!r}"
                            + ("" if similar is None else f"; {similar}")
                        )
                    match flag.method:
                        case methods.Normal():
                            raw, parsed = self._obtain_values(parts, flag)
                            self._ensure_unique_presence_of_flag(flag, parsed_flags)
                            parsed_flag = parser.ParsedFlag(
                                arg=flag, raw_values=raw, values=parsed
                            )
                            parsed_flags.append(parsed_flag)
                        case methods.Count(_, _):
                            pf = self._parsed_flag(flag, parsed_flags)
                            assert pf is not None
                            vals = typing.cast(list[Any], pf.values)
                            vals[0] += 1
                        case methods.Repeat(_):
                            raw, parsed = self._obtain_values(parts, flag)
                            pf = self._parsed_flag(flag, parsed_flags)
                            assert pf is not None
                            vals = typing.cast(list[Any], pf.values)
                            vals.append(parsed)
                            rawvals = typing.cast(list[Any], pf.raw_values)
                            rawvals.append(raw)
                        case methods.Switch(_, _):
                            # The switch is the only method where the actual value is determined dynamically thus we need to put it into
                            # a list and handle it later on when all dependencies are covered.
                            switches[flag.identifier] = True
                        case _:
                            raise NotImplementedError(f"unknown method {flag.method!r}")
            else:
                logger.debug("detected positional or subcommand")
                positional = self._positional_at(position)
                if positional is None:
                    subcommand = self._get_subcommand(part)
                    if subcommand is None:
                        similar = _did_you_mean(
                            part,
                            chain.from_iterable(
                                subcommand.names()
                                for subcommand in self._subcommands.values()
                            ),
                        )
                        raise RuntimeError(
                            f"no subcommand named {part!r}"
                            + ("" if similar is None else f"; {similar}")
                        )
                    logger.debug("detected subcommand")
                    parsed_commands.append(subcommand.parse_args(list(parts)))
                    break
                logger.debug("detected positional")
                value = self._obtain_value(part, positional)
                if value is not None:
                    parsed_positionals.append(
                        parser.ParsedPositional(
                            arg=positional, raw_value=value[0], value=value[1]
                        )
                    )
                    position += 1

        depres = Resolver()
        for ident, deps in (
            (a.identifier, a.dependencies) for a in self._args.values()
        ):
            depres.dependencies[ident] = deps
        depres.lock()

        parsable_args: list[Argument] = []

        def all_parsed() -> Generator[parser.ParsedArgument, None, None]:
            """Yields all parsed arguments."""
            yield from parsed_flags
            yield from parsed_positionals

        def all_unparsed() -> Generator[Argument, None, None]:
            """Yields all unparsed arguments."""
            for flag in self._flags:
                if self._parsed_flag(flag, parsed_flags) is None:
                    yield flag
            for pos in self._positionals:
                if self._parsed_positional(pos, parsed_positionals) is None:
                    yield pos

        logger.trace(f"{list(all_unparsed()) = }")

        # get all unspecified arguments whose dependencies are covered
        for ident, arg in self._args.items():
            for parsed_arg in all_parsed():
                assert isinstance(parsed_arg, parser.ParsedArgument)
                is_already_parsed = ident == parsed_arg.arg.identifier
                if is_already_parsed:
                    for parsable in depres.cover(parsed_arg.arg.identifier):
                        arg = self._arg_by_identifier(parsable)
                        if parsable not in [a.arg.identifier for a in all_parsed()]:
                            parsable_args.append(self._arg_by_identifier(parsable))

        for unparsed_arg in all_unparsed():
            parsable_args.append(unparsed_arg)

        # evaluate default values of unspecified parsable args
        logger.trace(f"{parsable_args = }")
        while parsable_args:
            arg = parsable_args.pop(0)
            if isinstance(arg, Flag) and arg.default is not None:
                flg_default = arg.default(parsed_command)
                parsed_flags.append(
                    parser.ParsedFlag(arg=arg, raw_values=None, values=flg_default)
                )
                for parsable in depres.cover(arg.identifier):
                    if parsable not in [a.arg.identifier for a in all_parsed()]:
                        parsable_args.append(self._arg_by_identifier(parsable))
            elif isinstance(arg, Positional) and arg.default is not None:
                pos_default = arg.default(parsed_command)
                parsed_positional: parser.ParsedPositional[PV]
                parsed_positional = parser.ParsedPositional(
                    arg=arg, raw_value=None, value=pos_default
                )
                parsed_positionals.append(parsed_positional)
            elif isinstance(arg, Flag) and isinstance(arg.method, methods.Switch):
                present = arg.identifier in (
                    ident
                    for (ident, was_mentioned) in switches.items()
                    if was_mentioned
                )
                switch_value: FV
                if present:
                    switch_value = arg.method.on_presence(parsed_command)
                else:
                    switch_value = arg.method.on_absence(parsed_command)
                parsed_flag = parser.ParsedFlag(
                    arg=arg, raw_values=None, values=[switch_value]
                )
                parsed_flags.append(parsed_flag)

        logger.trace(f"{depres!r}")

        for ident, deps in depres.dependencies.items():
            arg = self._arg_by_identifier(ident)

            provided = arg in (a.arg for a in all_parsed())
            required: bool | str

            if isinstance(arg, Flag):
                required = arg.required(parsed_command)
            elif isinstance(arg, Positional):
                required = arg.required
            else:
                raise NotImplementedError()

            message: str = (
                f"argument {_single_name_of_arg(arg)} is required but not specified"
            )
            req: bool
            if isinstance(required, bool):
                req = required
            if isinstance(required, str):
                message = f"{message}; {required}"
                req = True

            logger.trace(f"{arg}: {provided = } {req = }")

            if provided and deps:
                raise exceptions.MissingDependencyError(arg=arg, dependencies=deps)
            if not provided and req:
                raise RuntimeError(message)

        for parsed_flag in parsed_flags:
            method = parsed_flag.arg.method
            if isinstance(method, methods.Count):
                assert isinstance(parsed_flag.values, list)
                amt = parsed_flag.values[0]
                if amt == 0 and method.default is not None:
                    # override with default if none specified
                    amt = method.default(parsed_command)
                    parsed_flag.values = [amt]
                ok = method.validate_amount(parsed_command, amt)
                message = f"invalid amount for flag {_single_name_of_arg(parsed_flag.arg)}: {amt}"
                if isinstance(ok, str):
                    message = f"{message}; {ok}"
                    ok = False
                if not ok:
                    raise RuntimeError(message)
            if isinstance(method, methods.Repeat):
                assert isinstance(parsed_flag.values, list)
                amt = len(parsed_flag.values)
                ok = method.validate_amount(parsed_command, amt)
                message = f"invalid amount for (repeated) flag {_single_name_of_arg(parsed_flag.arg)}: {amt}"
                if isinstance(ok, str):
                    message = f"{message}; {ok}"
                    ok = False
                if not ok:
                    raise RuntimeError(message)

        for parsed_flag in parsed_flags:
            arg = parsed_flag.arg
            allowed = arg.allowed(parsed_command)
            message = f"argument {arg} is not allowed"
            if isinstance(allowed, str):
                message += f": {allowed}"
            elif allowed:
                continue
            raise RuntimeError(message)

        return parsed_command

    @staticmethod
    def _parsed_flag(
        flag: Flag[FV, PV, FV], parsed_flags: list[parser.ParsedFlag[FV]]
    ) -> parser.ParsedFlag[FV] | None:
        """Returns the parsed flag if `flag` has been parsed."""
        for f in parsed_flags:
            if f.arg.identifier == flag.identifier:
                return f
        return None

    @staticmethod
    def _parsed_positional(
        pos: Positional[FV, PV, PV],
        parsed_positionals: list[parser.ParsedPositional[PV]],
    ) -> parser.ParsedPositional[PV] | None:
        """Returns the parsed positional if `pos` has been parsed."""
        for p in parsed_positionals:
            if p.arg.identifier == pos.identifier:
                return p
        return None

    def _ensure_unique_presence_of_flag(
        self, flag: Flag[FV, PV, FV], parsed_flags: list[parser.ParsedFlag[FV]]
    ) -> None:
        """Raises a {py:class}`RuntimeError` when `flag` has already been parsed."""
        f = self._parsed_flag(flag, parsed_flags)
        if f is not None:
            raise RuntimeError(f"cannot specify {flag} twice")

    @staticmethod
    def _obtain_value(
        arg: str, positional: Positional[FV, PV, PV]
    ) -> tuple[str, PV | str] | None:
        """Obtains a single positional's value by converting it."""
        try:
            parsed_value = positional.into(arg)
        except exceptions.ConversionError:
            raise
        except Exception as e:
            raise exceptions.ConversionError(arg, positional.into) from e
        return (arg, parsed_value)

    @staticmethod
    def _obtain_values(
        args: ArgIterator, flag: Flag[FV, PV, FV]
    ) -> tuple[list[str], list[FV]]:
        """Obtains converted flag values from raw arguments."""
        raw_values: list[str] = []
        parsed_values: list[FV] = []

        previous: tuple[str, Converter[FV]] | None = None
        for index, value in enumerate(flag.values):
            greedy = value is Ellipsis
            if greedy:
                assert previous is not None
                name, into = previous
            else:
                assert value is not Ellipsis
                name, into = value

            while True:
                try:
                    raw = next(args)
                except StopIteration:
                    if greedy:
                        break
                    raise exceptions.MissingValueError(
                        flag, len(parsed_values), name
                    ) from None

                try:
                    parsed = into(raw)
                except exceptions.ConversionError:
                    if greedy:
                        args.prepend(raw)
                        break
                    raise
                except Exception as e:
                    if greedy:
                        args.prepend(raw)
                        break
                    raise exceptions.ConversionError(raw, into) from e

                raw_values.append(raw)
                parsed_values.append(parsed)
                if not greedy:
                    break

            previous = name, into

        return (raw_values, parsed_values)

    def _is_short(self, arg: str, /) -> bool:
        """Returns `True` if `arg` starts with the short prefix registered to this command."""
        return self.prefix_short is not None and arg.startswith(self.prefix_short)

    def _is_long(self, arg: str, /) -> bool:
        """Returns `True` if `arg` starts with the long prefix registered to this command."""
        return self.prefix_long is not None and arg.startswith(self.prefix_long)

    def _positional_at(self, index: int) -> Positional[FV, PV, PV] | None:
        """Returns the positional at a certain index."""
        positionals = [
            pos for pos in self._args.values() if isinstance(pos, Positional)
        ]
        try:
            return positionals[index]
        except IndexError:
            return None
