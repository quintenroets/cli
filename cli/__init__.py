from .input_interface import ask
from .install import install, get_install_command
from .output_interface import Message as message, Spinner as spinner
from .run import get, lines, run, run_commands, sh, start, urlopen

from rich.console import Console

console = Console()

status = console.status
