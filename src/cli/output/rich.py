import typing
from collections.abc import Callable
from functools import cached_property
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import rich

T = TypeVar("T")
if TYPE_CHECKING:
    from rich.console import Console


class ObjectProxy(Generic[T]):
    def __init__(self, create_function: Callable[[], T]) -> None:
        self.__create_function = create_function

    @cached_property
    def actual_object(self) -> T:
        return self.__create_function()

    def __getattr__(self, name: str) -> Any:
        return self.actual_object.__getattribute__(name)


untyped_console = ObjectProxy(create_function=rich.get_console)
console = typing.cast("Console", untyped_console)  # increase startup performance
