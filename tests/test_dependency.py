from typing import Never

import pytest

from powercli.command import Command
from powercli.dependency import Resolver
from powercli.exceptions import MissingDependencyError


def test_cyclic_dependency() -> None:
    resolver = Resolver()
    resolver.dependencies["a"] = {"b"}
    resolver.dependencies["b"] = {"c"}
    resolver.dependencies["c"] = {"a"}
    assert resolver.cyclic()
    with pytest.raises(RuntimeError):
        resolver.lock()

    resolver = Resolver()
    resolver.dependencies["a"] = {"b", "c"}
    resolver.dependencies["b"] = {"d"}
    resolver.dependencies["c"] = {"d"}
    resolver.dependencies["d"] = set()
    assert not resolver.cyclic()
    resolver.lock()


def test_one_dependency() -> None:
    cmd: Command[Never, Never] = Command()
    cmd.flag(identifier="f", short="f")
    cmd.flag(identifier="g", short="g", dependencies={"f"})
    with pytest.raises(MissingDependencyError):
        cmd.parse_args(["-g"])


def test_chained_dependency() -> None:
    cmd: Command[Never, Never]
    cmd = Command(add_common_flags=False)
    with pytest.raises(MissingDependencyError):
        cmd.flag(identifier="f", short="f", dependencies={"g"})
        cmd.flag(identifier="g", short="g", dependencies={"h"})
        cmd.flag(identifier="h", short="h")
        cmd.parse_args(["-f"])
    cmd = Command(add_common_flags=False)
    with pytest.raises(MissingDependencyError):
        cmd.flag(identifier="f", short="f", dependencies={"g"})
        cmd.flag(identifier="g", short="g", dependencies={"h"})
        cmd.flag(identifier="h", short="h")
        cmd.parse_args(["-f", "-g"])
    cmd = Command(add_common_flags=False)
    with pytest.raises(MissingDependencyError):
        cmd.flag(identifier="f", short="f", dependencies={"g"})
        cmd.flag(identifier="g", short="g", dependencies={"h"})
        cmd.flag(identifier="h", short="h")
        cmd.parse_args(["-f", "-h"])
