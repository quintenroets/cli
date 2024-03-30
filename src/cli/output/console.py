from ..commands import run


def set_title(title: str) -> None:
    echo_message = f"\\033]30;{title}\\007"
    command = f'echo -ne "{echo_message}"'
    run(command)
