from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    import os  # pragma: nocover
    from collections.abc import Mapping  # pragma: nocover


class CommandOptions(TypedDict, total=False):
    root: bool
    new_tab: bool
    title: str | None


class LaunchOptions(CommandOptions, total=False):
    text: bool
    shell: bool
    stdout: int | None
    stderr: int | None
    cwd: str | os.PathLike[str]
    env: Mapping[str, str]


class RunOptions(LaunchOptions, total=False):
    check: bool
    input: str | None
    capture_output: bool


def extract_subprocess_options(options: Mapping[str, object]) -> dict[str, Any]:
    keys = CommandOptions.__optional_keys__
    return {key: value for key, value in options.items() if key not in keys}
