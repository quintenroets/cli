from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from cli.output.message import CLR_N, UP, Message


@pytest.fixture
def message() -> Iterator[Message]:
    message = Message("hello")
    with message:
        yield message


def test_shown_message_is_stored(message: Message) -> None:
    assert message.message == "hello"


@patch("os.get_terminal_size")
def test_header_clears_each_wrapped_line(
    mocked_terminal_size: MagicMock,
    message: Message,
) -> None:
    mocked_terminal_size.return_value.columns = 4
    message.message = "hello\nworld"
    wrapped_lines = 4  # two lines of five characters, each spanning two terminal lines
    header = f"{UP * wrapped_lines}{CLR_N * wrapped_lines}{UP * wrapped_lines}"
    assert message.create_header() == header
