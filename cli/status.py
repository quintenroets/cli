def status(*args, **kwargs):
    import contextlib  # noqa: autoimport

    import cli  # noqa: autoimport

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
