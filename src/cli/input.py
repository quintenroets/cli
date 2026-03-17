import contextlib
from typing import Any

with contextlib.suppress(ModuleNotFoundError):  # not available on Windows
    import readline  # noqa: F401

    # correctly handle arrow keys when asking user input


def ask(question: str) -> str:
    print(question, end=" ")  # noqa: T201
    return input().lower().strip()


def prompt(*args: Any, **kwargs: Any) -> str:
    from rich.prompt import Prompt  # noqa: PLC0415

    return Prompt.ask(*args, **kwargs)


def confirm(*args: Any, **kwargs: Any) -> bool:
    from rich.prompt import Confirm  # noqa: PLC0415

    return Confirm.ask(*args, **kwargs)
