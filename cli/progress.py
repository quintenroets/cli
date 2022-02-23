def get_progress():
    from rich.progress import TextColumn  # lazy imports
    from rich.progress import BarColumn, Progress, TimeRemainingColumn

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
    busy_ids = []

    @classmethod
    @property
    def prog(cls):
        if cls._prog is None:
            cls._prog = get_progress()
        return cls._prog


def progress(sequence, description="", unit="it", total=None):
    ProgressManager.prog.__enter__()
    task_id = ProgressManager.prog.add_task(description=description, unit=unit)
    ProgressManager.busy_ids.append(task_id)
    yield from ProgressManager.prog.track(sequence, total, task_id, description)
    ProgressManager.busy_ids.remove(task_id)
    if not ProgressManager.busy_ids:
        ProgressManager.prog.__exit__(None, None, None)
