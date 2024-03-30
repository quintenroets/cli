import shlex
import sys

import cli


def entry_point() -> None:
    command = shlex.join(sys.argv[1:])
    cli.run_in_console(command)
