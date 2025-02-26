"""Categories that can be applied on commands and flags."""

from __future__ import annotations

__all__ = ["Color", "Category"]
from typing import TypeAlias

from attrs import define, field

Color: TypeAlias = int
"""A RGB color."""


@define(hash=True, eq=True)
class Category:
    """A category that can be applied on commands and flags."""

    title: str
    """The title of the category."""

    color: Color | None = field(default=None, kw_only=True)
    """An optional color for the category."""
