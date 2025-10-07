"""PowerCLI - Build powerful command-line applications in Python."""

# TODO: __main__ to generate completions

from __future__ import annotations

__all__ = ["Argument", "Flag", "Positional", "Category", "Command", "Static"]

from .args import Argument, Flag, Positional
from .category import Category
from .command import Command
from .static import Static
