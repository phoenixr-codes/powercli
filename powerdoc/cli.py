from pathlib import Path
from typing import Any

from adorable import color

from powercli.args import Flag
from powercli.command import Command
from powercli.static import Static
from powercli.utils import one_of

_PY_BLUE = color.from_rgb(0x306998)
_PY_YELLOW = color.from_rgb(0xFFD43B)
_BANNER = f"{_PY_YELLOW.on(_PY_BLUE):>} {_PY_BLUE:Power}{_PY_YELLOW:DOC}"

cmd: Command[Any, Any] = Command(
    name="powerdoc",
    description=f"{_BANNER} - Build documentation from a command",
    add_common_flags=True,
)

cmd.add_args(
    one_of(
        Flag(identifier="build-man", long="man", description="Build man page"),
        Flag(identifier="build-md", long="markdown", description="Build Markdown"),
        required=Static(True),
    )
)

cmd.pos(
    identifier="PATH",
    name="PATH",
    description="Specify the path to the Python file which contains the command",
    into=Path,
)

cmd.flag(
    identifier="section",
    short="s",
    long="section",
    description="Specify the section of the man page",
    values=[("SECTION", str)],
    default=Static(["1"]),
)

cmd.flag(
    identifier="obj",
    long="obj",
    description="The name of the object which represents the command",
    values=[("IDENTIFIER", str)],
    default=Static(["cmd"]),
)
