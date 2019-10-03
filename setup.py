import setuptools

import time_me

setuptools.setup(
    name=time_me.__name__,
    version=time_me.__version__,
    author=time_me.__author__,
    url=r'https://github.com/bentheiii/time_me',
    packages=['time_me'],
    extras_require={
        'bar plots': ['matplotlib']
    },
    python_requires='>=3.7.0',
)
