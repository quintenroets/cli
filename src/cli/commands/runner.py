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
    wait: bool = True
    console: bool = False
    text: bool = True
    check: bool = True
    shell: bool = False
    capture_output_tty: bool = False
    title: str | None = None
    verbose_errors: bool = True
    input: str | None = None
    stdout: int | None = None
    stderr: int | None = None
    _capture_output: bool = False
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for key, value in self.kwargs.items():
            self.__setattr__(key, value)

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

    def prepare_run(self) -> None:
        if self.console:
            self.prepare_console_command()
        if not self.wait:
            self.stdout = subprocess.DEVNULL
            self.stderr = subprocess.DEVNULL

    def capture_output(self) -> str:
        self._capture_output = True
        return self.run().stdout.strip()

    def capture_return_code(self) -> int:
        self.check = False
        self._capture_output = True
        return self.run().returncode

    def run(self) -> subprocess.CompletedProcess[T1]:
        return self.start_run(self._run)

    def _run(self) -> subprocess.CompletedProcess[T1]:
        return subprocess.run(
            self.command_parts,
            text=self.text,
            check=self.check,
            shell=self.shell,
            capture_output=self._capture_output,
            input=self.input,
            stdout=self.stdout,
            stderr=self.stderr,
        )

    def launch(self) -> subprocess.Popen[str]:
        return self.start_run(self._launch)

    def _launch(self) -> subprocess.Popen[str]:
        return subprocess.Popen(
            self.command_parts,
            text=self.text,
            shell=self.shell,
            stdout=self.stdout,
            stderr=self.stderr,
        )

    def start_run(self, runner: Callable[[], T2]) -> T2:
        self.prepare_run()
        try:
            return runner()
        except subprocess.CalledProcessError as error:
            raised_error = (
                CalledProcessError(error.stderr or error)
                if self.verbose_errors
                else error
            )
            raise raised_error

    def prepare_console_command(self) -> None:
        self.activate_console()
        self.wait = False  # avoid blocking for console openening
        if "DISPLAY" not in os.environ:
            # needed for non-login scripts to be able to activate console
            os.environ["DISPLAY"] = ":0.0"

    @classmethod
    def activate_console(cls) -> None:
        args = ("activate_window Konsole",)
        Runner(args, check=False).run()
