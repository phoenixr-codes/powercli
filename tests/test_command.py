from typing import Never

import pytest

from powercli.args import Flag, Positional
from powercli.command import Command
from powercli.utils import one_of, static


def test_prefix() -> None:
    Command(prefix_short=None, prefix_long=None)  # this is fine :)

    with pytest.raises(ValueError):
        Command(prefix_short="-", prefix_long="-")

    with pytest.raises(ValueError):
        Command(prefix_short="")

    with pytest.raises(ValueError):
        Command(prefix_long="")

    with pytest.raises(ValueError):
        Command(prefix_short="++", prefix_long="+")


def test_positional_and_subcommand() -> None:
    cmd = Command[None, None]()
    pos: Positional[Never, Never, Never] = Positional(name="hello")

    with pytest.raises(ValueError):
        Command[None, None]().add_arg(pos).add_subcommand(cmd)


def test_has_subcommand() -> None:
    assert Command().add_subcommand(Command(name="hi")).has_subcommand()
    assert not Command().has_subcommand()


def test_has_positional() -> None:
    assert Command().add_arg(Positional(name="p")).has_positional()
    assert not Command().has_positional()


def test_has_flag() -> None:
    assert Command(add_common_flags=False).add_arg(Flag(short="f")).has_flag()
    assert not Command(add_common_flags=False).has_flag()


def test_flag_without_proper_prefix() -> None:
    with pytest.raises(ValueError):
        Command(prefix_short=None, prefix_long=None).flag(short="f")

    with pytest.raises(ValueError):
        Command(prefix_long=None).flag(long="fire")

    with pytest.raises(ValueError):
        Command(prefix_short=None, prefix_long=None).flag(short="f", long="fire")


def test_multi_flag() -> None:
    cmd = Command[None, None]()
    cmd.flag(identifier="f", short="f")
    cmd.flag(identifier="g", short="g")
    cmd.flag(identifier="j", short="j")
    args = cmd.parse_args(["-fgj"])
    assert args.is_present("f") and args.is_present("g") and args.is_present("j")


def test_one_flag_of_multiple() -> None:
    cmd: Command[None, None] = Command(
        add_common_subcommands=False, add_common_flags=False
    )
    cmd.add_args(
        one_of(
            Flag(identifier="f", short="f"),
            Flag(identifier="g", short="g"),
            Flag(identifier="h", short="h"),
        )
    )
    args = cmd.parse_args(["-f"])
    assert (
        args.is_present("f") and not args.is_present("g") and not args.is_present("h")
    )

    cmd = Command(add_common_subcommands=False, add_common_flags=False)
    cmd.add_args(
        one_of(
            Flag(identifier="f", short="f"),
            Flag(identifier="g", short="g"),
            Flag(identifier="h", short="h"),
        )
    )
    args = cmd.parse_args(["-g"])
    assert (
        not args.is_present("f") and args.is_present("g") and not args.is_present("h")
    )

    cmd = Command(add_common_subcommands=False, add_common_flags=False)
    cmd.add_args(
        one_of(
            Flag(identifier="f", short="f"),
            Flag(identifier="g", short="g"),
            Flag(identifier="h", short="h"),
        )
    )
    with pytest.raises(RuntimeError):
        args = cmd.parse_args(["-f", "-g"])

    cmd = Command(add_common_subcommands=False, add_common_flags=False)
    cmd.add_args(
        one_of(
            Flag(identifier="f", short="f"),
            Flag(identifier="g", short="g"),
            Flag(identifier="h", short="h"),
        )
    )
    with pytest.raises(RuntimeError):
        args = cmd.parse_args(["-g", "-h"])

    cmd = Command(add_common_subcommands=False, add_common_flags=False)
    cmd.add_args(
        one_of(
            Flag(identifier="f", short="f"),
            Flag(identifier="g", short="g"),
            Flag(identifier="h", short="h"),
        )
    )
    with pytest.raises(RuntimeError):
        args = cmd.parse_args(["-f", "-h"])

    cmd = Command(add_common_subcommands=False, add_common_flags=False)
    cmd.add_args(
        one_of(
            Flag(identifier="f", short="f"),
            Flag(identifier="g", short="g"),
            Flag(identifier="h", short="h"),
            required=static(True),
        )
    )
    with pytest.raises(RuntimeError):
        args = cmd.parse_args([])

    cmd = Command(add_common_subcommands=False, add_common_flags=False)
    cmd.add_args(
        one_of(
            Flag(identifier="f", short="f"),
            Flag(identifier="g", short="g"),
            Flag(identifier="h", short="h"),
            required=static(True),
        )
    )
    args = cmd.parse_args(["-g"])
    assert args.is_absent("f") and args.is_present("g") and args.is_absent("h")


def test_fixed_values() -> None:
    cmd: Command[str | int, None] = Command()
    cmd.flag(identifier="f", short="f", values=[("A", str), ("B", str)])
    args = cmd.parse_args(["-f", "hello", "world"])
    assert args.value_of_flag("f") == ["hello", "world"]


def test_variable_values() -> None:
    cmd: Command[int | float, None] = Command()
    cmd.flag(identifier="f", short="f", values=[("X", int), ...])
    assert cmd.parse_args(["-f", "1", "2", "3"]).value_of("f") == [1, 2, 3]

    cmd = Command(add_common_subcommands=False, add_common_flags=False)
    cmd.flag(identifier="f", short="f", values=[("X", int), ...])
    with pytest.raises(RuntimeError):
        cmd.parse_args(["-f", "1", "2", "3", "n"])

    cmd = Command()
    cmd.flag(identifier="f", short="f", values=[("X", int), ...])
    cmd.pos(identifier="foo", name="FOO")
    args = cmd.parse_args(["-f", "1", "2", "3", "foo"])
    assert args.value_of_flag("f") == [1, 2, 3]
    assert args.value_of_positional("foo") == "foo"

    cmd = Command(add_common_subcommands=False, add_common_flags=False)
    cmd.flag(identifier="f", short="f", values=[("X", int), ..., ("Y", float), ...])
    args = cmd.parse_args(["-f", "12", "13", "14", "1.1", "1.3", "3"])
    assert args.value_of_flag("f") == [12, 13, 14, 1.1, 1.3, 3.0]


def test_flag_value_containing_prefix() -> None:
    cmd: Command[str, None]

    cmd = Command()
    cmd.flag(identifier="f", short="f", values=[("A", str)])
    args = cmd.parse_args(["-f", "-x"])
    assert args.value_of_flag("f") == ["-x"]

    cmd = Command()
    cmd.flag(identifier="f", short="f", values=[("A", str)])
    cmd.flag(identifier="x", short="x")
    args = cmd.parse_args(["-f", "-x"])
    assert args.value_of_flag("f") == ["-x"]
    assert args.is_absent("x")


def test_flag_with_default() -> None:
    cmd: Command[int, None] = Command(
        add_common_subcommands=False, add_common_flags=False
    )
    cmd.flag(identifier="f", short="f", values=[("X", int)], default=static([42]))
    args = cmd.parse_args([])
    assert args.value_of("f") == [42]


def test_positional_with_default() -> None:
    cmd: Command[None, int] = Command()
    cmd.pos(identifier="p", name="POS", into=int, default=static(42))
    args = cmd.parse_args([])
    assert args.value_of_positional("p") == 42
