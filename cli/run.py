import os
import sh
import shlex
import subprocess
import sys
import time
import types

from .errorhandler import ErrorHandler as errorhandler


def urlopen(*urls):
    urls = parse_iterable(urls)
    
    for url in urls:
        if os.name == 'nt':
            os.startfile(url)
        else:
            start(('xdg-open', url))


def start(*commands, **kwargs):
    return run(*commands, wait=False, **kwargs)
    

def get(*commands, **kwargs):
    kwargs['capture_output'] = True
    return run(*commands, **kwargs)


def run(*commands, **kwargs):
    """
    command can be:
        - command string
        - iterable of iterables of command parts
    """
    if 'capture_output' in kwargs:
        res = "".join([_run(command, **kwargs).stdout.strip() for command in commands])
    else:
        res = None  # sometimes no commands
        for command in commands:
            res = _run(command, **kwargs)
            
    if kwargs.get("console") and list(commands):
        # only activate console if console kwargs True and if commands have effectively run
        
        console = "konsole"
        is_open = get(
            f"wmctrl -l | grep ' '$(xdotool get_desktop)' ' | grep {console.capitalize()}",
            check=False
        )
        if not is_open:
            time.sleep(0.5)  # wait if first tab
        run(f"jumpapp -w {console}")
            
    return res


def _run(args, root=False, wait=True, console=False, text=True, check=True, shell=False, **kwargs):
    shell = shell or (any([shell_token in args for shell_token in "*|;$"]) and not console)  # don't use on untrusted input
    args = [args] if shell else parse_args(args, console)
    
    if (root or 'sudo' in args) and os.name == "posix":
        args.insert(0, "sudo")
            
        if "SUDO_ASKPASS" not in os.environ:
            from . import env  # lazy import
            env.load()
            
        if "SUDO_ASKPASS" in os.environ:
            args.insert(1, "-A")
            
    if console:
        wait = False  # avoid focussing console after process finished
        args = ["konsole", "--new-tab", "-e", os.environ["SHELL"], "-c"] + args
        if "DISPLAY" not in os.environ:
            os.environ["DISPLAY"] = ":0.0" # needed for non-login scripts to be able to activate console
            
    if not wait:
        kwargs['stdout'] = kwargs['stderr'] = subprocess.DEVNULL
        
    run = subprocess.run if wait else subprocess.Popen
    
    try:
        res = (
            subprocess.run(args, text=text, check=check, shell=shell, **kwargs)
            if wait else
            subprocess.Popen(args, shell=shell, **kwargs)
        )
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr or e)  # more verbose errors
    
    return res
    

def parse_iterable(values):
    if len(values) == 1 and not isinstance(values[0], str):
        values = values[0]
    return values


def parse_args(args, console=False):
    """
    args can be:
        - command string
        - iterable of iterables of command parts
    """
    if isinstance(args, str):
        parsed = shlex.split(args)
    else:
        parsed = []
        for arg in args:
            if isinstance(arg, str):
                parsed += shlex.split(arg)
            elif isinstance(arg, dict):
                parsed += [f"--{k}", v]
            elif isinstance(arg, list):
                parsed += arg
            elif isinstance(arg, types.GeneratorType):
                parsed += list(arg)
            else:
                # item with str method e.g. Path 
                parsed.append(str(arg))
    
    if console:  # literal string needed
        parsed = [" ".join(parsed)]
            
    return parsed


def install(*packages, installer_command=None):
    # lazy imports
    import platform
    import warnings
    
    packages = parse_args(packages)
    
    if platform.system() == "Linux":
        command = installer_command or get_install_command()
        commands = ((installer_command, p) for p in packages)
        cli.run(commands, root=True, check=False)
    else:        
        message = f"Required packages cannot be installed automatically because OS is not Linux"
        warnings.warn(message)


def get_install_command():
    commands = {
        "apt": "apt install -y",
        "pacman": "pacman -S --noconfirm"
    }
    for manager, command in commands.items():
        if sh.which(manager):
            return command


def main():
    with errorhandler():
        commands = sys.argv[1:]
        run(commands, console=True)


if __name__ == "__main__":
    main()
