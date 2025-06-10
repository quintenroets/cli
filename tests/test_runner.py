import os
import string
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, settings, strategies
from hypothesis.strategies import SearchStrategy

import cli
from cli.commands.runner import Runner

linux_only_test = pytest.mark.skipif(
    os.name != "posix",
    reason="Bash specific syntax used for tests",
)


def text_strategy() -> SearchStrategy[str]:
    return strategies.text(alphabet=string.ascii_letters)


@given(message=text_strategy())
def test_capture_output(message: str) -> None:
    assert cli.capture_output("printf", "%s", message) == message


@given(message=text_strategy())
def test_capture_output_lines(message: str) -> None:
    assert cli.capture_output_lines("printf", "%s", message) == message.splitlines()


@settings(deadline=3000)
@given(message=text_strategy())
def test_pipe_output_and_capture(message: str) -> None:
    commands = (
        ("printf", "%s", message),
        ("grep", "-F", "--", message),
    )
    assert cli.pipe_output_and_capture(commands, check=False) == message


@given(return_code=strategies.integers(min_value=0, max_value=255))
@linux_only_test
def test_capture_return_code(return_code: int) -> None:
    assert cli.capture_return_code("exit", return_code, shell=True) == return_code  # noqa: S604


@given(return_code=strategies.integers(min_value=0, max_value=255))
@linux_only_test
def test_completes_successfully(return_code: int) -> None:
    success = return_code == 0
    assert cli.completes_successfully("exit", return_code, shell=True) == success  # noqa: S604


def test_run_commands() -> None:
    commands = ("ls", "pwd")
    cli.run_commands(*commands)


def test_launch() -> None:
    cli.launch("ls")


def test_launch_commands() -> None:
    cli.launch_commands("ls")


def test_run_commands_in_shell() -> None:
    cli.run_commands_in_shell("ls")


@patch("subprocess.Popen")
def test_open(mocked_launch: MagicMock) -> None:
    cli.open_urls("pwd")
    mocked_launch.assert_called_once()


def test_tty() -> None:
    Runner(items=["ls"]).capture_tty_output()
