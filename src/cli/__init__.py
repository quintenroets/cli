from .commands import (
    capture_output,
    capture_output_lines,
    capture_return_code,
    completes_successfully,
    launch,
    launch_commands,
    open_urls,
    pipe_output_and_capture,
    run,
    run_commands,
    run_commands_in_shell,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from .terminal import confirm, console, prompt, track_progress  # pragma: nocover
else:
    from .terminal import __getattr__
