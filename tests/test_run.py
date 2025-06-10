import subprocess
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given
from superpathlib import Path

import cli
from cli.output.console import set_title

from .test_runner import linux_only_test, text_strategy


@linux_only_test
def test_exception_handling() -> None:
    with pytest.raises(cli.CalledProcessError):
        cli.run("exit 1", shell=True)  # noqa: S604


@linux_only_test
def test_non_verbose_exception_handling() -> None:
    with pytest.raises(subprocess.CalledProcessError):
        cli.run("exit 1", shell=True, verbose_errors=False)  # noqa: S604


def test_command_not_found_exception_handling() -> None:
    with pytest.raises(FileNotFoundError):
        cli.run("non_existing_command")


def test_command_and_argument_combination() -> None:
    cli.run("ls -l", "-a")


def test_cwd() -> None:
    with Path.tempdir() as folder:
        extracted_folder_name = cli.capture_output("pwd", cwd=folder).split("/")[-1]
    assert extracted_folder_name == folder.name


@given(value=text_strategy())
@linux_only_test
def test_extra_subprocess_kwarg(value: str) -> None:
    env = {"name": value}
    assert cli.capture_output("echo", "$name", shell=True, env=env) == value  # noqa: S604


def test_set_parsing() -> None:
    commands = "python", {"version"}
    cli.run(*commands)


def test_iterator_parsing() -> None:
    commands = ("python", iter(["--version"]))
    cli.run(*commands)


def test_dict_parsing() -> None:
    commands = "git", {"work-tree": "."}, "status"
    cli.run(*commands)


@patch("subprocess.run")
def test_title(mocked_popen: MagicMock) -> None:
    cli.run("ls", title="ls", console=True)
    mocked_popen.assert_called_once()


def test_set_title() -> None:
    set_title(title="ls")


def test_sudo() -> None:
    cli.run("sudo ls")


def test_root() -> None:
    cli.run("ls", root=True)


def test_root_in_shell() -> None:
    cli.run("ls", root=True, shell=True)  # noqa: S604
