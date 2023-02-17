import os
import shlex
import subprocess
import sys
import types


def sh(*cmds, **kwargs):
    return run_commands(*cmds, shell=True, **kwargs)


def run_commands(*cmds, **kwargs):
    for cmd in cmds:
        run(cmd, **kwargs)


def urlopen(*urls):
    for url in urls:
        if os.name == "nt":
            os.startfile(url)
        else:
            start("xdg-open", url)


def start(*args, **kwargs):
    return run(*args, wait=False, **kwargs)


def lines(*args, **kwargs) -> list[str]:
    output = get(*args, **kwargs)
    lines = [line for line in output.splitlines() if line]
    return lines


def get(*args, **kwargs) -> str:
    kwargs["capture_output"] = True
    output = run(*args, **kwargs)
    if not kwargs.get("capture_output_tty"):
        output = output.stdout
    return output.strip()


def is_success(*args) -> bool:
    return return_code(*args) == 0


def return_code(*args) -> int:
    return run(*args, check=False, capture_output=True).returncode


def run(
    *args,
    root=False,
    wait=True,
    console=False,
    text=True,
    check=True,
    shell=False,
    capture_output_tty=False,
    title=None,
    **kwargs,
) -> str | subprocess.CompletedProcess:
    """
    tty: also works for special outputs that clear the output and move the cursor
    """
    args = prepare_args(args, command=shell or console, root=root)

    if console:
        run("activate_window Konsole", check=False)
        wait = False  # avoid blocking if console not opened yet
        if title is not None and False:  # disable for now
            args = (f'echo -ne "\\033]30;{title}\\007"; ' + args[0],)
        args = [
            "konsole",
            "--new-tab",
            "-e",
            os.environ["SHELL"],
            "-c",
            *args,
        ]

        # needed for non-login scripts to be able to activate console
        if "DISPLAY" not in os.environ:
            os.environ["DISPLAY"] = ":0.0"

    if not wait:
        kwargs["stdout"] = kwargs["stderr"] = subprocess.DEVNULL

    try:
        if capture_output_tty:
            import tempfile  # noqa: autoimport

            import pexpect  # noqa: autoimport

            with tempfile.TemporaryFile() as tmp:
                child = pexpect.spawn(args[0], [*args[1:]], timeout=None, logfile=tmp)
                if "capture_output" in kwargs:
                    child.expect(pexpect.EOF)
                else:
                    child.interact()
                tmp.seek(0)
                res = tmp.read().decode()
        else:
            res = (
                subprocess.run(args, text=text, check=check, shell=shell, **kwargs)
                if wait
                else subprocess.Popen(args, shell=shell, **kwargs)
            )
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr or e)  # more verbose errors

    return res


def prepare_args(args, command=False, root=False):
    args = [str(arg) for arg in iterate_args(args, command)]
    if command:
        subargs_str = shlex.join(args[1:])
        if subargs_str:
            args = [" ".join((args[0], subargs_str))]

    if os.name == "posix":
        root_kw = "sudo"
        if root_kw in args[0]:
            root = True

        if root:
            if not auto_pw():
                from . import env  # noqa: autoimport

                env.load()

            if command:
                arg = args[0]
                if root_kw not in arg:
                    arg = root_kw + " " + arg
                if auto_pw():
                    args = [arg.replace(root_kw, root_kw + " -A")]
            else:
                if args[0] != root_kw:
                    args.insert(0, root_kw)
                if auto_pw():
                    args.insert(1, "-A")

    return args


def auto_pw() -> bool:
    return "SUDO_ASKPASS" in os.environ


def iterate_args(args, command):
    """
    arg can be:

    - command string
    - iterable of command parts
    """

    for i, arg in enumerate(args):
        if i == 0 and isinstance(arg, str) and not command:
            # allow first argument in the form of a command
            # only split if not in shell or console
            yield from shlex.split(arg)
        elif isinstance(arg, dict):
            for k, v in arg.items():
                yield f"--{k}"
                if v is not None:
                    yield v
        elif isinstance(arg, set):
            for part in arg:
                yield f"--{part}"
        elif (
            isinstance(arg, list)
            or isinstance(arg, tuple)
            or isinstance(arg, types.GeneratorType)
        ):
            yield from arg
        else:  # item with str method e.g. Path or int
            yield arg


def set_title(title: str):
    echo_message = f"\\033]30;{title}\\007"
    command = f'echo -ne "{echo_message}"'
    run(command)


def main():
    command = shlex.join(sys.argv[1:])
    run(command, console=True)


if __name__ == "__main__":
    main()
