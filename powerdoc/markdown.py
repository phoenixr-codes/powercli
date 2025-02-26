import textwrap
from collections.abc import Generator
from typing import Any

from attrs import define

from powercli.command import Command

from .builder import Builder


def escape(text: str) -> str:
    """Escapes text that would be treated specially in Markdown."""
    for ch in [
        "\\",
        "`",
        "*",
        "_",
        "{",
        "}",
        "[",
        "]",
        "(",
        ")",
        "#",
        "+",
        "-",
        "!",
        ">",
    ]:
        text = text.replace(ch, f"\\{ch}")
    return text


@define
class MarkdownBuilder(Builder):
    command: Command[Any, Any]
    width: int = 80

    def build(self) -> None:
        lines = []
        lines.extend(
            [
                *self.make_title_line(),
                *self.make_description(),
                *self.make_usage(),
            ]
        )
        print("\n".join(lines))

    def make_title_line(self) -> Generator[str, None, None]:
        yield f"# {escape(self.command.name)}"
        yield ""

    def make_description(self) -> Generator[str, None, None]:
        if (desc := self.command.description) is not None:
            yield escape(desc)
            yield ""
        if (long_desc := self.command.long_description) is not None:
            yield escape(long_desc)
            yield ""

    def make_usage(self) -> Generator[str, None, None]:
        if self.command.has_subcommand():
            yield "## Subcommands"
            yield ""
            for subcommand in self.command._subcommands.values():
                line = f"- {escape(subcommand.name)}"
                if (desc := subcommand.description) is not None:
                    line = f"{line} --- {escape(desc)}"
                yield line
        if self.command.has_flag():
            yield "## Flags"
            yield ""
            short_prefix = self.command.prefix_short or self.command.prefix_long
            long_prefix = self.command.prefix_long
            for flag in self.command._flags:
                names = []
                if short_prefix is not None:
                    if (name := flag.short) is not None:
                        names.append(f"{escape(short_prefix)}{escape(name)}")
                    names.extend(
                        map(
                            lambda name: f"{escape(short_prefix)}{escape(name)}",
                            flag.short_aliases,
                        )
                    )
                if long_prefix is not None:
                    if (name := flag.long) is not None:
                        names.append(f"{escape(long_prefix)}{escape(name)}")
                    names.extend(
                        map(
                            lambda name: f"{escape(long_prefix)}{escape(name)}",
                            flag.long_aliases,
                        )
                    )

                line = "- "
                line += " / ".join(f"`{escape(name)}`" for name in names)
                if (desc := flag.description) is not None:
                    line += f" --- {escape(desc)}"
                yield line
                if (long_desc := flag.description) is not None:
                    yield from textwrap.wrap(
                        escape(long_desc),
                        width=self.width,
                        initial_indent="  ",
                        subsequent_indent="  ",
                    )
