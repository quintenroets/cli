from .input_interface import ask
from .install import install, get_install_command
from .output_interface import Message as message
from .progress import progress
from .run import get, lines, run, run_commands, sh, start, urlopen

from rich import get_console

console = get_console()
