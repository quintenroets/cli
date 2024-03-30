from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from .rich import console

if TYPE_CHECKING:
    from rich.console import Status


def status(*args: Any, **kwargs: Any) -> Status | contextlib.nullcontext[None]:
    console.clear_live()
    use_status = not is_running_in_notebook()
    return console.status(*args, **kwargs) if use_status else contextlib.nullcontext()


def is_running_in_notebook() -> bool:
    try:
        get_ipython()  # type: ignore[name-defined]
    except NameError:
        in_notebook = False
    else:
        in_notebook = True
    return in_notebook
