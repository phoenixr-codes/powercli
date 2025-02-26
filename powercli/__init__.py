"""PowerCLI - Build powerful command-line applications in Python."""

# TODO: __main__ to generate completions
# TODO: example usage for (sub)commands (see also: Bun CLI)

from __future__ import annotations

__all__ = ["Argument", "Flag", "Positional", "Category", "Command"]

from .args import Argument, Flag, Positional
from .category import Category
from .command import Command
