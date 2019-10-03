from io import StringIO

import matplotlib

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')

from time_me import *

strings = [str(i) for i in range(1000)]
coach = TimeLimitCoach(0.1, sanity_argsets={
    (): ''.join(strings)
})


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


coach.compare().bar()
