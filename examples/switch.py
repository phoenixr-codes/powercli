import sys

from loguru import logger
from rich import print

from powercli import Command
from powercli.typedefs import Context
from powercli.methods import Switch
from powercli.utils import static

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

def disable_color(_: Context[str, None]) -> None:
    print("Disabling color...")

cmd: Command[str, None] = Command()
cmd.flag(
    identifier="f",
    short="f",
    method=Switch(on_presence=static("A"), on_absence=static("B")),
)
cmd.flag(
    identifier="no-color",
    long="no-color",
    method=Switch(on_presence=disable_color, on_absence=static(None))
)

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args.value_of("f"))
    print(args.value_of("no-color"))
