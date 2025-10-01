import sys

from loguru import logger
from rich import print

from powercli import Command
from powercli.deprecation import Deprecation
from powercli.typedefs import Context

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

deprecation = Deprecation("use -h instead when -f is 1", since="1.0")

def f_deprecation(ctx: Context[int, None]) -> Deprecation | None:
    if ctx.value_of("f") == [1]:
        return deprecation
    return None

cmd: Command[int, None]
cmd = Command()
cmd.flag(identifier="f", short="f", values=[("INT", int)])
cmd.flag(
    identifier="g", short="g", values=[("INT", int)], deprecation=f_deprecation
)

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
