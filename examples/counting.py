import sys

from loguru import logger
from rich import print

from powercli import Command, methods

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

cmd: Command[int, None] = Command(add_common_flags=False)
cmd.flag(identifier="f", short="f", method=methods.Count())

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
