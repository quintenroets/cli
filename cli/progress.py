import sys


def get_progress():
    from rich.progress import TextColumn  # noqa: autoimport
    from rich.progress import (BarColumn, Progress,  # noqa: autoimport
                               TimeRemainingColumn)

    columns = [TextColumn("[progress.description]{task.description}")]
    columns.extend(
        (
            TextColumn(
                "[progress.completed]{task.completed}/[progress.total]{task.total:>0.0f} {task.fields[unit]}"
            ),
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


def progress(sequence, description="", unit="it", total=None):
    # classmethod properties require python 3.9
    prog = ProgressManager.prog() if sys.version_info < (3, 9) else ProgressManager.prog
    prog.__enter__()

    task_id = prog.add_task(description=description, unit=unit)
    ProgressManager.busy_amount += 1
    yield from prog.track(sequence, total, task_id, description)
    ProgressManager.busy_amount -= 1
    if ProgressManager.busy_amount == 0:
        pass  # prog.__exit__(None, None, None)  # disable for now to fix issue of progress appearing twice
