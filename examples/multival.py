import sys
from typing import Never

from loguru import logger
from rich import print

from powercli import Command

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

cmd: Command[int | float, Never] = Command(add_common_flags=False)
cmd.flag(identifier="f", short="f", values=[("INT", int), ...])
cmd.flag(identifier="g", short="g", values=[("INT", int), ..., ("FLOAT", float), ...])

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
