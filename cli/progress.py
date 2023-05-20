import sys


def get_progress():
    from rich.progress import TimeRemainingColumn  # noqa: autoimport
    from rich.progress import BarColumn, Progress, TextColumn  # noqa: autoimport

    columns = [TextColumn("[progress.description]{task.description}")]

    column_message = (
        "[progress.completed]{task.completed}/[progress.total]"
        "{task.total:>0.0f} {task.fields[unit]}"
    )
    columns.extend(
        (
            TextColumn(column_message),
            BarColumn(bar_width=1000),  # shrinks depending on other columns
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        )
    )
    return Progress(*columns)


class ProgressManager:
    _prog = None
    busy_amount = 0

    @classmethod
    @property
    def prog(cls):
        if cls._prog is None:
            cls._prog = get_progress()
        return cls._prog


def progress(sequence, description="", unit="it", total=None, cleanup=False):
    # classmethod properties require python 3.9
    prog = ProgressManager.prog() if sys.version_info < (3, 9) else ProgressManager.prog
    prog.__enter__()

    task_id = prog.add_task(description=description, unit=unit)
    ProgressManager.busy_amount += 1
    yield from prog.track(sequence, total, task_id, description)
    ProgressManager.busy_amount -= 1
    # cleanup False by default because it makes completed progressbar appear twice
    if ProgressManager.busy_amount == 0 and cleanup:
        prog.__exit__(None, None, None)
