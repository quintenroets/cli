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
    assert trace_imports("cli") - trace_imports("sys") <= {"__future__", "cli"}


def trace_imports(module: str) -> set[str]:
    script = f"import sys, {module}; print(*sys.modules)"
    output = cli.capture_output(sys.executable, "-c", script)
    return {name.partition(".")[0] for name in output.split()}
