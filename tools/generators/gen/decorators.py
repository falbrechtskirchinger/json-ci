from types import FunctionType


class RegistryDecoratorBase:
    def __init__(self, name_or_fn, prefix, *args, **kwargs):
        self.prefix = prefix

        # was this decorator called with or without parameters?
        self.is_parameterless_decorator = bool(
            isinstance(name_or_fn, FunctionType) and not args and not kwargs
        )
        if self.is_parameterless_decorator:
            # for parameterless decorators, __init__ is the wrapping function
            self.name = None
            self.fn = name_or_fn
            self._register()
        else:
            self.name = name_or_fn

        self._init(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.is_parameterless_decorator:
            # for parameterless decorators, __call__ is the wrapped function and we need to forward the call to self.fn
            return self.fn(*args, **kwargs)
        else:
            # otherwise, __call__ is the wrapping function
            self.fn = args[0]
            self._register()
            return self.fn

    def _init(self, *args, **kwargs):
        raise NotImplementedError

    def _wrapped(self, *args, **kwargs):
        raise NotImplementedError

    def _register(self):
        if not self.name:
            self.name = self.fn.__name__.removeprefix("_").removeprefix(self.prefix)
        self.__class__.registry[self.name] = self._wrapped


class JinjaFilterDriver(RegistryDecoratorBase):
    registry = {}

    def __init__(self, name_or_fn=None, *args, **kwargs):
        super().__init__(name_or_fn, "filter_driver_", *args, **kwargs)

    def _init(self):
        pass

    def _wrapped(self, *args, **kwargs):
        return self.fn(*args, *kwargs)


class JinjaFilter(RegistryDecoratorBase):
    registry = {}

    def __init__(self, name_or_fn=None, *args, **kwargs):
        self.driver = None
        self.driver_fn = None
        super().__init__(name_or_fn, "filter_", *args, **kwargs)

    def _init(self, *, driver=None):
        self.driver = driver

    def _wrapped(self, *args, **kwargs):
        if self.driver:
            if not self.driver_fn:
                try:
                    self.driver_fn = JinjaFilterDriver.registry[self.driver]
                except KeyError:
                    raise RuntimeError(f"unknown Jinja filter driver: '{self.driver}'")
            return self.driver_fn(self.fn, *args, **kwargs)
        return self.fn(*args, **kwargs)


class JinjaGlobal(RegistryDecoratorBase):
    FUNCTION = "func"
    VARIABLE = "var"

    registry = {}

    def __init__(self, name_or_fn=None, *args, **kwargs):
        super().__init__(name_or_fn, "global_", *args, **kwargs)

    def _init(self, *, type=None):
        self.type = type if type else self.FUNCTION
        if not self.type in (self.FUNCTION, self.VARIABLE):
            raise ValueError(
                "global type must be one of JinjaGlobal.FUNCTION or"
                " JinjaGlobal.VARIABLE"
            )

    def _wrapped(self, *args, **kwargs):
        if self.type == self.VARIABLE:
            return self.fn()
        return self.fn
