from collections.abc import Generator
from datetime import date
from typing import Any

from attrs import define

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


@define
class ManBuilder(Builder):
    command: Command[Any, Any]

    def build(self) -> None:
        lines = []
        lines.extend(
            [
                *self.make_title_line(),
                *self.make_name(),
                *self.make_synopsis(),
                *self.make_description(),
            ]
        )
        print("\n".join(lines))

    def make_title_line(self) -> Generator[str, None, None]:
        yield f'.TH "{escape(self.command.name.upper())}" "1" "{date.today():%b %Y}" "{escape(self.command.name)}"'

    def make_name(self) -> Generator[str, None, None]:
        yield ".SH NAME"
        yield escape(self.command.name)

    def make_synopsis(self) -> Generator[str, None, None]:
        yield ".SH SYNOPSIS"
        yield f".B {escape(self.command.name)}"
        for flag in self.command._flags:
            yield "["
            names = []
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
