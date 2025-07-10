import sys
from typing import Any

from loguru import logger
from rich import print

from powercli import Command, common

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

cmd: Command[Any, Any] = Command(add_common_subcommands=False, add_common_flags=True)
cmd.add_subcommand(common.HelpCommand())
cmd.add_subcommand(common.VersionCommand("common example 1.0.0"))
cmd.add_subcommand(common.ListCommand())

foo: Command[Any, Any] = Command(
    name="foo",
    description="Does foo related stuff",
    add_common_subcommands=False,
    add_common_flags=True,
)
bar: Command[Any, Any] = Command(
    name="bar",
    description="Does foobar related stuff",
    add_common_subcommands=False,
    add_common_flags=True,
)
baz: Command[Any, Any] = Command(
    name="baz",
    description="Does foobarbaz related stuff",
    add_common_subcommands=False,
    add_common_flags=True,
)
foo.add_subcommand(bar)
bar.add_subcommand(baz)
cmd.add_subcommand(foo)

if __name__ == "__main__":
    args = cmd.parse_args()
    if not args.raw_args:
        args = cmd.parse_args(["?"])
    print(args)
