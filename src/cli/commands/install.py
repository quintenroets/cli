import platform
import shlex
import warnings

from . import is_success, run


def install(*packages: str, install_command: str | None = None) -> None:
    is_linux = platform.system() == "Linux"
    if is_linux:
        _install(*packages, install_command)
    else:
        message = "Required packages can only be installed on Linux"
        warnings.warn(message)


def _install(*packages: str, install_command: str | None = None) -> None:
    if install_command is None:
        install_command = extract_package_manager()
    for package in packages:
        args = shlex.split(package)
        run(install_command, *args, root=True, check=False)


def extract_package_manager():
    commands = {"apt": "apt install -y", "pacman": "pacman -S --noconfirm"}
    for manager, command in commands.items():
        if is_success("which", manager):
            return command
