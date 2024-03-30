from typing import Any

try:
    import readline  # noqa: F401

    # correctly handle arrow keys when asking user input
except ModuleNotFoundError:
    pass  # not available on Windows


def ask(question: str) -> str:
    print(question, end=" ")
    return input().lower().strip()


def prompt(*args: Any, **kwargs: Any) -> str:
    from rich.prompt import Prompt

    return Prompt.ask(*args, **kwargs)


def confirm(*args: Any, **kwargs: Any) -> bool:
    from rich.prompt import Confirm

    return Confirm.ask(*args, **kwargs)
