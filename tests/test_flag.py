from typing import Never

import pytest

from powercli.args import Flag


def test_get_names() -> None:
    assert {"foo", "f", "hello", "world", "b", "c", "d"} == set(
        Flag(
            short="f",
            long="foo",
            short_aliases={"b"},
            short_hidden_aliases={"c", "d"},
            long_aliases={"hello", "world"},
        ).names()
    )


def test_overlapping_names() -> None:
    with pytest.raises(RuntimeError):
        Flag(short="f", long="f")

    with pytest.raises(RuntimeError):
        Flag(short="f", short_hidden_aliases={"f"})

    with pytest.raises(RuntimeError):
        Flag(long="foo", long_aliases={"foo"})

    with pytest.raises(RuntimeError):
        Flag(short="f", long_aliases={"f"})


def test_missing_name() -> None:
    with pytest.raises(RuntimeError):
        Flag()

    with pytest.raises(RuntimeError):
        Flag(short_aliases={"f", "g"})

    with pytest.raises(RuntimeError):
        Flag(short_hidden_aliases={"f", "g"}, long_aliases={"foo", "bar"})


def test_more_of_nothing() -> None:
    with pytest.raises(RuntimeError):
        Flag(short="f", values=[...])

    with pytest.raises(RuntimeError):
        Flag(short="f", values=[..., ...])

    with pytest.raises(RuntimeError):
        Flag[Never, Never, int](short="f", values=[("X", int), ..., ...])

    with pytest.raises(RuntimeError):
        Flag[Never, Never, int](short="f", values=[..., ("X", int)])
