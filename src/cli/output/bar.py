from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import Event, Thread
from typing import TYPE_CHECKING

from rich.progress import (
    BarColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
)

if TYPE_CHECKING:
    from collections.abc import Iterator  # pragma: nocover


# publishing takes a lock and resamples the speed estimate, so a thread batches it
# instead of the tracking loop, which then costs one counter increment per item
progress_bar_update_period = 0.1


def create_progress() -> Progress:
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


@dataclass
class ProgressManager:
    progress: Progress = field(default_factory=create_progress)
    active_bars: int = 0


progress_manager = ProgressManager()


@contextmanager
def start_bar(
    description: str,
    unit: str,
    total: int | None,
    completed: int,
    *,
    cleanup_after_finish: bool,
) -> Iterator[TaskCounter]:
    progress = progress_manager.progress
    progress.start()

    task_id = progress.add_task(
        description=description,
        unit=unit,
        total=total,
        completed=completed,
    )
    progress_manager.active_bars += 1
    try:
        with TaskCounter(progress, task_id, completed=completed) as counter:
            yield counter
    finally:
        progress_manager.active_bars -= 1
        if cleanup_after_finish and progress_manager.active_bars == 0:
            progress.stop()


@dataclass(slots=True)
class TaskCounter:
    progress: Progress
    task_id: TaskID
    completed: int = 0
    done: Event = field(default_factory=Event)
    thread: Thread = field(init=False)

    def __post_init__(self) -> None:
        self.thread = Thread(target=self.publish_periodically, daemon=True)

    def __enter__(self) -> TaskCounter:  # noqa: PYI034
        self.thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.done.set()
        self.thread.join()
        self.publish()

    def publish_periodically(self) -> None:
        while not self.done.wait(progress_bar_update_period):
            self.publish()

    def publish(self) -> None:
        self.progress.update(self.task_id, completed=self.completed)
