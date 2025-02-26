import sys
from typing import Never

from loguru import logger
from rich import print

from powercli import Category, Command

logger.enable("powercli.command")
logger.add(sys.stdout, level="TRACE")

cool_category = Category(title="Cool", color=0xE559E3)

foo_cmd: Command[Never, Never] = Command(name="foo")
bar_cmd: Command[Never, Never] = Command(name="bar", category=cool_category)
baz_cmd: Command[Never, Never] = Command(name="baz", category=cool_category)

cmd: Command[str | int, None] = (
    Command(
        add_common_subcommands=True,
        description="A really cool command",
        long_description="Dis, platea cras suscipit eu pulvinar, dolor bibendum pellentesque. Praesent faucibus dolor sit dignissim euismod, elementum enim, dui maecenas. Eget, nunc non molestie magna ac odio habitasse montes leo. Massa dapibus maximus, consectetur ante amet odio mi adipiscing erat. Faucibus eget, nunc diam nulla pellentesque turpis arcu praesent odio.",
    )
    .flag(
        short="f",
        description="Does absolutely nothing",
        long_description=(
            "But maybe, and only maybe, if you just try hard enough, you "
            "might be able to make it do something."
        ),
    )
    .flag(
        short="g",
        description="Also, does absolutely nothing",
        values=[("PATH", str), ("SIZE", int), ...],
    )
    .add_subcommand(foo_cmd)
    .add_subcommand(bar_cmd)
    .add_subcommand(baz_cmd)
)

if __name__ == "__main__":
    args = cmd.parse_args()
    print(args)
