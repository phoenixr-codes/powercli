from typing import Never

import pytest

from powercli import methods
from powercli.command import Command


def test_repetition() -> None:
    cmd: Command[list[str | int], Never] = Command()
    cmd.flag(
        identifier="warnings",
        short="w",
        method=methods.Repeat(),
        values=[("ID", str), ("MAX", int)],
    )
    args = cmd.parse_args(["-w", "foo", "2", "-w", "bar", "6"])
    assert args.value_of_flag("warnings") == [["foo", 2], ["bar", 6]]


def test_validation() -> None:
    cmd: Command[list[int], Never] = Command()
    cmd.flag(
        identifier="f",
        short="f",
        values=[("ID", int)],
        method=methods.Repeat(validate_amount=lambda _, n: n in range(1, 3)),
    )

    args = cmd.parse_args(["-f", "1", "-f", "2"])
    assert args.value_of_flag("f") == [[1], [2]]

    with pytest.raises(RuntimeError):
        cmd.parse_args(["-f", "1", "-f", "2", "-f", "3"])
