import sys

from loguru import logger
from rich import print

from powercli import Command, Flag
from powercli.utils import one_of, static

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
        required=static(True),
    )
)

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
