import sys
from typing import Any

from adorable.common import YELLOW, AQUA, GREEN
from loguru import logger
from rich import print

from powercli import Category, Command
from powercli.command import Example

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

category_pm = Category("package management", color=AQUA)
category_build = Category("build", color=GREEN)
category_output = Category("output", color=YELLOW)

cmd: Command[Any, Any] = Command(
    name="nullc",
    description="The C compiler that does not actually do anything at all",
    examples=[
        Example(["run", "main.c"], "Compile and run a C program"),
        Example(["compile", "main.c", "-o", "main"], "Compile a C program"),
    ],
)
cmd.flag(
    identifier="color",
    long="no-color",
    description="Disables colored output",
    category=category_output,
)
cmd.flag(
    identifier="json",
    long="json",
    description="Formats output as JSON",
    category=category_output,
)
cmd.flag(
    identifier="offline",
    long="offline",
    description="Prevent downloading packages",
    category=category_pm,
)
cmd.add_subcommand(
    Command(
        name="build",
        description="Build the project",
        category=category_build,
    )
)
cmd.add_subcommand(
    Command(
        name="dep",
        description="Manage dependencies",
        category=category_pm,
    )
)

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
