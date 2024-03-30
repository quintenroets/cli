import os

from .run import launch


def open_urls(*urls: str) -> None:
    for url in urls:
        if os.name == "nt":
            os.startfile(url)  # type: ignore[attr-defined]
        else:
            launch("xdg-open", url)
