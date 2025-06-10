from unittest.mock import MagicMock, patch

from rich.prompt import Confirm, Prompt

import cli

word = "hello"


@patch("builtins.input")
def test_ask(mocked_input: MagicMock) -> None:
    cli.ask(word)
    mocked_input.assert_called_once()


@patch.object(Prompt, "ask")
def test_prompt(mocked_ask: MagicMock) -> None:
    cli.prompt(word)
    mocked_ask.assert_called_once()


@patch.object(Confirm, "ask")
def test_confirm(mocked_confirm: MagicMock) -> None:
    cli.confirm(word)
    mocked_confirm.assert_called_once()
