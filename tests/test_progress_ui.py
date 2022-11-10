import time

import pytest

import cli


@pytest.mark.skip(reason="requires manual inspection")
def test_progress():
    items = cli.progress(range(200), description="counting", unit="items")
    for i in items:
        time.sleep(0.01)


@pytest.mark.skip(reason="requires manual inspection")
def test_progress_double():
    for i in cli.progress(range(10), description="outer loop", unit="items"):
        time.sleep(0.1)
        if i == 4:
            for j in cli.progress(range(10), description="inner loop"):
                time.sleep(0.1)


@pytest.mark.skip(reason="requires manual inspection")
def test_progress_with_status():
    for i in cli.progress(range(10), "advance"):
        time.sleep(0.1)
        with cli.status("waiting"):
            time.sleep(0.1)

    with cli.status("waiting"):
        time.sleep(5)


if __name__ == "__main__":
    test_progress()
    test_progress_double()
    test_progress_with_status()
