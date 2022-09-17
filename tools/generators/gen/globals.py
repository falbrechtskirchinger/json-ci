import random
import string

from jinja2 import pass_eval_context

from .decorators import JinjaGlobal as jinja_global


@jinja_global
def _global_random_string(length=8, alphabet=None):
    if not alphabet:
        alphabet = string.ascii_letters + string.octdigits
    return "".join(list(map(lambda _: random.choice(alphabet), range(length))))


@jinja_global
@pass_eval_context
def _global_counter_string(ctx, length=4):
    self = _global_counter_string
    if not hasattr(self, "count") or id(ctx) != self.ctx_id:
        self.count = 0
        self.ctx_id = id(ctx)

    count = self.count
    self.count += 1

    return "{:0{n}d}".format(count, n=length)


@jinja_global(type=jinja_global.VARIABLE)
def _global_set():
    return set


@jinja_global(type=jinja_global.VARIABLE)
def _global_tuple():
    return tuple
