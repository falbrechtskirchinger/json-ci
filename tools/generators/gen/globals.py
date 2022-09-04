import random
import string

from .decorators import JinjaGlobal as jinja_global


@jinja_global
def _global_random_string(length=8, alphabet=None):
    if not alphabet:
        alphabet = string.ascii_letters + string.octdigits
    return "".join(list(map(lambda _: random.choice(alphabet), range(length))))


@jinja_global(type=jinja_global.VARIABLE)
def _global_set():
    return set


@jinja_global(type=jinja_global.VARIABLE)
def _global_tuple():
    return tuple
