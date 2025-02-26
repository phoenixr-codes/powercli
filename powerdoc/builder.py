from abc import ABCMeta, abstractmethod
from pathlib import Path


class Builder(metaclass=ABCMeta):
    path: Path
    """Directory where to put the files in."""

    @abstractmethod
    def build(self) -> None:
        """Build the desired files."""
