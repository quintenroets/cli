import os
import sys

UP = "\x1B[1A"
CLR = "\x1B[0K"
NEWLINE = "\n"
CLR_N = f"{CLR}{NEWLINE}"


class Message:
    def __init__(self, message=None):
        self._message = message

    def show(self, message):
        message = message.strip()
        sys.stdout.write(f"{self.header}{message.replace(NEWLINE, CLR_N)}{CLR_N}")
        self._message = message

    @property
    def message_length(self):
        width = os.get_terminal_size().columns
        length = (
            sum([((len(line) - 1) // width) + 1 for line in self._message.split("\n")])
            if self._message
            else 0
        )
        return length

    @property
    def header(self):
        if sys.stdout.isatty():
            l = self.message_length
            header = f"{UP * l}{CLR_N * l}{UP * l}"
        else:
            header = ""
        return header

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        if message is not None:
            self.show(message)

    def __enter__(self):
        message = self._message
        self._message = None
        self.message = message
        return self

    def __exit__(self, *_):
        print(self.header, end="")
