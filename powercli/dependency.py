"""Utilities related to dependency management."""

from __future__ import annotations

__all__ = ["Resolver"]
from collections import deque
from collections.abc import Generator

from attrs import define, field

from .typedefs import Identifier


# TODO: maybe switch to standard library graphlib.TopologicalSorter
@define
class Resolver:
    """A dependency resolver."""

    dependencies: dict[Identifier, set[Identifier]] = field(init=False, factory=dict)

    def cyclic(self) -> bool:
        """Returns `True` when dependencies are cyclic."""
        for identifier in self.dependencies:
            check_next = deque([identifier])
            while len(check_next) > 0 and (ident := check_next.pop()):
                for dep in self.dependencies[ident]:
                    if dep == identifier:
                        return True
                    check_next.append(dep)
        return False

    def lock(self) -> None:
        """Mark the dependencies as done."""
        if self.cyclic():
            raise RuntimeError("cyclic dependencies")

    def cover(self, identifier: Identifier, /) -> Generator[Identifier, None, None]:
        """Yields each ID which no longer depends on any args after the operation."""
        for key, value in self.dependencies.items():
            value.discard(identifier)
            if not value:
                yield key

    def uncovered(self) -> tuple[Identifier, set[Identifier]] | None:
        """Returns each identifier and dependency of arguments whose dependencies are not covered."""
        for key, value in self.dependencies.items():
            if value:
                return (key, value)
        return None
