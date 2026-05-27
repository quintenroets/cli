"""Launch a command in a new cmux tab to verify run_in_new_tab end-to-end."""
# ruff: noqa: INP001

import cli


def main() -> None:
    command = "echo 'hello from the new tab'; pwd"
    cli.run_in_new_tab(command, title="new-tab-test")


if __name__ == "__main__":
    main()
