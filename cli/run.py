import os
import shlex
import subprocess
import sys
import time
import types


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
    output = run(*args, **kwargs)
    if not kwargs.get('tty'):
        output = output.stdout
    return output.strip()


def run(*args, root=False, wait=True, console=False, text=True, check=True, shell=False, capture_output_tty=False, **kwargs):
    """
    tty: also works for special outputs that clear the output and move the cursor
    """
    args = prepare_args(args, command=shell or console, root=root)
            
    if console:
        run('wmctrl -a Konsole', check=False)
        wait = False  # avoid blocking if console not opened yet
        args = ['konsole', '--new-tab', '-e', os.environ['SHELL'], '-c', *args]
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ':0.0' # needed for non-login scripts to be able to activate console
            
    if not wait:
        kwargs['stdout'] = kwargs['stderr'] = subprocess.DEVNULL
    
    try:
        if capture_output_tty:
            import pexpect
            import tempfile
            with tempfile.TemporaryFile() as tmp:
                child = pexpect.spawn(args[0], [*args[1:]], timeout=None, logfile=tmp)
                if 'capture_output' in kwargs:
                    child.expect(pexpect.EOF)
                else:
                    child.interact()
                tmp.seek(0)
                res = tmp.read().decode()
        else:
            res = (
                subprocess.run(args, text=text, check=check, shell=shell, **kwargs)
                if wait else
                subprocess.Popen(args, shell=shell, **kwargs)
            )
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr or e)  # more verbose errors
                
    return res


def prepare_args(args, command=False, root=False):
    if not command:
        args = iterate_args(args)
        
    args = [str(arg) for arg in args]
    
    if os.name == 'posix':
        root_kw = 'sudo'
        if root_kw in args[0]:
            root = True
    
        if root:
            if 'SUDO_ASKPASS' not in os.environ:
                from . import env  # lazy import
                env.load()
                
            if command:
                arg = args[0]
                if root_kw not in arg:
                    arg = root_kw + ' ' + arg
                args = [arg.replace(root_kw, root_kw + ' -A')]
            else:
                if args[0] != root_kw:
                    args.insert(0, root_kw)
                args.insert(1, '-A')
    
    return args


def iterate_args(args):
    '''
    arg can be:
        - command string
        - iterable of command parts
    '''
    
    for i, arg in enumerate(args):
        if i == 0 and isinstance(arg, str):
            # allow first argument in the form of a command
            yield from shlex.split(arg)
        elif isinstance(arg, dict):
            for k, v in arg.items():
                yield f'--{k}'
                if v is not None:
                    yield v
        elif isinstance(arg, set):
            for part in arg:
                yield f'--{part}'
        elif isinstance(arg, list) or isinstance(arg, tuple) or isinstance(arg, types.GeneratorType):
            yield from arg
        else:  # item with str method e.g. Path or int
            yield arg


def main():
    command = ' '.join(sys.argv[1:])
    run(command, console=True)


if __name__ == '__main__':
    main()
