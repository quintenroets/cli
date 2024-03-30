from __future__ import annotations

import os
import sys
from typing import Any

UP = "\x1b[1A"
CLR = "\x1b[0K"
NEWLINE = "\n"
CLR_N = f"{CLR}{NEWLINE}"


class Message:
    def __init__(self, message: str | None = None) -> None:
        self._message = message

    def show(self, message: str) -> None:
        message = message.strip()
        sys.stdout.write(f"{self.header}{message.replace(NEWLINE, CLR_N)}{CLR_N}")
        self._message = message

    @property
    def message_length(self) -> int:
        width = os.get_terminal_size().columns
        length = (
            sum([((len(line) - 1) // width) + 1 for line in self._message.split("\n")])
            if self._message
            else 0
        )
        return length

    @property
    def header(self) -> str:
        return self.create_header() if sys.stdout.isatty() else ""

    def create_header(self) -> str:
        length = self.message_length
        return f"{UP * length}{CLR_N * length}{UP * length}"

    @property
    def message(self) -> str | None:
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        if message is not None:
            self.show(message)

    def __enter__(self) -> Message:
        message = self._message
        self._message = None
        self.message = message
        return self

    def __exit__(self, *_: Any) -> None:
        print(self.header, end="")
