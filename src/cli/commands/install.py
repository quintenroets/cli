import platform
import shlex
import warnings
from collections.abc import Iterator

from .run import completes_successfully, run


def install(*packages: str, install_command: str | None = None) -> None:
    is_linux = platform.system() == "Linux"
    if is_linux:
        _install(*packages, install_command=install_command)
    else:
        message = "Required packages can only be installed on Linux"
        warnings.warn(message)


def _install(*packages: str, install_command: str | None = None) -> None:
    if install_command is None:
        install_command = next(extract_package_manager_command(), None)
    assert install_command is not None
    for package in packages:
        args = shlex.split(package)
        run(install_command, *args, root=True, check=False)


def extract_package_manager_command() -> Iterator[str]:
    commands = {"apt": "apt install -y", "pacman": "pacman -S --noconfirm"}
    for package_manager, command in commands.items():
        if completes_successfully("which", package_manager):
            yield command
