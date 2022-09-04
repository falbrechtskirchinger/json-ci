import shlex

from .decorators import JinjaFilterDriver as jinja_filter_driver
from .decorators import JinjaFilter as jinja_filter


@jinja_filter_driver
def _filter_driver_identity(fn, *args, **kwargs):
    return fn(*args, **kwargs)


@jinja_filter_driver
def _filter_driver_foreach(fn, input, *args, **kwargs):
    if isinstance(input, list):
        return [fn(x, *args, **kwargs) for x in input]
    elif not isinstance(input, str):
        try:
            it = iter(input)
        except TypeError:
            pass
        else:
            return (fn(x, *args, **kwargs) for x in it)

    return fn(input, *args, **kwargs)


@jinja_filter(driver="foreach")
def _filter_append(input, suffix):
    return f"{input}{suffix}"


@jinja_filter(driver="foreach")
def _filter_prepend(input, prefix):
    return f"{prefix}{input}"


@jinja_filter(driver="foreach")
def _filter_format_as(input, fmt):
    return fmt.format(input)


@jinja_filter(driver="foreach")
def _filter_quote(input, q='"'):
    return f"{q}{input}{q}"


@jinja_filter(driver="foreach")
def _filter_shell_quote(input):
    return shlex.quote(input)


_SLUG_CHARS = "/-. "
_SLUG_TRANS = str.maketrans(_SLUG_CHARS, "_" * len(_SLUG_CHARS))


@jinja_filter(driver="foreach")
def _filter_slugify(input):
    return input.translate(_SLUG_TRANS)


@jinja_filter
def _filter_write_to_file(
    text, filename, lstrip=False, rstrip=False, strip=False, append=True
):
    def _strip(x):
        if strip:
            return x.strip(strip if isinstance(strip, str) else None)
        if lstrip:
            x = x.lstrip(lstrip if isinstance(lstrip, str) else None)
        if rstrip:
            x = x.rstrip(rstrip if isinstance(rstrip, str) else None)
        return x

    if len(shlex.split(filename)) > 1:
        filename = shlex.quote(filename)

    res = [] if append else [f'RUN printf "" >{filename}']
    res += [
        f'RUN printf "{line}\\n" >>{filename}' for line in map(_strip, text.split("\n"))
    ]
    return "\n".join(res)
