try:
    import readline

    # correctly handle arrow keys when asking user input
except ModuleNotFoundError:
    pass  # not available on Windows

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.prompt import Confirm, Prompt


def ask(question: str) -> str:
    print(question, end=" ")
    return input().lower().strip()


def prompt(*args, **kwargs) -> Prompt:
    from rich.prompt import Prompt

    return Prompt.ask(*args, **kwargs)


def confirm(*args, **kwargs) -> Confirm:
    from rich.prompt import Confirm

    return Confirm.ask(*args, **kwargs)
