"""Methods influence the behavior of how flags are parsed."""

from __future__ import annotations

__all__ = ["Method", "Normal", "Count", "Repeat", "Switch"]
from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from attrs import define

from .typedefs import Context, WithContext
from .utils import static

if TYPE_CHECKING:
    from .args import Flag


class Method(metaclass=ABCMeta):
    """The base class for a method."""

    @staticmethod
    @abstractmethod
    def _validate_flag(flag: Flag[Any, Any, Any]) -> None:
        """Called when the flag is initialized.

        This method should raise exceptions for invalid flags.
        """


@define
class Normal(Method):
    """The default way of parsing an argument."""

    @staticmethod
    def _validate_flag(flag: Flag[Any, Any, Any]) -> None:
        """Called when the flag is initialized.

        This method should raise exceptions for invalid flags.
        """


@define
class Count[FV, PV](Method):
    """Counts the amount of times the flag has been specified.

    # Examples

    ```python
    from powercli.args import Flag
    from powercli.methods import Count
    from powercli.utils import static

    Flag(
        short="v",
        long="verbose",
        description="Enables verbosity up to 4 different levels"
        method=Count(
            lambda _, amount: amount in range(0, 5),  # restrict range
            default=static(2)  # returned when absent
        )
    )
    ```

    # Requirements

    - The flag does not take any values.
    - The flag does not have any default values.
    """

    validate_amount: Callable[[Context[FV, PV], int], bool | str] = static(True)
    default: WithContext[FV, PV, int] | None = static(0)

    @staticmethod
    def _validate_flag(flag: Flag[Any, Any, Any]) -> None:
        """Called when the flag is initialized.

        This method should raise exceptions for invalid flags.
        """
        if flag.values or flag.default is not None:
            raise RuntimeError(
                "`values` and `default` must not be set when using the `Count` method."
            )


@define
class Repeat[FV, PV](Method):
    """Allows multiple presence of the flag.

    The returned [powercli.parser.ParsedFlag] contains its converted values
    within a list even if the flag does not take any values.

    # Examples

    ```python
    from pathlib import Path

    from powercli.args import Flag
    from powercli.methods import Repeat

    Flag(
        short="W",
        long="warning",
        description="Displays warning messages",
        method=Repeat()
        values=[("PATH", Path)]
    )
    ```

    # Requirements

    - The flag does not take any default values.
    """

    validate_amount: Callable[[Context[FV, PV], int], bool | str] = static(True)
    """A function that validates the amount of repetitions."""

    @staticmethod
    def _validate_flag(flag: Flag[Any, Any, Any]) -> None:
        """Called when the flag is initialized.

        This method should raise exceptions for invalid flags.
        """
        if flag.default is not None:
            raise RuntimeError("`default` must not be set when using `Repeat`")


@define
class Switch[FV, PV, P, A](Method):
    """Evaluates `P` when the value is present or `A` for absence.

    # Parameters

    * `on_presence` - The value evaluated when the flag is present.

    * `on_absence` - The value evaluated when the flag is absent.

    # Examples

    ```python
    from powercli.args import Flag
    from powercli.methods import Switch
    from powercli.utils import static

    Flag(
        short="r",
        description="Walks the directory recursively",
        method=Switch.boolean()
    )
    ```

    # Requirements

    - The flag does not take any values.
    - The flag does not take any default values.
    """

    on_presence: WithContext[FV, PV, P]
    """The value evaluated when the flag is present."""

    on_absence: WithContext[FV, PV, A]
    """The value evaluated when the flag is absent."""

    @staticmethod
    def _validate_flag(flag: Flag[Any, Any, Any]) -> None:
        """Called when the flag is initialized.

        This method should raise exceptions for invalid flags.
        """
        if flag.values or flag.default is not None:
            raise RuntimeError(
                "`values` and `default` must not be set when using the `Switch` method."
            )

    @staticmethod
    def boolean() -> Switch[Any, Any, bool, bool]:
        """A constructor for a commonly used switch that evaluates `True` on presence and `False` on absence."""
        return Switch(
            on_presence=static(True),
            on_absence=static(False),
        )
