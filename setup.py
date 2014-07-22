#!/usr/bin/env python2

from pkg_resources import resource_string
from setuptools import setup, find_packages

tests_require = [
    'nose>=1.0',
    'coverage',
    'nosexcover',
    'mock>=1.0'
]


setup(
    name='OmniHack',
    version='0.0.1',
    description='A collection of Python containers for data analysis',
    author='Eugene Scherba',
    author_email='escherba@gmail.com',
    url='http://about.me/escherba',
    license="MIT",
    keywords="mapping key-value container data analysis algorithm",
    packages=find_packages(exclude=['tests']),
    test_suite="nose.collector",
    zip_safe=True,
    setup_requires=tests_require,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
    ],
    long_description=resource_string(__name__, 'README.rst'),
)
