from powercli import methods
from powercli.command import Command
from powercli.utils import static


def test_presence_default() -> None:
    cmd = Command[bool, None]()
    cmd.flag(identifier="f", short="f", method=methods.Switch.boolean())

    args = cmd.parse_args(["-f"])
    assert args.value_of_flag("f") == [True]

    args = cmd.parse_args([])
    assert args.value_of_flag("f") == [False]


def test_custom() -> None:
    cmd = Command[int, None]()
    cmd.flag(
        identifier="f",
        short="f",
        method=methods.Switch(on_presence=static(1), on_absence=static(0)),
    )

    args = cmd.parse_args(["-f"])
    assert args.value_of_flag("f") == [1]

    args = cmd.parse_args([])
    assert args.value_of_flag("f") == [0]
