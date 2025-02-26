"""Type definitions used within the `powercli` package."""

from __future__ import annotations

__all__ = [
    "Context",
    "Converter",
    "Identifier",
    "WithContext",
]

from collections.abc import Callable

from .parser import ParsedCommand

type Identifier = str
"""An identifier for arguments which can be used for queries for instance."""

type Converter[T] = Callable[[str], T]
"""A function that takes a `str` and converts it into a different type."""

type Context[FV, PV] = ParsedCommand[FV, PV]
"""
The context containing parsed commands and arguments which can be used for
runtime checks.
"""

type WithContext[FV, PV, T] = Callable[[Context[FV, PV]], T]
"""A function evaluating a value depending on the context."""
