#!/usr/bin/env python

"""
Call `pip install -e .` to install package locally for testing.
"""

from setuptools import setup

# build command
setup(
    name="PyNCA",
    version="0.0.1",
    author="James Graydon",
    author_email="jsg2239@columbia.edu",
    license="GPLv3",
    description="A package for performing NCAs in Python",
    classifiers=["Programming Language :: Python :: 3"],
    entry_points={
        "console_scripts": ["PyNCA = mini-project.__main__:main"]
    },
)
