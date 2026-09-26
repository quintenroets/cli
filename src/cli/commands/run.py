from __future__ import annotations

from typing import TYPE_CHECKING, Any, Unpack

from .commands import CommandItem, CommandPreparer
from .options import LaunchOptions, RunOptions, extract_subprocess_options

if TYPE_CHECKING:
    import subprocess  # pragma: nocover
    from collections.abc import Iterable  # pragma: nocover


def pipe_output_and_capture(
    commands: Iterable[Iterable[Any]],
    **kwargs: Unpack[RunOptions],
) -> str | None:
    output = None
    for args in commands:
        output = capture_output(*args, **(kwargs | {"input": output}))
    return output


def capture_output_lines(*args: CommandItem, **kwargs: Unpack[RunOptions]) -> list[str]:
    return [line for line in capture_output(*args, **kwargs).splitlines() if line]


def capture_output(*args: CommandItem, **kwargs: Unpack[RunOptions]) -> str:
    return run(*args, **(kwargs | {"capture_output": True})).stdout.strip()


def completes_successfully(*args: CommandItem, **kwargs: Unpack[RunOptions]) -> bool:
    return capture_return_code(*args, **kwargs) == 0


def capture_return_code(*args: CommandItem, **kwargs: Unpack[RunOptions]) -> int:
    return run(*args, **(kwargs | {"capture_output": True, "check": False})).returncode


def run_commands_in_shell(*commands: str, **kwargs: Unpack[RunOptions]) -> None:
    return run_commands(*commands, **(kwargs | {"shell": True}))


def run_commands(*commands: str, **kwargs: Unpack[RunOptions]) -> None:
    for command in commands:
        run(command, **kwargs)


def run(
    *args: CommandItem,
    **kwargs: Unpack[RunOptions],
) -> subprocess.CompletedProcess[str]:
    import subprocess  # noqa: PLC0415

    options = {"text": True, "check": True, **extract_subprocess_options(kwargs)}
    return subprocess.run(create_arguments(args, kwargs), **options)  # noqa: PLW1510, S603


def launch_commands(*commands: str, **kwargs: Unpack[LaunchOptions]) -> None:
    for command in commands:
        launch(command, **kwargs)


def launch(
    *args: CommandItem,
    **kwargs: Unpack[LaunchOptions],
) -> subprocess.Popen[str]:
    from subprocess import DEVNULL, Popen  # noqa: PLC0415

    overrides = extract_subprocess_options(kwargs)
    options = {"text": True, "stdout": DEVNULL, "stderr": DEVNULL, **overrides}
    return Popen(create_arguments(args, kwargs), **options)  # noqa: S603


def create_arguments(
    items: Iterable[CommandItem],
    options: LaunchOptions,
) -> tuple[str, ...]:
    return CommandPreparer(
        items,
        use_shell_command=options.get("shell", False),
        use_root=options.get("root", False),
    ).create_arguments()
