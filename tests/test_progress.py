import time
from collections.abc import Iterable, Iterator
from unittest.mock import patch

import pytest

import cli
from cli.output.bar import progress_manager

SLEEP_INTERVAL = 0.01
ITERATIONS = 20


# Best to inspect these tests manually


@pytest.fixture
def sequence() -> range:
    return range(ITERATIONS)


@pytest.fixture
def tracked_sequence(sequence: range) -> Iterable[int]:
    # the delay is covered by the tests below, so the bar can show up right away
    return cli.track_progress(sequence, description="counting", unit="items", delay=0)


def sleep() -> None:
    time.sleep(SLEEP_INTERVAL)


def test_progress(tracked_sequence: Iterable[int]) -> None:
    for _ in tracked_sequence:
        sleep()


def test_progress_with_cleanup(sequence: range) -> None:
    items = cli.track_progress(
        sequence,
        description="counting",
        unit="items",
        cleanup_after_finish=True,
        delay=0,
    )
    for _ in items:
        sleep()


def test_progress_with_status(tracked_sequence: Iterable[int]) -> None:
    for _ in tracked_sequence:
        sleep()
        with cli.status("waiting"):
            sleep()

    with cli.status("waiting"):
        sleep()


def generate_slowly(sequence: range) -> Iterator[int]:
    for item in sequence:
        sleep()
        yield item


def test_fast_sequence_skips_the_progress_bar(sequence: range) -> None:
    items = cli.track_progress(sequence)
    with patch("cli.output.bar.start_bar") as start_bar:
        assert list(items) == list(sequence)
    start_bar.assert_not_called()


def test_slow_consumer_gets_a_progress_bar(sequence: range) -> None:
    """The delay is wall clock, so time spent consuming counts towards it too."""
    items = cli.track_progress(sequence, delay=SLEEP_INTERVAL)
    with patch("cli.output.bar.start_bar") as start_bar:
        for _ in items:
            sleep()
    start_bar.assert_called_once()


def test_bar_resumes_at_the_items_already_yielded(sequence: range) -> None:
    """
    Items yielded before the bar appears never reach it, so it starts at their count.

    A bar starting from zero would stay short of its total for the whole run.
    """
    items = cli.track_progress(
        generate_slowly(sequence),
        total=ITERATIONS,
        delay=SLEEP_INTERVAL,
    )
    assert list(items) == list(sequence)

    task = progress_manager.progress.tasks[-1]
    assert task.completed == ITERATIONS
    assert task.finished


def test_items_are_not_withheld_during_the_delay(sequence: range) -> None:
    """Nothing may be buffered: an item is yielded as soon as it is produced."""
    items = cli.track_progress(generate_slowly(sequence), delay=SLEEP_INTERVAL * 5)
    assert next(items) == sequence[0]
