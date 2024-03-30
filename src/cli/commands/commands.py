import os
import shlex
import types
import typing
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Protocol


class StringLike(Protocol):
    def __str__(self) -> str: ...


CommandItem = StringLike | dict[str, StringLike] | set[StringLike] | list[StringLike]


@dataclass
class CommandPreparer:
    items: tuple[CommandItem, ...]
    use_shell_command: bool = False
    use_console: bool = False
    use_root: bool = False
    title: str | None = None
    askpass_key: str = "SUDO_ASKPASS"
    root_keyword: str = "sudo"

    def run(self) -> tuple[str, ...]:
        use_shell_command = self.use_shell_command
        return (
            self.prepare_shell_command()
            if use_shell_command
            else self.prepare_command()
        )

    def prepare_command(self) -> tuple[str, ...]:
        return tuple(self.generate_command_parts())

    def prepare_shell_command(self) -> tuple[str, ...]:
        command = " ".join(self.generate_command_parts())
        commands: tuple[str, ...]
        if self.should_use_root(command):
            if not command.startswith(self.root_keyword):
                command = f"{self.root_keyword } {command}"
            if self.askpass_is_available:
                command = command.replace(self.root_keyword, f"{self.root_keyword} -A")
        if self.use_console:
            if self.title is not None:
                command = self.create_title_command() + command
            shell = os.getenv("SHELL") or "/bin/bash"
            commands = ("konsole", "--new-tab", "-e", shell, "-c", command)
        else:
            commands = (command,)
        return commands

    def create_title_command(self) -> str:
        return f"echo -ne '\\033]30;{self.title}\\007'; "

    @cached_property
    def askpass_is_available(self) -> bool:
        askpass_program = os.environ.get(self.askpass_key)
        return askpass_program is not None and Path(askpass_program).exists()

    def should_use_root(self, first_command_part: str) -> bool:
        if os.name == "posix":
            should_use_root = self.use_root or self.root_keyword in first_command_part
        else:
            should_use_root = False
        return should_use_root

    def generate_command_parts(self) -> Iterator[str]:
        command_parts = self._generate_command_parts()
        first_part = next(command_parts, None)
        if first_part is not None:
            if self.use_shell_command:
                yield first_part
            else:
                yield from self.generate_root_parts(first_part)
        yield from command_parts

    def generate_root_parts(self, first_part: str) -> Iterator[str]:
        if self.should_use_root(first_part):
            yield self.root_keyword
            if self.askpass_is_available:
                yield "-A"
        if first_part != self.root_keyword:
            yield first_part

    def _generate_command_parts(self) -> Iterator[str]:
        for i, item in enumerate(self.items):
            if i == 0 and isinstance(item, str) and not self.use_shell_command:
                # allow first argument in the form of a command
                # only split if no shell command used
                yield from shlex.split(item)
            else:
                yield from self.extract_items_as_strings(item)

    def extract_items_as_strings(self, item: CommandItem) -> Iterator[str]:
        for item in self.extract_items(item):
            yield str(item)

    @classmethod
    def extract_items(cls, item: CommandItem) -> Iterator[StringLike]:
        collection_types = list, tuple, types.GeneratorType
        is_collection = any(
            isinstance(item, collection) for collection in collection_types
        )
        if is_collection:
            yield from typing.cast(Iterable[StringLike], item)
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
