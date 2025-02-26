import sys
from typing import Any

from loguru import logger
from rich import print

from powercli import Category, Command

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

category_run = Category("run", color=0xED87C6)
category_pm = Category("package management", color=0x4294ED)
category_build = Category("build", color=0xD1AC1B)
category_proj = Category("project management", color=0x18DDD7)

cmd: Command[Any, Any] = Command(
    name="bun",
    description="Bun is a fast JavaScript runtime, package manager, bundler, and test runner.",
    epilog="Learn more about Bun:          https://bun.sh/docs\nJoin our Discord community:    https://bun.sh/discord",
)

cmd.add_subcommand(
    Command(
        name="run",
        description="Execute a file or a package.json script with Bun",
        category=category_run,
    )
)
cmd.add_subcommand(
    Command(
        name="test",
        description="Run unit tests with Bun",
        category=category_run,
    )
)
cmd.add_subcommand(
    Command(
        name="x",
        description="Execute a package binary (CLI), installing if needed",
        category=category_run,
    )
)
cmd.add_subcommand(
    Command(
        name="repl",
        description="Start a REPL session with Bun",
        category=category_run,
    )
)
cmd.add_subcommand(
    Command(
        name="exec",
        description="Run a shell script directly with Bun",
        category=category_run,
    )
)

cmd.add_subcommand(
    Command(
        name="install",
        aliases={"i"},
        description="Install dependencies for a package.json",
        category=category_pm,
    )
)
cmd.add_subcommand(
    Command(
        name="add",
        aliases={"a"},
        description="Add a dependency to package.json",
        category=category_pm,
    )
)
cmd.add_subcommand(
    Command(
        name="remove",
        aliases={"rm"},
        description="Remove a dependency from package.json",
        category=category_pm,
    )
)
cmd.add_subcommand(
    Command(
        name="update",
        description="Update outdated dependencies",
        category=category_pm,
    )
)
cmd.add_subcommand(
    Command(
        name="outdated",
        description="Display latest versions of outdated dependencies",
        category=category_pm,
    )
)
cmd.add_subcommand(
    Command(
        name="link",
        description="Register or link a local npm package",
        category=category_pm,
    )
)
cmd.add_subcommand(
    Command(
        name="unlink",
        description="Unregister a local npm package",
        category=category_pm,
    )
)
cmd.add_subcommand(
    Command(
        name="publish",
        description="Publish a package to the npm registry",
        category=category_pm,
    )
)
cmd.add_subcommand(
    Command(
        name="patch",
        description="Prepare a package for patching",
        category=category_pm,
    )
)
cmd.add_subcommand(
    Command(
        name="pm",
        description="Additional package management utilities",
        category=category_pm,
    )
)

cmd.add_subcommand(
    Command(
        name="build",
        description="Bundle TypeScript & JavaScript into a single file",
        category=category_build,
    )
)

cmd.add_subcommand(
    Command(
        name="init",
        description="Start an empty Bun project from a blank template",
        category=category_proj,
    )
)
cmd.add_subcommand(
    Command(
        name="create",
        aliases={"c"},
        description="Create a new project from a template",
        category=category_proj,
    )
)
cmd.add_subcommand(
    Command(
        name="upgrade",
        description="Upgrade to latest version of Bun",
        category=category_proj,
    )
)

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
