import sys
from typing import Any

from loguru import logger
from rich import print

from powercli import Command

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

cmd: Command[Any, Any] = Command(add_common_flags=True, add_common_subcommands=True)
cmd.flag(identifier="last", long="", values=[("ARGS", str), ...])

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
