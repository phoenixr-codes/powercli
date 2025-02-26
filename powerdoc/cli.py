from copy import deepcopy
from pathlib import Path
from typing import Any

from adorable import color  # type: ignore

from powercli.args import Flag
from powercli.command import Command
from powercli.utils import one_of, static

_PY_BLUE = color.from_hex(0x306998)
_PY_YELLOW = color.from_hex(0xFFD43B)
_BANNER = f"{deepcopy(_PY_YELLOW).on(deepcopy(_PY_BLUE)):>} {_PY_BLUE.fg:Power}{_PY_YELLOW.fg:DOC}"

cmd: Command[Any, Any] = Command(
    name="powerdoc",
    description=f"{_BANNER} - Build documentation from a command",
    add_common_flags=True,
)

cmd.add_args(
    one_of(
        Flag(identifier="build-man", long="man", description="Build man page"),
        Flag(identifier="build-md", long="markdown", description="Build Markdown"),
        required=static(True),
    )
)

cmd.pos(
    identifier="PATH",
    name="PATH",
    description="Specify the path to the Python file which contains the command",
    into=Path,
)

cmd.flag(
    identifier="obj",
    long="obj",
    description="The name of the object which represents the command (default: cmd)",
    values=[("IDENTIFIER", str)],
    default=static(["cmd"]),
)
