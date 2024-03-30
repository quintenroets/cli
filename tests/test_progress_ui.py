import time

import cli
import pytest

SLEEP_INTERVAL = 0.01
ITERATIONS = 200


def sleep() -> None:
    time.sleep(SLEEP_INTERVAL)


@pytest.mark.skip(reason="requires manual inspection")
def test_progress() -> None:
    items = cli.progress(range(ITERATIONS), description="counting", unit="items")
    for i in items:
        sleep()


@pytest.mark.skip(reason="requires manual inspection")
def test_progress_with_cleanup() -> None:
    items = cli.progress(range(ITERATIONS), description="counting", unit="items")
    for i in items:
        sleep()


@pytest.mark.skip(reason="requires manual inspection")
def test_progress_double() -> None:
    for i in cli.progress(range(ITERATIONS), description="outer loop", unit="items"):
        sleep()
        if i == 4:
            for j in cli.progress(range(ITERATIONS), description="inner loop"):
                sleep()


@pytest.mark.skip(reason="requires manual inspection")
def test_progress_with_status() -> None:
    for i in cli.progress(range(ITERATIONS), "advance"):
        sleep()
        with cli.status("waiting"):
            sleep()

    with cli.status("waiting"):
        sleep()


if __name__ == "__main__":
    test_progress()
    test_progress_with_cleanup()
    test_progress_double()
    test_progress_with_status()
