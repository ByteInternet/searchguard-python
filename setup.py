#!/usr/bin/env python3

from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

setup(
    name='searchguard',
    version='0.2',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/ByteInternet/searchguard-python',
    author='Jeroen van Heugten',
    author_email='jeroen@byte.nl',
    classifiers=classifiers,
    long_description_content_type="text/markdown",
    install_requires=[
        'requests==2.9.1'
    ],
)

