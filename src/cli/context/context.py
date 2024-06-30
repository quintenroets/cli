from package_utils.context import Context

from cli.models import Config, Options, Secrets

context = Context(Options, Config, Secrets)
