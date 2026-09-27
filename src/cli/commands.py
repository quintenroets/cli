from __future__ import annotations

import os
import sys

TYPE_CHECKING = False
if TYPE_CHECKING:
    import subprocess  # pragma: nocover
    from collections.abc import Iterable, Iterator, Mapping  # pragma: nocover
    from typing import Any, TypedDict, Unpack  # pragma: nocover

    class LaunchOptions(TypedDict, total=False):  # pragma: nocover
        root: bool
        text: bool
        shell: bool
        stdout: int | None
        stderr: int | None
        cwd: str | os.PathLike[str]
        env: Mapping[str, str]

    class RunOptions(LaunchOptions, total=False):  # pragma: nocover
        check: bool
        input: str | None
        capture_output: bool


def pipe_output_and_capture(
    commands: Iterable[Iterable[Any]],
    **kwargs: Unpack[RunOptions],
) -> str | None:
    output = None
    for args in commands:
        output = capture_output(*args, **(kwargs | {"input": output}))
    return output


def capture_output_lines(*args: object, **kwargs: Unpack[RunOptions]) -> list[str]:
    return [line for line in capture_output(*args, **kwargs).splitlines() if line]


def capture_output(*args: object, **kwargs: Unpack[RunOptions]) -> str:
    return run(*args, **(kwargs | {"capture_output": True})).stdout.strip()


def completes_successfully(*args: object, **kwargs: Unpack[RunOptions]) -> bool:
    return capture_return_code(*args, **kwargs) == 0


def capture_return_code(*args: object, **kwargs: Unpack[RunOptions]) -> int:
    return run(*args, **(kwargs | {"capture_output": True, "check": False})).returncode


def run_commands_in_shell(*commands: str, **kwargs: Unpack[RunOptions]) -> None:
    return run_commands(*commands, **(kwargs | {"shell": True}))


def run_commands(*commands: str, **kwargs: Unpack[RunOptions]) -> None:
    for command in commands:
        run(command, **kwargs)


def run(
    *args: object,
    **kwargs: Unpack[RunOptions],
) -> subprocess.CompletedProcess[str]:
    import subprocess  # noqa: PLC0415

    options = {"text": True, "check": True, **extract_subprocess_options(kwargs)}
    return subprocess.run(create_arguments(args, kwargs), **options)  # noqa: PLW1510, S603


def launch_commands(*commands: str, **kwargs: Unpack[LaunchOptions]) -> None:
    for command in commands:
        launch(command, **kwargs)


def open_urls(*urls: object) -> None:
    for url in urls:
        if os.name == "nt":
            os.startfile(url)  # type: ignore[attr-defined] # noqa: S606 # pragma: nocover
        else:
            command = "xdg-open" if sys.platform == "linux" else "open"
            launch(command, url)


def launch(
    *args: object,
    **kwargs: Unpack[LaunchOptions],
) -> subprocess.Popen[str]:
    from subprocess import DEVNULL, Popen  # noqa: PLC0415

    overrides = extract_subprocess_options(kwargs)
    options = {"text": True, "stdout": DEVNULL, "stderr": DEVNULL, **overrides}
    return Popen(create_arguments(args, kwargs), **options)  # noqa: S603


def create_arguments(
    items: Iterable[object],
    options: LaunchOptions,
) -> str | tuple[str, ...]:
    arguments = expand_arguments(items, options)
    return " ".join(arguments) if options.get("shell") else tuple(arguments)


def expand_arguments(items: Iterable[object], options: LaunchOptions) -> Iterator[str]:
    import shlex  # noqa: PLC0415
    from collections.abc import Iterator  # noqa: PLC0415

    if options.get("root") and os.name == "posix":
        yield "sudo"
    for i, item in enumerate(items):
        if i == 0 and isinstance(item, str) and not options.get("shell"):
            yield from shlex.split(item)
        elif isinstance(item, list | tuple | Iterator):
            yield from map(str, item)
        elif isinstance(item, dict):
            for key, value in item.items():
                yield f"--{key}"
                if value is not None:
                    yield str(value)
        elif isinstance(item, set):
            for part in item:
                yield f"--{part}"
        else:
            yield str(item)


def extract_subprocess_options(options: Mapping[str, object]) -> dict[str, Any]:
    return {key: value for key, value in options.items() if key != "root"}
