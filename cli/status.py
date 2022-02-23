def status(*args, **kwargs):
    import cli
    import contextlib

    return (
        cli.console.status(*args, **kwargs)
        if cli.console._live is None
        else contextlib.nullcontext()
    )
