"""Management of deprecation of the CLI."""

from __future__ import annotations

from attrs import define, field


@define
class Deprecation:
    """A deprecation that can be applied on commands and arguments."""

    message: str | None = None
    """
    An optional message describing the reason and/or alternatives of the
    deprecation
    """

    since: str | None = field(kw_only=True, default=None)
    """
    An optional version since when the deprecation started.
    """
