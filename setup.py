#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found")
    read_md = lambda f: open(f, 'r').read()

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

try:
    readme = read_md('README.md')
except:
    readme = ""
try:
    changelog = read_md('CHANGELOG.md')
except:
    changelog = ""

setup(
    name='rockettm',
    version='2.1.10',
    description='Rocket task manager',
    long_description=readme + '\n\n' + changelog,
    author='Alberto Galera Jimenez',
    author_email='galerajimenez@gmail.com',
    url='https://github.com/kianxineki/rockettm',
    py_modules=['rockettm', 'rockettm_server'],
    include_package_data=True,
    install_requires=['amqp', 'kombu', 'timekiller', 'basicevents'],
    license="GPL",
    zip_safe=False,
    keywords='rockettm',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    entry_points={
        'console_scripts': [
            'rockettm_server = rockettm_server:main'
        ]
    },
)
