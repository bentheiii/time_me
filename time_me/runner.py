from typing import Callable

from abc import ABC, abstractmethod
from functools import update_wrapper


class Runner(ABC):
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    @abstractmethod
    def assign_result(self, key, result):
        pass


class FunctionRunner(Runner):
    def __init__(self, func: Callable):
        update_wrapper(self, func)
        self.__func__ = func

    def __call__(self, *args, **kwargs):
        return self.__func__(*args, **kwargs)

    def __str__(self):
        return self.__func__.__name__

    def assign_result(self, key, result):
        if not hasattr(self.__func__, '__results__'):
            self.__func__.__results__ = {}
        self.__func__.__results__[key] = result


class ObjectRunner(Runner):
    def __init__(self, obj, func, args, kwargs):
        self.obj = obj
        self.__func__ = func
        self.args = args
        self.kwargs = kwargs
        self.__name__ = None

    def __call__(self, *args, **kwargs):
        return self.__func__(*self.args, *args, **self.kwargs, **kwargs)

    def __str__(self):
        return self.__name__ or f'{self.obj} ({self.__func__.__name__})'

    def assign_result(self, key, result):
        pass


def runner(x) -> Runner:
    if callable(x):
        return FunctionRunner(x)
    raise TypeError(x)
