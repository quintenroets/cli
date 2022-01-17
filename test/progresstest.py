import cli

items = list(range(200))
items = cli.progress(items, description='counting', unit='items')

import time

for i in items:
    time.sleep(0.01)
