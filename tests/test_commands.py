import os
import string
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, settings, strategies
from hypothesis.strategies import SearchStrategy

import cli

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
    success = return_code == 0
    assert cli.completes_successfully("exit", return_code, shell=True) == success  # noqa: S604


def test_launch_commands() -> None:
    cli.launch_commands("ls")


def test_run_commands_in_shell() -> None:
    cli.run_commands_in_shell("ls")


def test_open() -> None:
    open_function = "os.startfile" if os.name == "nt" else "subprocess.Popen"
    with patch(open_function) as mocked_open:
        cli.open_urls("pwd")
        mocked_open.assert_called_once()


@linux_only_test
def test_exception_handling() -> None:
    with pytest.raises(subprocess.CalledProcessError) as info:
        cli.capture_output("echo error >&2; exit 1", shell=True)  # noqa: S604
    assert info.value.returncode == 1
    assert info.value.stderr == "error\n"


def test_cwd(tmp_path: Path) -> None:
    output = cli.capture_output("pwd", cwd=tmp_path)
    assert Path(output).name == tmp_path.name


@given(value=text_strategy())
@linux_only_test
def test_env(value: str) -> None:
    env = {"name": value}
    assert cli.capture_output("echo", "$name", shell=True, env=env) == value  # noqa: S604


@pytest.mark.parametrize(
    ("items", "expected"),
    [
        (("python", {"version"}), ("python", "--version")),
        (("python", iter(["--version"])), ("python", "--version")),
        (("git", {"work-tree": "."}, "status"), ("git", "--work-tree", ".", "status")),
        (("git status", 1), ("git", "status", "1")),
    ],
)
@patch("subprocess.run")
def test_parsing(
    mocked_run: MagicMock,
    items: tuple[object, ...],
    expected: tuple[str, ...],
) -> None:
    cli.run(*items)
    assert mocked_run.call_args.args[0] == expected


@patch("subprocess.Popen", autospec=True)
def test_root(mocked_popen: MagicMock) -> None:
    cli.launch("ls", root=True)
    if os.name == "posix":
        assert mocked_popen.call_args.args[0] == ("sudo", "ls")
