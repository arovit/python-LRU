#!/usr/bin/python

from collections import OrderedDict
from time import time

def lru_cache_function(max_size=1024, expiration=15*60):
    def wrapper(func):
        return LRUCachedFunction(func, LRUCacheDict(max_size, expiration))
    return wrapper


class LRUCacheDict(object):
    """ A dictionary-like object, supporting LRU caching semantics.
    """
    def __init__(self, max_size=1024, expiration=15*60):
        self.max_size = max_size
        self.expiration = expiration

        self.__values = {}
        self.__expire_times = OrderedDict()
        self.__access_times = OrderedDict()

    def size(self):
        return len(self.__values)

    def clear(self):
        self.__values.clear()
        self.__expire_times.clear()
        self.__access_times.clear()

    def has_key(self, key):
        return self.__values.has_key(key)

    def __setitem__(self, key, value):
        t = int(time())
        self.__delete__(key)
        self.__values[key] = value
        self.__access_times[key] = t
        self.__expire_times[key] = t + self.expiration
        self.cleanup()

    def __getitem__(self, key):
        t = int(time())
        del self.__access_times[key]
        self.__access_times[key] = t
        self.cleanup()
        return self.__values[key]

    def __delete__(self, key):
        if self.__values.has_key(key):
            del self.__values[key]
            del self.__expire_times[key]
            del self.__access_times[key]

    def cleanup(self):
        if self.expiration is None:
            return None
        t = int(time())
        #Delete expired
        for k in self.__expire_times.iterkeys():
            if self.__expire_times[k] < t:
                self.__delete__(k)
            else:
                break

        #If we have more than self.max_size items, delete the oldest
        while (len(self.__values) > self.max_size):
            for k in self.__access_times.iterkeys():
                self.__delete__(k)
                break

class LRUCachedFunction(object):
    """
    >>> def f(x):
    ...    print "Calling f(" + str(x) + ")"
    ...    return x
    >>> f = LRUCachedFunction(f, LRUCacheDict(max_size=3, expiration=3) )

    """
    def __init__(self, function, cache=None):
        if cache:
            self.cache = cache
        else:
            self.cache = LRUCacheDict()
        self.function = function
        self.__name__ = self.function.__name__

    def __call__(self, *args, **kwargs):
        key = repr( (args, kwargs) ) + "#" + self.__name__ #In principle a python repr(...) should not return any # characters.
        try:
            return self.cache[key]
        except KeyError:
            value = self.function(*args, **kwargs)
            self.cache[key] = value
            return value
   
