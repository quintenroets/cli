from __future__ import annotations

import atexit
from functools import cached_property
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator  # pragma: nocover

    from rich.progress import Progress  # pragma: nocover


T = TypeVar("T")


class ProgressManager:
    @cached_property
    def progress(self) -> Progress:
        from rich.progress import (  # noqa: PLC0415
            BarColumn,
            Progress,
            TextColumn,
            TimeRemainingColumn,
        )

        column_message = (
            "[progress.completed]{task.completed}/[progress.total]"
            "{task.total:>0.0f} {task.fields[unit]}"
        )
        columns = [
            TextColumn("[progress.description]{task.description}"),
            TextColumn(column_message),
            BarColumn(bar_width=1000),  # shrinks depending on other columns
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        ]
        progress = Progress(*columns)
        atexit.register(progress.stop)
        return progress


progress_manager = ProgressManager()


def track_progress(
    sequence: Iterable[T],
    description: str = "",
    unit: str = "item",
    total: int | None = None,
) -> Iterator[T]:
    progress = progress_manager.progress
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
