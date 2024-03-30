from cli import cli
from package_dev_utils.tests.args import no_cli_args


@no_cli_args
def test_entry_point() -> None:
    cli.entry_point()
