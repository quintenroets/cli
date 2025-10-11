import contextlib
from unittest.mock import MagicMock, patch

from package_dev_utils.tests.args import cli_args

from cli import cli


@patch("subprocess.Popen")
@cli_args("ls")
def test_entry_point(mocked_popen: MagicMock) -> None:
    with contextlib.suppress(FileNotFoundError):
        cli.entry_point()
    mocked_popen.assert_called_once()
