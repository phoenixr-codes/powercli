import sys
from typing import Any

from adorable.common import AQUA, GREEN, PURPLE, YELLOW
from loguru import logger
from rich import print

from powercli import Category, Command, Flag
from powercli.command import Example
from powercli.static import Static
from powercli.utils import one_of

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

category_pm = Category("package management", color=AQUA)
category_build = Category("build", color=GREEN)
category_output = Category("output", color=YELLOW)
category_lint = Category("lint", color=PURPLE)

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
cmd.add_args(
    one_of(
        Flag(
            identifier="json",
            long="json",
            description="Formats output as JSON",
            category=category_output,
        ),
        Flag(
            identifier="yaml",
            long="yaml",
            description="Formats output as YAML",
            deprecation=Static(True),
            category=category_output,
        ),
    )
)
cmd.flag(
    identifier="offline",
    long="offline",
    description="Prevent downloading packages",
    category=category_pm,
)
cmd.flag(
    identifier="warn-abi",
    long="warn-abi",
    description="Warn about things that will change when compiling with an ABI-compliant compiler",
    category=category_lint,
)
cmd.flag(
    identifier="warn-adress",
    long="warn-address",
    description="Warn about suspicious uses of memory addresses",
    category=category_lint,
)
cmd.flag(
    identifier="warn-attribute",
    long="warn-attribute",
    description="Warn about inappropriate attribute usage",
    category=category_lint,
)
cmd.flag(
    identifier="warn-comment",
    long="warn-comment",
    description="Warn about possibly nested block comments, and C++ comments spanning more than one physical line",
    category=category_lint,
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
