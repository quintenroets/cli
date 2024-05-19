import os
import string

import cli
import pytest
from hypothesis import given, settings, strategies
from hypothesis.strategies import SearchStrategy
from superpathlib import Path

linux_only_test = pytest.mark.skipif(
    os.name != "posix", reason="Bash specific syntax used for tests"
)


def text_strategy() -> SearchStrategy[str]:
    return strategies.text(alphabet=string.ascii_letters)


@given(message=text_strategy())
def test_capture_output(message: str) -> None:
    assert cli.capture_output("printf", "%s", message) == message


@given(message=text_strategy())
def test_capture_output_lines(message: str) -> None:
    assert cli.capture_output_lines("printf", "%s", message) == message.splitlines()


@settings(deadline=1000)
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
    assert cli.capture_return_code("exit", return_code, shell=True) == return_code


@given(return_code=strategies.integers(min_value=0, max_value=255))
@linux_only_test
def test_completes_successfully(return_code: int) -> None:
    success = return_code == 0
    assert cli.completes_successfully("exit", return_code, shell=True) == success


@linux_only_test
def test_exception_handling() -> None:
    with pytest.raises(cli.CalledProcessError):
        cli.run("exit 1", shell=True)


def test_command_not_found_exception_handling() -> None:
    with pytest.raises(FileNotFoundError):
        cli.run("non_existing_command")


def test_command_and_argument_combination() -> None:
    cli.run("ls -l", "-a")


def test_run_commands() -> None:
    commands = ("ls", "pwd")
    cli.run_commands(*commands)


def test_cwd() -> None:
    with Path.tempdir() as folder:
        extracted_folder_name = cli.capture_output("pwd", cwd=folder).split("/")[-1]
    assert extracted_folder_name == folder.name


@given(value=text_strategy())
@linux_only_test
def test_extra_subprocess_kwarg(value: str) -> None:
    env = {"name": value}
    assert cli.capture_output("echo", "$name", shell=True, env=env) == value
