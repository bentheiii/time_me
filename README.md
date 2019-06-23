# Time_Me
time_me is a utility package to easily compare performance of different function implementations.
```
from io import StringIO

from time_me import TimeLimitCoach

strings = [str(i) for i in range(1000)]
coach = TimeLimitCoach(  # a coach is the object that keeps track of all the measurements
    0.1,  # create this coach to run each function as many times as it can, up to 0.1 seconds
    sanity_argsets={
        (): ''.join(strings)
    }  # before measuring each function, make sure it returns the values
)


@coach.measure
def add():
    ret = ''
    for i in strings:
        ret += i
    return ret


@coach.measure
def join():
    return ''.join(strings)


@coach.measure
def buffer():
    ret = StringIO()
    ret.writelines(strings)
    return ret.getvalue()


print(coach.compare())
# or
coach.compare().bar()
```