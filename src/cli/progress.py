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
    task_id = progress.add_task(description=description, unit=unit)
    try:
        yield from progress.track(sequence, total=total, task_id=task_id)
    finally:
        progress.stop_task(task_id)
        if all(task.stop_time is not None for task in progress.tasks):
            progress.stop()
            for task in progress.tasks:
                progress.remove_task(task.id)


@cache
def create_progress() -> Progress:
    from rich import progress  # noqa: PLC0415

    count_format = (
        "[progress.completed]{task.completed}/[progress.total]"
        "{task.total:>0.0f} {task.fields[unit]}"
    )
    columns = (
        progress.TextColumn("[progress.description]{task.description}"),
        progress.TextColumn(count_format),
        progress.BarColumn(bar_width=None),
        progress.TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        progress.TimeRemainingColumn(),
    )
    display = progress.Progress(*columns)
    atexit.register(display.stop)
    return display
