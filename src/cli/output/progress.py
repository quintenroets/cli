from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from rich.progress import Progress


T = TypeVar("T")


@dataclass
class ProgressManager:
    number_of_active_progress_tracks = 0

    @cached_property
    def progress(self) -> Progress:
        from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn

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
        return Progress(*columns)


progress_manager = ProgressManager()


def track_progress(
    sequence: Iterable[T],
    description: str = "",
    unit: str = "item",
    total: int | None = None,
    cleanup_after_finish: bool = False,
    # cleanup_after_finish makes completed progressbar appear twice
) -> Iterable[T]:
    progress = progress_manager.progress
    progress.__enter__()

    task_id = progress.add_task(description=description, unit=unit)
    progress_manager.number_of_active_progress_tracks += 1
    yield from progress.track(sequence, total, task_id, description)
    progress_manager.number_of_active_progress_tracks -= 1
    if cleanup_after_finish and progress_manager.number_of_active_progress_tracks == 0:
        progress.__exit__(None, None, None)
