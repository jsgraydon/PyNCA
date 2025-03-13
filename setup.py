#!/usr/bin/env python

"""
Call `pip install -e .` to install package locally for testing.
"""

from setuptools import setup, find_packages

# build command
setup(
    name="PyNCA",
    version="0.1.0",
    packages=find_packages(include=["pynca", "pynca.*"]),
    install_requires=["numpy", "pandas", "plotly", "scipy"],
    author="James Graydon",
    author_email="jsg2239@columbia.edu",
    license="GPLv3",
    description="A package for performing NCAs in Python",
    classifiers=["Programming Language :: Python :: 3"],
    entry_points={
        "console_scripts": [
            "pynca=pynca.__main__:main",
        ],
    },
)
