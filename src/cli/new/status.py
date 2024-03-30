import contextlib


def status(*args, **kwargs):
    import cli  # noqa: E402, autoimport

    try:
        get_ipython()
    except NameError:
        notebook = False
    else:
        notebook = True

    cli.console.clear_live()

    return (
        cli.console.status(*args, **kwargs)
        if cli.console._live is None and not notebook
        else contextlib.nullcontext()
    )
