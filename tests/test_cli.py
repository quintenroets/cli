import sys

import rich
from rich.prompt import Confirm, Prompt

import cli
from cli.progress import create_progress


def test_terminal_attributes() -> None:
    assert cli.console is rich.get_console()
    assert cli.prompt == Prompt.ask
    assert cli.confirm == Confirm.ask
    assert not hasattr(cli, "unknown")


def test_progress() -> None:
    for _ in cli.track_progress(range(1)):
        list(cli.track_progress(range(1)))
        assert create_progress().live.is_started
    assert not create_progress().live.is_started


def test_progress_without_total() -> None:
    progress = create_progress()
    for _ in cli.track_progress(i for i in range(1)):
        (task,) = progress.tasks
        assert task.total is None
    assert task.completed == task.total == 1


def test_import_loads_no_dependencies() -> None:
    assert capture_imports("cli") - capture_imports("sys") <= {"__future__", "cli"}


def capture_imports(module: str) -> set[str]:
    script = f"import sys, {module}; print(*sys.modules)"
    output = cli.capture_output(sys.executable, "-c", script)
    return {name.partition(".")[0] for name in output.split()}
