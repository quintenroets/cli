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
    
    if os.name == 'nt':
        for url in urls:
            os.startfile(url)
    else:
        for url in urls:
            start(f'xdg-open "{url}"')


def start(*commands, **kwargs):
    return run(*commands, wait=False, **kwargs)
    

def get(*commands, **kwargs):
    kwargs['capture_output'] = True
    return run(*commands, **kwargs)


def run(*commands, **kwargs):
    commands = parse_iterable(commands)
    
    if 'capture_output' in kwargs:
        res = "".join([_run(command, **kwargs).stdout.strip() for command in commands])
    else:
        for command in commands:
            res = _run(command, **kwargs)
            
    if kwargs.get("console") and commands:
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


def _run(*args, root=False, wait=True, console=False, text=True, check=True, shell=False, **kwargs):
    shell = shell or (any([shell_token in args[0] for shell_token in "|;$"]) and not console)  # don't use on untrusted input
    args = list(args) if shell or console else parse_args(args)
    
    if (root or 'sudo' in args) and os.name == "posix":
        args.insert(0, "sudo")
            
        if "SUDO_ASKPASS" not in os.environ:
            from . import env  # lazy import
            env.load()
            
        if "SUDO_ASKPASS" in os.environ:
            args.insert(1, "-A")
            
    if console:
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


def parse_args(args):
    if len(args) == 1 and isinstance(args[0], str):
        args = shlex.split(args[0])
    
    parsed = []
    for arg in args:
        if isinstance(arg, dict):
            parsed += [f"--{k}", v]
        elif isinstance(arg, list):
            parsed += arg
        elif isinstance(arg, types.GeneratorType):
            parsed += list(arg)
        else:
            parsed.append(arg)
            
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
