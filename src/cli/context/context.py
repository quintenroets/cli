from cli.models import Config, Options, Secrets
from package_utils.context import Context

context = Context(Options, Config, Secrets)
