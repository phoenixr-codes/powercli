from enum import auto, StrEnum
import sys
from typing import Any

from loguru import logger
from rich import print

from powercli import Command
from powercli.utils import member_of

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

class Pet(StrEnum):
    DOG = auto()
    CAT = auto()

cmd: Command[Any, Any] = Command(add_common_flags=True)
cmd.pos(identifier="foo", name="FOO", into=member_of(Pet))

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
