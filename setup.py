#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

project_root = os.path.dirname(__file__)

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

long_description = ''

try:
    from contextlib import suppress
    with suppress(OSError):
        with open(os.path.join(project_root, 'README.md'), 'rt') as readme_fh:
            long_description = readme_fh.read()
except ImportError:
    with open(os.path.join(project_root, 'README.md'), 'rt') as readme_fh:
        long_description = readme_fh.read()

setup(
    name='searchguard',
    version='0.7',
    packages=find_packages(exclude=['tests']),
    license='MIT',
    url='https://github.com/ByteInternet/searchguard-python',
    author='Jeroen van Heugten',
    author_email='jeroen@byte.nl',
    classifiers=classifiers,
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'requests==2.20'
    ],
)

