from enum import StrEnum

import pytest

import powercli.utils
from powercli.utils import member_of


def test_did_you_mean() -> None:
    assert (
        powercli.utils._did_you_mean("builf", ["build", "package", "run"])
        == "did you mean 'build'?"
    )

    assert (
        powercli.utils._did_you_mean("builf", ["build", "built", "package", "run"])
        == "did you mean one of 'built' or 'build'?"
    )

    assert (
        powercli.utils._did_you_mean(
            "builf", ["build", "built", "buila", "package", "run"]
        )
        == "did you mean one of 'built', 'build' or 'buila'?"
    )


def test_enum_member_converter() -> None:
    class Pet(StrEnum):
        CAT = "cat"
        DOG = "dog"

    assert member_of(Pet)("Cat") == Pet.CAT
    assert member_of(Pet)("dog") == Pet.DOG
    assert member_of(Pet, ignore_case=False)("cat") == Pet.CAT
    with pytest.raises(ValueError):
        member_of(Pet, ignore_case=False)("Cat")
