def status(*args, **kwargs):
    import cli
    import contextlib

    try:
        get_ipython()
    except:
        notebook = False
    else:
        notebook = True

    return (
        cli.console.status(*args, **kwargs)
        if cli.console._live is None and not notebook
        else contextlib.nullcontext()
    )
