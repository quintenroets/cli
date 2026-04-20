import os

from .commands import StringLike
from .run import launch
import platform


def open_urls(*urls: StringLike) -> None:
    for url in urls:
        if os.name == "nt":
            os.startfile(url)  # type: ignore[attr-defined] # noqa: S606 # pragma: nocover
        elif platform.system() == "Linux":
            launch("xdg-open", url)
        else:
            launch("open", url)
