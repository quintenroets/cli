from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

T = TypeVar("T")
if TYPE_CHECKING:
    from collections.abc import Callable  # pragma: nocover

    from rich.console import Console  # pragma: nocover


class ObjectProxy(Generic[T]):
    def __init__(self, create_function: Callable[[], T]) -> None:
        self.__create_function = create_function

    @cached_property
    def actual_object(self) -> T:
        return self.__create_function()

    def __getattr__(self, name: str) -> Any:
        return self.actual_object.__getattribute__(name)


def load_console() -> Console:
    from rich import get_console  # noqa: PLC0415

    return get_console()


# the proxy keeps rich out of the import path until the console is used
console = cast("Console", ObjectProxy(create_function=load_console))
