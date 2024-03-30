from package_utils.context.entry_point import create_entry_point

from cli import main

from ..context import context

entry_point = create_entry_point(main, context)
