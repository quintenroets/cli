import os
import shlex
import sys
import typing
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast


class StringLike(Protocol):
    def __str__(self) -> str: ...


CommandItem = (
    StringLike | dict[str, StringLike] | Sequence[StringLike] | Iterator[StringLike]
)


@dataclass
class CommandPreparer:
    items: Iterable[CommandItem]
    use_shell_command: bool = False
    new_tab: bool = False
    use_root: bool = False
    title: str | None = None

    def run(self) -> tuple[str, ...]:
        parts = (
            self.generate_shell_command_parts()
            if self.use_shell_command
            else self.generate_command_parts()
        )
        return tuple(parts)

    def generate_shell_command_parts(self) -> Iterator[str]:
        command = " ".join(self.generate_command_parts())
        if self.new_tab:
            yield from self.generate_new_tab_command_parts(command)
        else:
            yield command

    def generate_new_tab_command_parts(self, command: str) -> Iterator[str]:
        cwd = str(Path.cwd())
        if running_in_cmux():
            script = create_cmux_new_tab_script(command, cwd, self.title)
            yield from ("sh", "-c", script)
        elif sys.platform == "darwin":
            yield from ("osascript", "-e", create_mac_new_tab_script(command, cwd))
        else:
            os.environ.setdefault("DISPLAY", ":0.0")
            shell = os.getenv("SHELL") or "/bin/bash"
            yield from ("konsole", "--new-tab", "--workdir", cwd, "-e", shell, "-c")
            if self.title is not None:
                command = f"echo -ne '\\033]30;{self.title}\\007'; " + command
            yield command

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

    def extract_items_as_strings(self, command_item: CommandItem) -> Iterator[str]:
        for item in self.extract_items(command_item):
            yield str(item)

    @classmethod
    def extract_items(cls, item: CommandItem) -> Iterator[StringLike]:
        collection_types = list, tuple, Iterator
        is_collection = any(
            isinstance(item, collection) for collection in collection_types
        )
        if is_collection:
            yield from typing.cast("Iterable[StringLike]", item)
        elif isinstance(item, dict):
            for key, value in item.items():
                yield f"--{key}"
                if value is not None:
                    yield value
        elif isinstance(item, set):
            for part in item:
                yield f"--{part}"
        elif hasattr(item, "__str__"):
            yield cast("str", item)


def running_in_cmux() -> bool:
    return bool(os.getenv("CMUX_TAB_ID"))


def create_cmux_new_tab_script(command: str, cwd: str, title: str | None) -> str:
    payload = shlex.quote(f"cd {shlex.quote(cwd)} && {command}\n")
    create_surface = (
        "surface=$(cmux --id-format uuids new-surface --type terminal --focus true"
        " | awk '{print $2}')"
    )
    steps = [create_surface, f'cmux send --surface "$surface" {payload}']
    if title is not None:
        steps.append(f'cmux rename-tab --surface "$surface" {shlex.quote(title)}')
    return " && ".join(steps)


def create_mac_new_tab_script(command: str, cwd: str) -> str:
    cwd = shlex.quote(cwd)
    if os.getenv("TERM_PROGRAM") == "iTerm.app":
        lines = (
            'tell application "iTerm2"',
            "  tell current window",
            "    create tab with default profile",
            "    tell current session of current tab",
            f'      write text "cd {cwd}"',
            f'      write text "{command}"',
            "    end tell",
            "  end tell",
            "end tell",
        )
        script = "\n".join(lines)
    else:
        script = f'tell application "Terminal" to do script "cd {cwd} && {command}"'
    return script
