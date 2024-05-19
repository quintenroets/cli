import io
import os
import subprocess
import typing
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Generic, TypeVar

from ..models import CalledProcessError
from .commands import CommandItem, CommandPreparer

T1 = TypeVar("T1", bound=str)
T2 = TypeVar("T2")


@dataclass
class Runner(Generic[T1]):
    items: tuple[CommandItem, ...]
    root: bool = False
    console: bool = False
    title: str | None = None
    quiet: bool = False

    # subprocess arguments
    text: bool = True
    check: bool = True
    shell: bool = False
    input: str | None = None
    stdout: int | None = None
    stderr: int | None = None

    verbose_errors: bool = True
    kwargs: dict[str, Any] = field(default_factory=dict)
    subprocess_kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name, value in self.kwargs.items():
            if hasattr(self, name):
                self.__setattr__(name, value)
            else:
                self.subprocess_kwargs[name] = value

    @cached_property
    def command_parts(self) -> tuple[str, ...]:
        use_shell_command = self.shell or self.console
        command_preparer = CommandPreparer(
            self.items, use_shell_command, self.console, self.root, self.title
        )
        return command_preparer.run()

    def capture_tty_output(self) -> str:
        import tempfile

        with tempfile.TemporaryFile() as untyped_log_file:
            log_file = typing.cast(io.TextIOWrapper, untyped_log_file)
            self.run_in_tty(log_file)
            log_file.seek(0)
            return log_file.read()

    def run_in_tty(self, log_file: io.TextIOWrapper) -> None:
        import pexpect

        command, *args = self.command_parts
        child = pexpect.spawn(command, args, timeout=None, logfile=log_file)
        if self.capture_output is not None:
            child.expect(pexpect.EOF)
        else:
            child.interact()

    def capture_output(self) -> str:
        return self.run(capture_output=True).stdout.strip()

    def capture_return_code(self) -> int:
        self.check = False
        return self.run(capture_output=True).returncode

    def run(
        self, capture_output: bool | None = None
    ) -> subprocess.CompletedProcess[T1]:
        if capture_output is None:
            capture_output = self.quiet
        return self.run_with_exception_handling(self._run, capture_output)

    def _run(self, capture_output: bool) -> subprocess.CompletedProcess[T1]:
        return subprocess.run(
            self.command_parts,
            text=self.text,
            check=self.check,
            shell=self.shell,
            capture_output=capture_output,
            input=self.input,
            stdout=self.stdout,
            stderr=self.stderr,
            **self.subprocess_kwargs,
        )

    def run_in_console(self) -> subprocess.Popen[str]:
        self.prepare_console_command()
        return self.launch()

    def launch(self) -> subprocess.Popen[str]:
        if self.stdout is None:
            self.stdout = subprocess.DEVNULL
        if self.stderr is None:
            self.stderr = subprocess.DEVNULL
        return self.run_with_exception_handling(self._launch)

    def _launch(self) -> subprocess.Popen[str]:
        return subprocess.Popen(
            self.command_parts,
            text=self.text,
            shell=self.shell,
            stdout=self.stdout,
            stderr=self.stderr,
            **self.subprocess_kwargs,
        )

    def run_with_exception_handling(
        self, runner: Callable[..., T2], *args: Any, **kwargs: Any
    ) -> T2:
        try:
            return runner(*args, **kwargs)
        except subprocess.CalledProcessError as error:
            verbose = self.verbose_errors
            raise CalledProcessError(error.stderr or error) if verbose else error

    def prepare_console_command(self) -> None:
        self.console = True
        self.activate_console()
        if "DISPLAY" not in os.environ:  # pragma: nocover
            # needed for non-login scripts to be able to activate console
            os.environ["DISPLAY"] = ":0.0"

    @classmethod
    def activate_console(cls) -> None:
        args = ("activate_window Konsole",)
        try:
            Runner(args, check=False).run()
        except FileNotFoundError:  # pragma: nocover
            pass
