import sys

from loguru import logger
from rich import print

from powercli import Command

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

cmd: Command[None, None] = Command(add_common_flags=False)
cmd.flag(identifier="f", short="f", dependencies={"g"})
cmd.flag(identifier="g", short="g", dependencies={"h"})
cmd.flag(identifier="h", short="h")

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
