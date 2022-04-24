from dotenv import load_dotenv
from plib import Path


def load(path=None):
    path = path or Path.HOME / ".bash_profile"
    load_dotenv(dotenv_path=path)
