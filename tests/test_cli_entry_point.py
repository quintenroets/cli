<<<<<<< HEAD
import contextlib
=======
from package_dev_utils.tests.args import no_cli_args
>>>>>>> template

from cli import cli
from package_dev_utils.tests.args import cli_args


@cli_args("ls")
def test_entry_point() -> None:
    with contextlib.suppress(FileNotFoundError):
        cli.entry_point()
