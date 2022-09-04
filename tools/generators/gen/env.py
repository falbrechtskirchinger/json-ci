from jinja2 import Environment, FileSystemLoader

from . import filters
from . import globals
from .decorators import JinjaFilter, JinjaGlobal


def create_jinja_environment(searchpath, **kwargs):
    # set up Jinja
    env = Environment(
        loader=FileSystemLoader(searchpath=searchpath),
        extensions=["jinja2.ext.debug", "jinja2.ext.do"],
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        **kwargs,
    )

    # add filters
    for name, fn in JinjaFilter.registry.items():
        env.filters[name] = fn

    # add globals
    for name, g in JinjaGlobal.registry.items():
        env.globals[name] = g()

    return env
