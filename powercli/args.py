"""Argument classes that can be used to create flags and positionals."""

from __future__ import annotations

__all__ = ["Argument", "Flag", "Positional"]

from abc import ABCMeta
from collections.abc import Collection, Generator, Sequence
from types import EllipsisType

from attrs import Factory, define, field

from . import methods
from .category import Category
from .typedefs import Converter, Identifier, WithContext
from .utils import _not_unique, static


@define(kw_only=True)
class Argument(metaclass=ABCMeta):
    """Base class for arguments.

    You should not subclass this class as the parser only knows how to handle
    {py:obj}`powercli.args.Flag`s and {py:obj}`powercli.args.Positional`s.
    Create a subclass of either of those.
    """

    identifier: Identifier = field()
    """A unique identifier which can be used for queries and validation.

    Defaults to the ID of the created instance.
    """

    @identifier.default
    def _(self) -> Identifier:
        return str(id(self))

    dependencies: set[Identifier] = Factory(set)
    """Argument this argument depends on at parse time.

    This must be a set of all argument IDs that are required to evaluated
    the default value and for flags whether it is required. Arguments
    needed to evaluate whether a flag is allowed are **not** dependencies.

    ```{seealso}
    - {py:attr}`powercli.args.Positional.default`
    - {py:attr}`powercli.args.Flag.default`
    - {py:attr}`powercli.args.Flag.required`
    ```
    """


@define(kw_only=True)
class Flag[FV, PV, T](Argument):
    """A flag is usually an optional option that toggles some feature.

    Flags can also accept values, be repeated and much more.
    """

    short: str | None = None
    """A one character long name of the flag."""

    long: str | None = None
    """The long name of the flag.

    This flag can be of any length including 0 and 1.
    """

    short_aliases: set[str] = Factory(set)
    """A set of aliases for the short name."""

    long_aliases: set[str] = Factory(set)
    """A set of aliases for the long name."""

    short_hidden_aliases: set[str] = Factory(set)
    """A set of hidden aliases for the short name."""

    long_hidden_aliases: set[str] = Factory(set)
    """A set of hidden aliases for the long name."""

    description: str | None = None
    """A short one-sentence description of the flag."""

    long_description: str | None = None
    """A long description of the flag."""

    values: Sequence[tuple[str, Converter[T]] | EllipsisType] = Factory(list)
    """Values the flag takes.

    # Examples

    ```python
    from powercli import Flag

    Flag(
        # ...
        values=[("X", float), ..., ("Y", int), ...],
        # parse as much `float`s as possible, then as much `int`s as possible
    )
    ```

    :::{tip}
    Avoid using a flag that accepts a variable amount of string or something similar as it consumes
    potential flags as well. For example:

    ```python
    from powercli import Flag

    Flag(
        # ...
        short="f",
        values=[("X", str), ...],
        # parse as much `float`s as possible
    )
    ```

    If we add this flag to a command and input something like `-f --hey --ho`, then `--hey` and `--ho`
    will be parsed as values of the flag `-f` instead of separate flags `--hey` and `--ho`.

    This may be useful however if you want to consume all arguments without parsing them for example
    when passing them to an external program. Usually such flag has an empty long name and no short name:

    ```python
    from powercli import Flag

    Flag(
        # ...
        short=None,
        long="",
        values=[("ARGS", str), ...],
    )
    ```
    :::
    """

    default: WithContext[FV, PV, Collection[T]] | None = None
    """Default values for the flag.

    # Examples

    ```python
    from  powercli import Flag

    Flag(
        # ...
        values=[("X", float), ("Y", int)],
        default=[1.5, 42],
    )
    ```
    """

    method: methods.Method = Factory(lambda: methods.Normal())
    """The method of the flag that influences the parsing behavior."""

    required: WithContext[FV, PV, bool | str] = static(False)
    """Whether the flag is required."""

    allowed: WithContext[FV, PV, bool | str] = static(True)
    """Whether the flag is allowed."""

    category: Category | None = None
    """The optional category of this flag."""

    def __attrs_post_init__(self) -> None:
        # names
        if self.short is None and self.long is None:
            raise ValueError("either `short` or `long` must be set")
        if self.short is not None and len(self.short) != 1:
            raise ValueError("`short` must consist of exactly one character")
        if self.short is None and (self.short_aliases | self.short_hidden_aliases):
            raise ValueError("consider setting `short` before using aliases")
        if self.long is None and (self.long_aliases | self.long_hidden_aliases):
            raise ValueError("consider setting `long` before using aliases")
        if names := _not_unique(
            self.short_aliases,
            self.short_hidden_aliases,
            (set() if self.short is None else {self.short}),
            self.long_aliases,
            self.long_hidden_aliases,
            (set() if self.long is None else {self.long}),
        ):
            raise ValueError(f"name(s) {names} present twice or more")

        # values and default
        self.method._validate_flag(self)

        for idx, val in enumerate(self.values):
            if val is not Ellipsis:
                continue
            if idx == 0:
                raise ValueError("first item of `values` must not be `...`")
            elif self.values[idx - 1] is Ellipsis:
                raise ValueError(
                    f"`...` cannot follow `...` (index {idx - 1} and {idx})"
                )

    def __str__(self) -> str:
        return " / ".join(self.names())

    def __repr__(self) -> str:
        return f"<Flag #{self.identifier} ({', '.join(map(repr, self.names()))})>"

    def names(self) -> Generator[str, None, None]:
        """Yields all names this flag can be specified with."""
        if self.short is not None:
            yield self.short
        if self.long is not None:
            yield self.long
        yield from self.short_aliases
        yield from self.short_hidden_aliases
        yield from self.long_aliases
        yield from self.long_hidden_aliases

    def visible_short_names(self) -> Generator[str, None, None]:
        """Yields all non-hidden short names this flag can be specified with."""
        if self.short is not None:
            yield self.short
        yield from self.short_aliases

    def visible_long_names(self) -> Generator[str, None, None]:
        """Yields all non-hidden long names this flag can be specified with."""
        if self.long is not None:
            yield self.long
        yield from self.long_aliases

    def has_short_name(self) -> bool:
        """Returns `True` if this flag has a short name."""
        return self.short is not None

    def has_long_name(self) -> bool:
        """Returns `True` if this flag has a long name."""
        return self.long is not None


@define(kw_only=True)
class Positional[FV, PV, T](Argument):
    """A positional is usually a required value of a command.

    Positionals cannot be mixed with subcommands.
    """

    name: str
    """The name of the positional."""

    description: str | None = None
    """A short one-sentence description of the positional."""

    long_description: str | None = None
    """A long description of the positional."""

    into: Converter[T] | Converter[str] = str
    """A function that converts the input."""

    default: WithContext[FV, PV, T] | None = None
    """A default value for this positional."""

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Positional #{self.identifier} ({self.name!r})>"

    @property
    def required(self) -> bool:
        """Whether the positional is required."""
        return self.default is None
