# TODO: also generate Command.examples

from collections.abc import Generator
from datetime import date
from typing import Any

from attrs import define, field

from powercli._help_utils import _add_description
from powercli.args import Flag
from powercli.command import Command

from .builder import Builder


def escape(text: str) -> str:
    """Escapes text that would be treated specially in Roff."""
    for char in ["\\", '"', "-", "^", "#", "%", "{", "}", "[", "]"]:
        text = text.replace(char, f"\\{char}")
    lines: list[str] = []
    for line in text.splitlines(keepends=True):
        for char in [".", "'"]:
            if line.startswith(char):
                line = f"\\&{char}{line.removeprefix(char)}"
                continue
        lines.append(line)
    text = "".join(lines)
    return text


def _prefix_flag(
    command: Command[Any, Any],
    flag: Flag[Any, Any, Any],
    *,
    visible_aliases: bool = True,
    hidden_aliases: bool = False,
) -> Generator[str, None, None]:
    """Generates each name of a flag with the matching prefix."""
    if flag.short is not None and command.prefix_short is not None:
        yield command.prefix_short + flag.short
    if flag.long is not None and command.prefix_long is not None:
        yield command.prefix_long + flag.long
    if visible_aliases:
        for alias in flag.short_aliases:
            if command.prefix_short is not None:
                yield command.prefix_short + alias
        for alias in flag.long_aliases:
            if command.prefix_long is not None:
                yield command.prefix_long + alias
    if hidden_aliases:
        for alias in flag.short_hidden_aliases:
            if command.prefix_short is not None:
                yield command.prefix_short + alias
        for alias in flag.long_hidden_aliases:
            if command.prefix_long is not None:
                yield command.prefix_long + alias


@define
class ManBuilder(Builder):
    command: Command[Any, Any]
    section: int = field(kw_only=True)

    def build(self) -> None:
        lines = []
        lines.extend(
            [
                *self.make_title_line(),
                *self.make_name(),
                *self.make_synopsis(),
                *self.make_description(),
                *self.make_options(),
            ]
        )
        print("\n".join(lines))

    def make_title_line(self) -> Generator[str, None, None]:
        yield f'.TH "{escape(self.command.name.upper())}" "{self.section}" "{date.today():%b %Y}" "{escape(self.command.name)}"'

    def make_name(self) -> Generator[str, None, None]:
        yield ".SH NAME"
        yield escape(self.command.name)

    def make_synopsis(self) -> Generator[str, None, None]:
        yield ".SH SYNOPSIS"
        yield f".B {escape(self.command.name)}"
        for flag in self.command._flags:
            yield "["
            names = []
            # TODO: use _prefix_flag()
            if self.command.prefix_short is not None:
                if (short_name := flag.short) is not None:
                    names.append(self.command.prefix_short + short_name)
                for short_name in flag.short_aliases:
                    names.append(self.command.prefix_short + short_name)
            if self.command.prefix_long is not None:
                if (long_name := flag.long) is not None:
                    names.append(self.command.prefix_long + long_name)
                for long_name in flag.long_aliases:
                    names.append(self.command.prefix_long + long_name)
            yield "\n|\n".join(map(lambda x: f".B {escape(x)}", names))
            yield "]"

    def make_description(self) -> Generator[str, None, None]:
        if (desc := self.command.description) is not None:
            yield ".SH DESCRIPTION"
            yield escape(desc)

    def make_options(self) -> Generator[str, None, None]:
        # TODO: escape
        indent = 7
        if self.command.has_flag():
            yield ".SH OPTIONS"
            for flag in self.command._flags:
                flag_names = ", ".join(_prefix_flag(self.command, flag))
                text = _add_description(
                    flag_names,
                    indent=0,
                    description_indentation=indent,
                    description=flag.description,
                    long_description=flag.long_description,
                )
                yield text
                yield ""
