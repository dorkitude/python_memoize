import functools
import types
import inspect
import md5

from dorkitude_utils import dict_utils
from dorkitude_utils import hashing


class Memoize(object):
    """

    This is a decorator.  It will cache the results of a bound function (a
    classmethod or an instance method), as long as its arguments are hashable.

    Then next time you call the function, the cached results will be returned,
    rather than the function having to re-execute.

    For unbound functions, use MemoizeGlobal instead!

    """

    v=0

    def __init__(self, function):
        self.function = function 

    def __get__(self, obj, objtype):
        """Added to support instance methods."""
        fn = functools.partial(self.__call__, obj)
        return fn

    def __call__(self, *args, **kwargs):

        try:
            obj = args[0]
        except IndexError, e:
            msg = "No first argument was sent to the function call.  "
            msg += "If this is an unbound function, use MemoizeGlobal instead:"
            msg += "  {}".format(self.function)
            msg += "  Original error: {}".format(e)
            raise Exception(msg)

        if (not hasattr(obj, '_memoize_cache')
                or "_memoize_cache" not in obj.__dict__):
            obj._memoize_cache = {}

        key = (Memoize.v, self.function, args[1:], frozenset(kwargs.items()))

        if key not in obj._memoize_cache:
            obj._memoize_cache[key] = self.function(*args, **kwargs)
        else:
            pass

        return obj._memoize_cache[key]

    @classmethod
    def flush_item(self, obj):
        obj._memoize_cache = {}

    @classmethod
    def flush(cls):
        cls.v = cls.v + 1

    @classmethod
    def flush_all(cls):
        cls.flush()


class MemoizeGlobal(object):
    """

    Use to decorate global (module-level) functions that need to be memoized.

    Uses this class itself for storage, meaning data is only stored in server
    memory.

    """

    storage = {}

    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):

        key = (self.function.__name__, id(self.function), args, frozenset(kwargs.items()))

        fetched = self.fetch(key)

        if fetched:
            return fetched

        else:
            executed = self.function(*args, **kwargs)
            self.store(key, executed)

            return executed

    def fetch(self, key):
        try:
            return self.__class__.storage[key]
        except KeyError:
            return None

    def store(self, key, value):
        self.__class__.storage[key] = value
    
    @classmethod
    def flush(cls):
        cls.storage = {}

    @classmethod
    def flush_all(cls):
        cls.flush()
