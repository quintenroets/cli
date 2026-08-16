import subprocess
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given
from superpathlib import Path

import cli
from cli.commands.commands import CommandPreparer
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


@patch("sys.platform", "linux")
@patch.dict("os.environ", {"CMUX_TAB_ID": ""})
@patch("subprocess.run")
def test_title_linux(mocked_popen: MagicMock) -> None:
    cli.run("ls", title="ls", new_tab=True)
    mocked_popen.assert_called_once()


@patch("sys.platform", "darwin")
@patch.dict("os.environ", {"CMUX_TAB_ID": ""})
@patch("subprocess.run")
def test_new_tab_mac(mocked_popen: MagicMock) -> None:
    cli.run("ls", title="ls", new_tab=True)
    mocked_popen.assert_called_once()


@patch("sys.platform", "darwin")
@patch.dict("os.environ", {"CMUX_TAB_ID": "", "TERM_PROGRAM": "iTerm.app"})
@patch("subprocess.run")
def test_new_tab_mac_iterm(mocked_popen: MagicMock) -> None:
    cli.run("ls", new_tab=True)
    mocked_popen.assert_called_once()


@patch.dict("os.environ", {"CMUX_TAB_ID": "tab-id"})
@patch("subprocess.run")
def test_new_tab_cmux(mocked_popen: MagicMock) -> None:
    cli.run("ls", title="ls", new_tab=True)
    mocked_popen.assert_called_once()


def test_set_title() -> None:
    set_title(title="ls")


def test_sudo() -> None:
    cli.run("sudo ls")


@pytest.mark.parametrize("askpass_is_available", [False, True])
@pytest.mark.parametrize("shell", [False, True])
def test_root(*, shell: bool, askpass_is_available: bool) -> None:
    with patch.object(
        CommandPreparer,
        "askpass_is_available",
        new=askpass_is_available,
    ):
        cli.run("ls", root=True, shell=shell)
