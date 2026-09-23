import os
import sys

from .commands import StringLike
from .run import launch


def open_urls(*urls: StringLike) -> None:
    for url in urls:
        if os.name == "nt":
            os.startfile(url)  # type: ignore[attr-defined] # noqa: S606 # pragma: nocover
        else:
            command = "xdg-open" if sys.platform == "linux" else "open"
            launch(command, url)
