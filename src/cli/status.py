import contextlib

from .console import console


def status(*args, **kwargs):
    console.clear_live()
    use_status = not is_running_in_notebook()
    return console.status(*args, **kwargs) if use_status else contextlib.nullcontext()


def is_running_in_notebook() -> bool:
    try:
        get_ipython()
    except NameError:
        in_notebook = False
    else:
        in_notebook = True
    return in_notebook
