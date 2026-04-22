import contextlib
from unittest.mock import MagicMock, patch

from package_dev_utils.tests.args import cli_args

from cli import cli


@patch("subprocess.Popen")
@cli_args("ls")
def test_run_in_new_tab(mocked_popen: MagicMock) -> None:
    with contextlib.suppress(FileNotFoundError):
        cli.run_in_new_tab()
    mocked_popen.assert_called_once()
