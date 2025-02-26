import sys

from loguru import logger
from rich import print

from powercli import Command
from powercli.utils import static

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

cmd: Command[int, None] = Command(add_common_flags=False)
cmd.flag(identifier="f", short="f", values=[("INT", int)], default=static([10]))
cmd.flag(identifier="g", short="g", values=[("INT", int)], default=static([20]))

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
