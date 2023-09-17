from hypothesis import given, strategies

import cli


def text_strategy(**kwargs):
    blacklist_categories = "Cc", "Cs", "Zs"
    alphabet = strategies.characters(
        blacklist_categories=blacklist_categories, **kwargs
    )
    return strategies.text(alphabet=alphabet)


@given(message=text_strategy())
def test_output(message):
    assert cli.get("printf", "%s", message) == message


@given(message=text_strategy())
def test_lines(message):
    assert cli.lines("printf", "%s", message) == message.splitlines()


@given(message=text_strategy())
def test_pipe(message):
    commands = (
        ("printf", "%s", message),
        ("grep", "-F", "--", message),
    )
    assert cli.pipe(commands, check=False) == message


@given(return_code=strategies.integers(min_value=0, max_value=255))
def test_return_code(return_code):
    assert cli.return_code("exit", return_code, shell=True) == return_code
