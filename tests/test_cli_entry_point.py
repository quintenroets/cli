import contextlib

from cli import cli
from package_dev_utils.tests.args import cli_args


@cli_args("ls")
def test_entry_point() -> None:
    with contextlib.suppress(FileNotFoundError):
        cli.entry_point()
