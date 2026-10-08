import sys

import rich
from rich.prompt import Confirm, Prompt

import cli


def test_terminal_attributes() -> None:
    assert cli.console is rich.get_console()
    assert cli.prompt == Prompt.ask
    assert cli.confirm == Confirm.ask
    assert not hasattr(cli, "unknown")


def test_import_loads_no_dependencies() -> None:
    assert capture_imports("import cli") - capture_imports("") <= {"__future__", "cli"}


def capture_imports(code: str) -> set[str]:
    lines = "import sys", code, "print(*sys.modules)"
    output = cli.capture_output(sys.executable, "-c", "\n".join(lines))
    return {name.partition(".")[0] for name in output.split()}
