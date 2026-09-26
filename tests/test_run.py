import subprocess
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given
from superpathlib import Path

import cli
from cli.commands.commands import CommandItem

from .test_runner import linux_only_test, text_strategy


@linux_only_test
def test_exception_handling() -> None:
    with pytest.raises(subprocess.CalledProcessError) as info:
        cli.capture_output("echo error >&2; exit 1", shell=True)  # noqa: S604
    assert info.value.returncode == 1
    assert info.value.stderr == "error\n"


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


@pytest.mark.parametrize(
    ("items", "expected"),
    [
        (("python", {"version"}), ("python", "--version")),
        (("python", iter(["--version"])), ("python", "--version")),
        (("git", {"work-tree": "."}, "status"), ("git", "--work-tree", ".", "status")),
    ],
)
@patch("subprocess.run")
def test_parsing(
    mocked_run: MagicMock,
    items: tuple[CommandItem, ...],
    expected: tuple[str, ...],
) -> None:
    cli.run(*items)
    assert mocked_run.call_args.args[0] == expected


@pytest.mark.parametrize("shell", [False, True])
def test_root(*, shell: bool) -> None:
    cli.run("ls", root=True, shell=shell)
