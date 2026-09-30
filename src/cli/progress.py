from __future__ import annotations

import atexit
from functools import cache
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from rich.progress import Progress


T = TypeVar("T")


def track_progress(
    sequence: Iterable[T],
    description: str = "",
    unit: str = "item",
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
    from rich.progress import (  # noqa: PLC0415
        BarColumn,
        Progress,
        TextColumn,
        TimeRemainingColumn,
    )

    count_format = (
        "[progress.completed]{task.completed}/[progress.total]"
        "{task.total:>0.0f} {task.fields[unit]}"
    )
    columns = (
        TextColumn("[progress.description]{task.description}"),
        TextColumn(count_format),
        BarColumn(bar_width=1000),  # shrinks depending on other columns
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
    )
    progress = Progress(*columns)
    atexit.register(progress.stop)
    return progress
