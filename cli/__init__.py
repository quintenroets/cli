import readline  # correctly handle arrow keys when asking user input

import rich

from .input_interface import ask, confirm, prompt
from .install import get_install_command, install
from .output_interface import Message as message
from .progress import progress
from .run import get, lines, run, run_commands, sh, start, urlopen
from .status import status


class Proxy:
    def __init__(self, handler):
        self.__handler = handler

    def __getattr__(self, name):
        return self.__handler().__getattribute__(name)


console = Proxy(rich.get_console)  # increase startup performance
