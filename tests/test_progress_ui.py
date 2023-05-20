import time

import pytest

import cli

SLEEP_INTERVAL = 0.01
ITERATIONS = 200


def sleep():
    time.sleep(SLEEP_INTERVAL)


@pytest.mark.skip(reason="requires manual inspection")
def test_progress():
    items = cli.progress(range(ITERATIONS), description="counting", unit="items")
    for i in items:
        sleep()


@pytest.mark.skip(reason="requires manual inspection")
def test_progress_with_cleanup():
    items = cli.progress(range(ITERATIONS), description="counting", unit="items")
    for i in items:
        sleep()


@pytest.mark.skip(reason="requires manual inspection")
def test_progress_double():
    for i in cli.progress(range(ITERATIONS), description="outer loop", unit="items"):
        sleep()
        if i == 4:
            for j in cli.progress(range(ITERATIONS), description="inner loop"):
                sleep()


@pytest.mark.skip(reason="requires manual inspection")
def test_progress_with_status():
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
