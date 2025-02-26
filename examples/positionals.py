import sys
from typing import Any

from loguru import logger
from rich import print

from powercli import Command

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

cmd: Command[Any, Any] = Command(add_common_subcommands=False, add_common_flags=True)
cmd.pos(identifier="foo", name="FOO", description="Hello World")
cmd.pos(identifier="bar", name="BAR", description="Bye World", into=int)
cmd.pos(identifier="baz", name="BAZ")

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
