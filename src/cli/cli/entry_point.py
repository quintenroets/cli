import shlex
import sys

import cli


def run_in_new_tab() -> None:
    command = shlex.join(sys.argv[1:])
    cli.run_in_new_tab(command)
