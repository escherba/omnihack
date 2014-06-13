#!/usr/bin/env

import sys
if sys.version_info[0] <= 2:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup
else:
    from distutils.core import setup

setup(name='OmniHack',
      version='0.0.1',
      description='A collection of Python containers for data analysis',
      author='Eugene Scherba',
      author_email='escherba@gmail.com',
      url='http://about.me/escherba',
      license="BSD",
      keywords="mapping key-value container data analysis",
      provides=['omnihack'],
      py_modules=['omnihack'],
      test_suite="test_omni",
      zip_safe=True,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Operating System :: OS Independent',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.0',
          'Programming Language :: Python :: 3.1',
          'Programming Language :: Python :: 3.2',
          ],

      long_description=open('README.rst').read(),

      )
