import sys

from loguru import logger
from rich import print

from powercli import Command, Flag, Static
from powercli.utils import one_of

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

cmd: Command[None, None] = Command(add_common_subcommands=False, add_common_flags=False)
cmd.add_args(
    one_of(
        Flag(identifier="f", short="f"),
        Flag(identifier="g", short="g"),
        Flag(identifier="h", short="h"),
    )
)
cmd.add_args(
    one_of(
        Flag(identifier="i", short="i"),
        Flag(identifier="j", short="j"),
        Flag(identifier="k", short="k"),
        required=Static(True),
    )
)

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
