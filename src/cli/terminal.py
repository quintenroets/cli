from __future__ import annotations

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any  # pragma: nocover

    from rich.console import Console  # pragma: nocover
    from rich.prompt import Confirm, Prompt  # pragma: nocover

    from . import progress  # pragma: nocover

    console: Console  # pragma: nocover
    prompt = Prompt.ask  # pragma: nocover
    confirm = Confirm.ask  # pragma: nocover
    track_progress = progress.track_progress  # pragma: nocover
else:

    def __getattr__(name: str) -> Any:
        match name:
            case "console":
                from rich import get_console  # noqa: PLC0415

                return get_console()
            case "prompt":
                from rich.prompt import Prompt  # noqa: PLC0415

                enable_line_editing()
                return Prompt.ask
            case "confirm":
                from rich.prompt import Confirm  # noqa: PLC0415

                enable_line_editing()
                return Confirm.ask
            case "track_progress":
                from .progress import track_progress  # noqa: PLC0415

                return track_progress
            case _:
                raise AttributeError(name)


def enable_line_editing() -> None:
    import contextlib  # noqa: PLC0415

    with contextlib.suppress(ModuleNotFoundError):  # not available on Windows
        import readline  # noqa: F401, PLC0415
