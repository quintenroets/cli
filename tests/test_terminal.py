from unittest.mock import MagicMock, patch

import rich
from rich.prompt import Confirm, Prompt

import cli

word = "hello"


@patch.object(Prompt, "ask")
def test_prompt(mocked_ask: MagicMock) -> None:
    cli.prompt(word)
    mocked_ask.assert_called_once()


@patch.object(Confirm, "ask")
def test_confirm(mocked_confirm: MagicMock) -> None:
    cli.confirm(word)
    mocked_confirm.assert_called_once()


def test_console_is_rich_console() -> None:
    assert cli.console is rich.get_console()


def test_unknown_attribute_is_missing() -> None:
    assert not hasattr(cli, "unknown")
