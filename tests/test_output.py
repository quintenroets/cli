from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from cli.output.message import Message

from .test_progress import ITERATIONS


@pytest.fixture
def message() -> Iterator[Message]:
    message = Message("hello")
    with message:
        yield message


def test_message(message: Message) -> None:
    for i in range(ITERATIONS):
        message.message = str(i)


@patch("os.get_terminal_size")
def test_create_header(mocked_terminal_size: MagicMock, message: Message) -> None:
    mocked_terminal_size.columns = 100
    message.create_header()


def test_extract_message(message: Message) -> None:
    assert message.message
