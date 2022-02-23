import time

import cli


def test_progress():
    items = cli.progress(range(200), description="counting", unit="items")
    for i in items:
        time.sleep(0.01)


def test_progress_double():
    for i in cli.progress(range(10), description="outer loop", unit="items"):
        time.sleep(0.1)
        if i == 4:
            for j in cli.progress(range(10), description="inner loop"):
                time.sleep(0.1)


test_progress()
test_progress_double()
