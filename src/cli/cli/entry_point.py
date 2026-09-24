import sys

import cli


def run_in_new_tab() -> None:
    cli.run_in_new_tab(sys.argv[1:])
