from collections.abc import Iterable
from itertools import count
from unittest.mock import patch

import pytest

import cli
from cli.progress import create_progress

from .test_cli import capture_imports

progress = create_progress()


def test_nesting() -> None:
    for _ in cli.track_progress(range(1), show_after=0):
        list(cli.track_progress(range(1), show_after=0))
        assert progress.live.is_started
    assert not progress.live.is_started


@pytest.mark.parametrize(("items", "total"), [([0, 1], 2), ((i for i in [0, 1]), None)])
def test_total(items: Iterable[int], total: int | None) -> None:
    with patch("cli.progress.perf_counter", count().__next__):
        for _ in cli.track_progress(items, show_after=2):
            if progress.tasks:
                (task,) = progress.tasks
                assert task.total == total
    assert task.completed == task.total == 2  # noqa: PLR2004


def test_fast_skips_rich() -> None:
    assert "rich" not in capture_imports("import cli; list(cli.track_progress([0]))")
