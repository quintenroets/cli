from typing import Any

import cli
from hypothesis import given, strategies
from hypothesis.strategies import SearchStrategy


def text_strategy(**kwargs: Any) -> SearchStrategy[str]:
    alphabet = strategies.characters(blacklist_categories=["Cc", "Cs", "Zs"], **kwargs)
    return strategies.text(alphabet=alphabet)


@given(message=text_strategy())
def test_capture_output(message: str) -> None:
    assert cli.capture_output("printf", "%s", message) == message


@given(message=text_strategy())
def test_capture_output_lines(message: str) -> None:
    assert cli.capture_output_lines("printf", "%s", message) == message.splitlines()


@given(message=text_strategy())
def test_pipe_output_and_capture(message: str) -> None:
    commands = (
        ("printf", "%s", message),
        ("grep", "-F", "--", message),
    )
    assert cli.pipe_output_and_capture(commands, check=False) == message


@given(return_code=strategies.integers(min_value=0, max_value=255))
def test_capture_return_code(return_code: int) -> None:
    assert cli.capture_return_code("exit", return_code, shell=True) == return_code
