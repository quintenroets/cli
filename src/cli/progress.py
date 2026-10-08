from __future__ import annotations

import atexit
from functools import cache
from itertools import chain
from operator import length_hint
from time import perf_counter

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from typing import TypeVar

    from rich.progress import Progress, TaskID

    T = TypeVar("T")


def track_progress(
    items: Iterable[T],
    description: str = "",
    unit: str = "items",
    total: int | None = None,
    *,
    show_after: float = 0.2,
) -> Iterator[T]:
    if total is None:
        total = length_hint(items) or None
    remaining = iter(items)
    deadline = perf_counter() + show_after
    for completed, item in enumerate(remaining):
        if perf_counter() < deadline:
            yield item
        else:
            task_id = create_progress().add_task(description, total=total, unit=unit)
            yield from track_task(task_id, chain([item], remaining), completed)


def track_task(task_id: TaskID, items: Iterator[T], completed: int) -> Iterator[T]:
    progress = create_progress()
    progress.start()
    try:
        task = next(task for task in progress.tasks if task.id == task_id)
        yield from progress.track(items, task.total, completed, task_id)
        progress.update(task_id, total=task.completed + completed)
    finally:
        progress.advance(task_id, completed)  # track drops starting offset on exit
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
