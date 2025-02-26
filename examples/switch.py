import sys

from loguru import logger
from rich import print

from powercli import Command
from powercli.methods import Switch
from powercli.utils import static

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

cmd: Command[str, None] = Command()
cmd.flag(
    identifier="f",
    short="f",
    method=Switch(on_presence=static("A"), on_absence=static("B")),
)

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args.value_of("f"))
