import powercli.utils


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
