import sys
from typing import Any

from loguru import logger
from rich import print

from powercli import Category, Command

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

category_pm = Category("package management")
category_build = Category("build")
category_output = Category("output")

cmd: Command[Any, Any] = Command(
    name="nullc",
    description="The C compiler that does not actually do anything at all",
)
cmd.flag(identifier="color", long="no-color", description="Disables colored output", category=category_output)
cmd.flag(identifier="json", long="json", description="Formats output as JSON", category=category_output)
cmd.flag(identifier="offline", long="offline", description="Prevent downloading packages", category=category_pm)
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
