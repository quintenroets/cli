from __future__ import annotations

from typing import TYPE_CHECKING

import rich

from .exceptions import CalledProcessError
from .input_interface import ask, confirm, prompt
from .install import get_install_command, install
from .output_interface import Message as message
from .progress import ProgressManager, progress
from .run import (
    get,
    is_success,
    lines,
    pipe,
    prepare_args,
    return_code,
    run,
    run_commands,
    set_title,
    sh,
    start,
    urlopen,
)
from .status import status

if TYPE_CHECKING:
    from rich.console import Console

try:
    import readline

    # correctly handle arrow keys when asking user input
except ModuleNotFoundError:
    pass  # not available on Windows


class Proxy:
    def __init__(self, handler):
        self.__handler = handler

    def __getattr__(self, name):
        return self.__handler().__getattribute__(name)


console: Console = Proxy(rich.get_console)  # increase startup performance
