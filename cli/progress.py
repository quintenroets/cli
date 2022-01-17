from rich.progress import *

    
def progress(
    sequence: Union[Sequence[ProgressType], Iterable[ProgressType]],
    description: str = None,
    total: Optional[int] = None,
    unit = 'it',
    description_width=None
) -> Iterable[ProgressType]:

    columns: List["ProgressColumn"] = (
        [TextColumn("[progress.description]{task.description}")] if description else []
    )
    columns.extend(
        (
            TextColumn("[progress.completed]{task.completed}/[progress.total]{task.total:>0.0f} " + unit),
            BarColumn(bar_width=500), # shrinks depending on other columns
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        )
    )
    progress = Progress(*columns)

    with progress:
        yield from progress.track(
            sequence, total=total, description=description
        )
