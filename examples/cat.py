import sys
from itertools import chain
from pathlib import Path
from typing import Any, cast

from rich.console import Console
from rich.syntax import Syntax

from powercli import Command
from powercli.methods import Repeat, Switch
from powercli.static import Static

cmd: Command[Any, Any] = Command(name="cat")
cmd.pos(identifier="file", name="FILE", into=Path, default=Static(None))
cmd.flag(
    identifier="theme",
    long="theme",
    description="Color theme, aka Pygments style (default: github-dark)",
    values=[("THEME", str)],
    default=Static(["github-dark"]),
)
cmd.flag(
    identifier="line-numbers",
    long="line-numbers",
    description="Enable line numbers",
    method=Switch.boolean(),
)
cmd.flag(
    identifier="highlight",
    short="m",
    description="Highlight the line at an index (repeatable)",
    method=Repeat(),
    values=[("INDEX", int)],
)
cmd.flag(
    identifier="padding",
    short="p",
    long="padding",
    description="Apply padding",
    values=[("PADDING", int)],
    default=Static(0),
)

if __name__ == "__main__":
    console = Console()
    args = cmd.parse_args()

    [theme] = cast(list[str], args.value_of("theme"))
    [line_numbers] = cast(list[bool], args.value_of("line-numbers"))
    highlight = set(
        chain.from_iterable(cast(list[list[int]], args.value_of("highlight")))
    )
    [padding] = cast(list[int], args.value_of("padding"))

    filepath = cast(Path | None, args.value_of("file"))
    if filepath is None:
        text = Syntax(
            sys.stdin.read(),
            lexer="text",
            theme=theme,
            line_numbers=line_numbers,
            highlight_lines=highlight,
            padding=padding,
        )
    else:
        text = Syntax.from_path(
            str(filepath),
            theme=theme,
            line_numbers=line_numbers,
            highlight_lines=highlight,
            padding=padding,
        )
    console.print(text)
