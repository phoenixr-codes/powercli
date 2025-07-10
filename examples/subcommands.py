import sys

from loguru import logger
from rich import print

from powercli import Category, Command

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

main_cmd: Command[None, None] = Command(
    add_common_subcommands=False, epilog="Hello World."
)
sub_cmd1: Command[None, None] = Command(
    add_common_subcommands=False, name="foo", description="Does foo stuff"
)
sub_cmd2: Command[None, None] = Command(
    add_common_subcommands=False,
    name="bar",
    description="Does bar stuff",
    long_description="Bar stuff is really important thus this command exists.",
)
sub_cmd3: Command[None, None] = Command(add_common_subcommands=False, name="baz")

main_cmd.add_subcommand(sub_cmd1)
main_cmd.add_subcommand(sub_cmd2)
main_cmd.add_subcommand(sub_cmd3)
main_cmd.flag(short="f", category=Category("hey"))
main_cmd.flag(short="g", category=Category("hey"))
main_cmd.flag(short="x", category=Category("bye"))
main_cmd.flag(short="y", category=Category("bye"))
main_cmd.flag(
    short="z", category=Category("bye"), values=[("X", str), ("Y", str), ("Z", str)]
)

if __name__ == "__main__":
    args = main_cmd.parse_args()
    if (subargs := args.subcommand()) is not None and subargs.command.name == "foo":
        print("Foo!")
    print(args)
