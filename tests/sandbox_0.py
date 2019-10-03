import numpy as np

import matplotlib

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')

from time_me import *

vals = [i for i in range(1000) if i % 7 != 0]
coach = TimeLimitCoach(0.5)
queries = np.random.randint(0, 1000, 1000)


@coach.trial()
def _(cls):
    o = cls(vals)
    ret = 0
    for q in queries:
        if q in o:
            ret += 1
    return ret


_(frozenset)
_(set)
#_(list)
#_(tuple)
_(dict.fromkeys, __name__ = 'dict')

coach.compare().bar()
