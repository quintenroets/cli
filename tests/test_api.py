import os
import string

import cli
import pytest
from hypothesis import given, settings, strategies
from hypothesis.strategies import SearchStrategy

linux_only_test = pytest.mark.skipif(
    os.name == "posix", reason="Bash specific syntax used for tests"
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
