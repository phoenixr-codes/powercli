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

if __name__ == "__main__":
    args = cmd.parse_args()
    if not args.raw_args:
        args = cmd.parse_args(["?"])
    print(args)
