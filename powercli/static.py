"""Declare values used in PowerCLI API as static."""

from __future__ import annotations

from typing import Any

from attrs import frozen

from .typedefs import Context


@frozen
class Static[T]:
    """
    A wrapper around a value that when called with a single argument (the
    context) simply returns the wrapped value.


    This is useful when used for attributes where the actual context is
    irrelevant. On top of that external code such as the help message generator
    can improve the output if a static object is used.

    # Examples

    ```python
    from powercli import Flag, Static

    Flag(
        # ...
        required=Static(True)
    )
    ```
    """

    value: T
    """The wrapped value that is returned when this object is called."""

    def __call__(self, context: Context[Any, Any], *args: Any, **kwargs: Any) -> T:
        return self.value
