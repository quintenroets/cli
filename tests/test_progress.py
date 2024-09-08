import time
from collections.abc import Iterable

import pytest

import cli

SLEEP_INTERVAL = 0.01
ITERATIONS = 200


# Best to inspect these tests manually


@pytest.fixture
def sequence() -> range:
    return range(ITERATIONS)


@pytest.fixture
def tracked_sequence(sequence: range) -> Iterable[int]:
    return cli.track_progress(sequence, description="counting", unit="items")


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
    )
    for _ in items:
        sleep()


def test_nested_progress(tracked_sequence: Iterable[int], sequence: range) -> None:
    for i in tracked_sequence:
        sleep()
        if i == ITERATIONS / 2:
            for _ in cli.track_progress(sequence, description="inner loop"):
                sleep()


def test_progress_with_status(tracked_sequence: Iterable[int]) -> None:
    for _ in tracked_sequence:
        sleep()
        with cli.status("waiting"):
            sleep()

    with cli.status("waiting"):
        sleep()
