from typing import Union, Tuple, Dict, Mapping, Any, SupportsFloat, Iterable, Sequence

from functools import total_ordering

from math import isclose

from time_me.runner import Runner, runner as to_runner, ObjectRunner
from time_me.timer import Timer

ArgSet_Raw = Tuple[Tuple, Dict]
ArgSet = Union[ArgSet_Raw, Tuple, Dict]


def parse_argset(a):
    if isinstance(a, tuple) and len(a) == 2 and isinstance(a[0], tuple) and isinstance(a[1], dict):
        return a
    elif isinstance(a, Iterable):
        return a, {}
    elif isinstance(a, Mapping):
        return (), a
    raise TypeError(a)


class Coach:
    def __init__(self, sanity_argsets: Mapping[ArgSet, Any] = None, sanity_tol=1e-7, verbose=False):
        self._sanity_argsets = sanity_argsets or {}
        self._sanity_tol = sanity_tol

        self._measured = set()

        self.verbose = verbose

    def call(self, runner: Runner, argset: ArgSet, timer: Timer):
        a, k = parse_argset(argset)
        with timer.resume():
            runner(*a, **k)

    def sane(self, expected_value: Any, actual: Any):
        if expected_value == actual:
            return True
        if isinstance(actual, (float, int)) and isinstance(expected_value, (float, int)) \
                and isclose(actual, expected_value, abs_tol=self._sanity_tol):
            return True
        if isinstance(actual, Mapping) and isinstance(expected_value, Mapping) \
                and self.sane(expected_value.items(), actual.items()):
            return True
        if isinstance(actual, Iterable) and isinstance(expected_value, Iterable) \
                and type(expected_value) == type(actual):
            i, j = iter(expected_value), iter(actual)
            end = object()
            while True:
                v_1, v_2 = next(i, end), next(j, end)
                if v_1 is end:
                    if v_2 is end:
                        return True
                    break
                if v_2 is end:
                    break
                if not self.sane(v_1, v_2):
                    break
        return False

    def iter_argsets(self, timer) -> Iterable[ArgSet_Raw]:
        yield ((), {})

    def __call__(self, runner):
        if not isinstance(runner, Runner):
            runner = to_runner(runner)

        for sa, expected in self._sanity_argsets.items():
            a, k = parse_argset(sa)
            actual = runner(*a, **k)
            if not self.sane(expected, actual):
                raise ValueError(f'{expected} vs {actual}')

        timer = Timer()
        n = 0

        for argset in self.iter_argsets(timer):
            a, k = argset
            with timer.resume():
                runner(*a, **k)
            n += 1

        ret = self.Result(runner, timer, n)
        runner.assign_result(self, ret)
        self._measured.add(ret)
        return ret

    def measure(self, obj):
        result = self(obj)
        if self.verbose:
            print(result)
        return obj

    def compare(self, *objs):
        if not objs:
            objs = self._measured
        results = []
        for o in objs:
            if isinstance(o, __class__.Result):
                results.append(o)
            else:
                res_dict = getattr(o, '__results__', None)
                if isinstance(res_dict, Mapping) and self in res_dict:
                    results.append(res_dict[self])
                else:
                    results.append(self(o))

        return self.ResultComparison(sorted(results))

    def trial(self, obj_key: Union[int, str] = 0):
        def ret(func):
            def ret(*args, __name__=None, **kwargs):
                if isinstance(obj_key, int):
                    if len(args) <= obj_key:
                        raise ValueError(f'trial must have at least {obj_key - 1} positional arguments')
                    obj = args[obj_key]
                else:
                    if obj_key not in kwargs:
                        raise ValueError(f'trial must have {obj_key} keyword arguments')
                    obj = kwargs[obj_key]
                runner = ObjectRunner(obj, func, args, kwargs)
                if __name__:
                    runner.__name__ = __name__
                return self(runner)

            return ret

        return ret

    class Result:
        def __init__(self, runner: Runner, total_time: SupportsFloat, n: int):
            self.runner = runner
            self.total_time = float(total_time)
            self.n = n

        def __float__(self):
            return self.total_time / self.n

        def __lt__(self, other):
            return float(self) < float(other)

        def __gt__(self, other):
            return float(self) > float(other)

        def __le__(self, other):
            return float(self) <= float(other)

        def __ge__(self, other):
            return float(self) >= float(other)

        def __str__(self):
            if self.n > 1:
                return f'{self.runner}: {self.total_time:.2g}/{self.n:,} = {float(self):.2g} seconds'
            return f'{self.runner}: {self.total_time:.2g} seconds'

        def __truediv__(self, other):
            return float(self) / float(other)

    class ResultComparison(Sequence[Result]):
        def __init__(self, source: Sequence):
            self.source = source

        def __iter__(self):
            yield from self.source

        def __getitem__(self, item):
            return self.source[item]

        def __len__(self):
            return len(self.source)

        def __str__(self):
            return '\n'.join(str(r) for r in self)

        def bar(self, autoshow=True):
            import matplotlib.pyplot as plt

            plt.bar(
                range(len(self)), [float(r) for r in self], tick_label=[str(r.runner) for r in self]
            )
            plt.ylabel('seconds / run')

            comparisons = [self[0], None]
            for i, result in enumerate(self):
                msg = [f'{float(result):.2e} sec']
                for cmp in comparisons:
                    if (not cmp) or cmp <= 0 or cmp == result:
                        continue
                    msg.append(f'{result / cmp:.1f}x {cmp.runner}')

                plt.text(i, float(result) / 2, '\n'.join(msg), ha='center', va='center', wrap=True)
                if result not in comparisons:
                    comparisons[-1] = result

            if autoshow:
                plt.show()


class TimeLimitCoach(Coach):
    def __init__(self, time_limit, **kwargs):
        super().__init__(**kwargs)
        self.time_limit = time_limit

    def iter_argsets(self, timer) -> Iterable[ArgSet_Raw]:
        while timer < self.time_limit:
            for argset in super().iter_argsets(timer):
                yield argset


class ArgCoach(Coach):
    def __init__(self, n: int = 1, argsets: Iterable[ArgSet] = ((),), **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.argsets = argsets

    def iter_argsets(self, timer) -> Iterable[ArgSet_Raw]:
        for _ in range(self.n):
            for argset in self.argsets:
                yield parse_argset(argset)
