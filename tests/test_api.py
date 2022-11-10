import pytest

import cli


@pytest.mark.parametrize("command, output", [("echo ja", "ja"), ("echo nee", "nee")])
def test_output(command, output):
    assert cli.get(command) == output


def test_return_code():
    for return_code in (0, 1):
        assert cli.return_code(f"bash -c 'exit {return_code}'") == return_code
