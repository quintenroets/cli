import os
import shlex
import typing
from collections.abc import Iterable, Iterator
from dataclasses import dataclass


@dataclass
class CommandPreparer:
    items: Iterable[object]
    use_shell_command: bool = False
    use_root: bool = False

    def create_arguments(self) -> tuple[str, ...]:
        return (
            (self.create_command(),)
            if self.use_shell_command
            else tuple(self.generate_command_parts())
        )

    def create_command(self) -> str:
        parts = self.generate_command_parts()
        return " ".join(parts) if self.use_shell_command else shlex.join(parts)

    def generate_command_parts(self) -> Iterator[str]:
        if self.use_root and os.name == "posix":
            yield "sudo"
        for i, item in enumerate(self.items):
            if i == 0 and isinstance(item, str) and not self.use_shell_command:
                # allow first argument in the form of a command
                # only split if no shell command used
                yield from shlex.split(item)
            else:
                yield from self.extract_items_as_strings(item)

    def extract_items_as_strings(self, command_item: object) -> Iterator[str]:
        for item in self.extract_items(command_item):
            yield str(item)

    @classmethod
    def extract_items(cls, item: object) -> Iterator[object]:
        collection_types = list, tuple, Iterator
        is_collection = any(
            isinstance(item, collection) for collection in collection_types
        )
        if is_collection:
            yield from typing.cast("Iterable[object]", item)
        elif isinstance(item, dict):
            for key, value in item.items():
                yield f"--{key}"
                if value is not None:
                    yield value
        elif isinstance(item, set):
            for part in item:
                yield f"--{part}"
        elif hasattr(item, "__str__"):
            yield item
