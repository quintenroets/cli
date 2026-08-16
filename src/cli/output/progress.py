from __future__ import annotations

from itertools import chain, islice
from operator import length_hint
from time import perf_counter
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator  # pragma: nocover


T = TypeVar("T")

# rich.progress costs ~12 ms to import — more than a short run takes end to end — so
# the bar has to outlast this delay before it is worth building
progress_bar_delay = 0.2


def track_progress(  # noqa: PLR0913
    sequence: Iterable[T],
    description: str = "",
    unit: str = "item",
    total: int | None = None,
    *,
    cleanup_after_finish: bool = False,
    # cleanup_after_finish makes completed progressbar appear twice
    delay: float = progress_bar_delay,
) -> Iterator[T]:
    if total is None:
        total = length_hint(sequence) or None
    iterator = iter(sequence)
    deadline = perf_counter() + delay
    completed = 0
    pending = take_next(iterator)
    # yielding inside the loop hands time back, so the delay covers the consumer too
    while pending and perf_counter() < deadline:
        yield from pending
        completed += 1
        pending = take_next(iterator)
    if pending:
        # deferred so that runs finishing before the deadline never import rich
        from .bar import start_bar  # noqa: PLC0415

        # tracking stays in this generator: a delegated one costs more per item
        # than the counting itself, and the bar already resumes at the count above
        with start_bar(
            description,
            unit,
            total=total,
            completed=completed,
            cleanup_after_finish=cleanup_after_finish,
        ) as counter:
            for item in chain(pending, iterator):
                yield item
                counter.completed += 1


def take_next(iterator: Iterator[T]) -> list[T]:
    return list(islice(iterator, 1))
