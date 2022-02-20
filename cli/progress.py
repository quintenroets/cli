def progress(sequence, description=None, total=None, unit="it", description_width=None):
    from rich.progress import (
        TextColumn,
        BarColumn,
        TimeRemainingColumn,
        Progress,
    )  # lazy imports

    columns = (
        [TextColumn("[progress.description]{task.description}")] if description else []
    )
    columns.extend(
        (
            TextColumn(
                "[progress.completed]{task.completed}/[progress.total]{task.total:>0.0f} "
                + unit
            ),
            BarColumn(bar_width=1000),  # shrinks depending on other columns
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        )
    )
    progress = Progress(*columns)

    with progress:
        yield from progress.track(sequence, total=total, description=description)
