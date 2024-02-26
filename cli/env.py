from dotenv import load_dotenv
from superpathlib import Path


def load(path=None):
    path = path or Path.HOME / ".bash_profile"
    load_dotenv(dotenv_path=path)
