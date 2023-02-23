from setuptools import find_packages, setup

NAME = "quinten-cli"


def read(filename):
    try:
        with open(filename) as fp:
            content = fp.read().split("\n")
    except FileNotFoundError:
        content = []
    return content


setup(
    author="Quinten Roets",
    author_email="quinten.roets@gmail.com",
    description="extended subprocess",
    name=NAME,
    version="1.0.1",
    packages=find_packages(),
    install_requires=read("requirements.txt"),
    entry_points={
        "console_scripts": [
            "konsolerun = cli.run:main",
        ]
    },
)
