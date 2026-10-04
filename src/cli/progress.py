from __future__ import annotations

import atexit
from functools import cache

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from typing import TypeVar

    from rich.progress import Progress

    T = TypeVar("T")


def track_progress(
    sequence: Iterable[T],
    description: str = "",
    unit: str = "items",
    total: int | None = None,
) -> Iterator[T]:
    progress = create_progress()
    progress.start()
    task_id = progress.add_task(description=description, total=total, unit=unit)
    try:
        yield from progress.track(sequence, total=total, task_id=task_id)
        task = next(task for task in progress.tasks if task.id == task_id)
        progress.update(task_id, total=task.completed)
    finally:
        progress.stop_task(task_id)
        if all(task.stop_time is not None for task in progress.tasks):
            progress.stop()
            for task in progress.tasks:
                progress.remove_task(task.id)


@cache
def create_progress() -> Progress:
    from rich import progress  # noqa: PLC0415

    columns = (
        progress.TextColumn("[progress.description]{task.description}"),
        progress.MofNCompleteColumn(),
        progress.TextColumn("{task.fields[unit]}"),
        progress.BarColumn(bar_width=None),
        progress.TaskProgressColumn(),
        progress.TimeRemainingColumn(),
    )
    display = progress.Progress(*columns)
    atexit.register(display.stop)
    return display
