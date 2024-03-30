import subprocess
from collections.abc import Iterable
from typing import Any

from .commands import CommandItem
from .runner import Runner


def run(*args: CommandItem, **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return Runner[str](args, kwargs=kwargs).run()


def run_in_console(*args: CommandItem, **kwargs: Any) -> subprocess.Popen[str]:
    return Runner[str](args, kwargs=kwargs).run_in_console()


def capture_output_lines(*args: CommandItem, **kwargs: Any) -> list[str]:
    output = capture_output(*args, **kwargs)
    return [line for line in output.splitlines() if line]


def capture_output(*args: CommandItem, **kwargs: Any) -> str:
    return Runner[str](args, kwargs=kwargs).capture_output()


def completes_successfully(*args: CommandItem, **kwargs: Any) -> bool:
    return capture_return_code(*args, **kwargs) == 0


def capture_return_code(*args: CommandItem, **kwargs: Any) -> int:
    return Runner(args, kwargs=kwargs).capture_return_code()


def launch(*args: CommandItem, **kwargs: Any) -> subprocess.Popen[str]:
    return Runner(args, kwargs=kwargs).launch()


def run_commands_in_shell(*commands: str, **kwargs: Any) -> None:
    return run_commands(*commands, shell=True, **kwargs)


def run_commands(*commands: str, **kwargs: Any) -> None:
    for command in commands:
        args = (command,)
        Runner(args, kwargs=kwargs).run()


def launch_commands(*commands: str, **kwargs: Any) -> None:
    for command in commands:
        args = (command,)
        Runner(args, kwargs=kwargs).launch()


def pipe_output_and_capture(
    commands: Iterable[Iterable[Any]], **kwargs: Any
) -> str | None:
    output = None
    for args in commands:
        output = Runner(tuple(args), input=output, kwargs=kwargs).capture_output()
    return output
