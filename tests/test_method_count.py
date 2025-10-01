from typing import Never, TypeVar

import pytest

from powercli import methods
from powercli.args import Flag
from powercli.command import Command
from powercli.exceptions import MissingDependencyError
from powercli.static import Static
from powercli.typedefs import Context, Identifier

FV = TypeVar("FV")
PV = TypeVar("PV")


def test_values_and_default() -> None:
    with pytest.raises(RuntimeError):
        Flag(short="f", method=methods.Count(), values=[("X", str)])

    with pytest.raises(RuntimeError):
        Flag(short="f", method=methods.Count(), default=Static(["foo"]))


def test_counting() -> None:
    cmd: Command[int, Never]

    cmd = Command()
    cmd.flag(identifier="f", short="f", method=methods.Count())
    assert cmd.parse_args(["-f", "-f", "-f"]).value_of("f") == [3]

    cmd = Command()
    cmd.flag(identifier="f", short="f", method=methods.Count())
    assert cmd.parse_args(["-fff"]).value_of("f") == [3]

    cmd = Command()
    cmd.flag(identifier="f", short="f", method=methods.Count())
    assert cmd.parse_args([]).value_of("f") == [0]

    cmd = Command()
    cmd.flag(identifier="f", short="f", method=methods.Count())
    cmd.flag(short="g")
    assert cmd.parse_args(["-f", "-g", "-f"]).value_of("f") == [2]
    assert cmd.parse_args(["-ff", "-g", "-ff", "-f"]).value_of("f") == [5]


def test_default() -> None:
    cmd: Command[int, Never] = Command()
    cmd.flag(
        identifier="f",
        short="f",
        method=methods.Count(default=lambda ctx: _first(ctx, "g") or 0),
        dependencies={"g"},
    )
    cmd.flag(identifier="g", short="g", values=[("X", int)])
    with pytest.raises(MissingDependencyError):
        cmd.parse_args([]).value_of("f")
    assert cmd.parse_args(["-g", "10"]).value_of("f") == [10]
    assert cmd.parse_args(["-f", "-g", "10", "-f"]).value_of("f") == [2]


def test_validation() -> None:
    cmd: Command[int, Never] = Command()
    cmd.flag(
        identifier="f",
        short="f",
        method=methods.Count(validate_amount=lambda _, amt: amt in range(1, 3)),
    )
    with pytest.raises(RuntimeError):
        cmd.parse_args(["-fff"])


def _first(ctx: Context[FV, PV], flag_identifier: Identifier) -> FV | int | None:
    values = ctx.value_of_flag(flag_identifier)
    if values is None:
        return None
    it = iter(values)
    return next(it)
