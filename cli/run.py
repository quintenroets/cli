import os
import shlex
import subprocess
import sys
import time
import types

from .errorhandler import ErrorHandler as errorhandler


def sh(*cmds, **kwargs):
    return commands(*cmds, shell=True, **kwargs)


def run_commands(*cmds, **kwargs):
    for cmd in cmds:
        run(cmd, **kwargs)


def urlopen(*urls):    
    for url in urls:
        if os.name == 'nt':
            os.startfile(url)
        else:
            start('xdg-open', url)


def start(*args, **kwargs):
    return run(*args, wait=False, **kwargs)


def lines(*args, **kwargs):
    lines = get(*args, **kwargs).split('\n')
    lines = [l for l in lines if l]
    return lines


def get(*args, **kwargs):
    kwargs['capture_output'] = True
    return run(*args, **kwargs).stdout


def run(*args, root=False, wait=True, console=False, text=True, check=True, shell=False, **kwargs):
    """
    arg can be:
        - string
        - iterable of command parts (only allowed if not shell and not console)
    """
    args = list(args) if shell or console else parse_args(args)
        
    if os.name == 'posix':
        if root:
            args.insert(0, 'sudo')
        if 'sudo' in args:
            
            if 'SUDO_ASKPASS' not in os.environ:
                from . import env  # lazy import
                env.load()
            if 'SUDO_ASKPASS' in os.environ:
                args.insert(args.index('sudo') + 1, '-A')
            
    if console:
        wait = False  # avoid blocking if console not opened yet
        args = ['konsole', '--new-tab', '-e', os.environ['SHELL'], '-c', *args]
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ':0.0' # needed for non-login scripts to be able to activate console
            
    if not wait:
        kwargs['stdout'] = kwargs['stderr'] = subprocess.DEVNULL
    
    try:
        res = (
            subprocess.run(args, text=text, check=check, shell=shell, **kwargs)
            if wait else
            subprocess.Popen(args, shell=shell, **kwargs)
        )
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr or e)  # more verbose errors
    
    if console:
        run('wmctrl -a Konsole', check=False)
            
    return res


def parse_args(args):
    """
    arg can be:
        - command string
        - iterable of command parts
    """
    
    parsed = []
    for arg in args:
        if isinstance(arg, str):
            parsed += shlex.split(arg)
        elif isinstance(arg, dict):
            for k, v in arg.items():
                parsed.append(f'--{k}')
                if v not in [None, True]:
                    parsed.append(v)
        elif isinstance(arg, list):
            parsed += arg
        elif isinstance(arg, types.GeneratorType):
            parsed += list(arg)
        else:
            # item with str method e.g. Path or int
            parsed.append(str(arg))
            
    return parsed


def main():
    with errorhandler():
        command = ' '.join(sys.argv[1:])
        run(command, console=True)


if __name__ == "__main__":
    main()
