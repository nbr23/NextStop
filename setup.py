#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = "NextStop",
    version = "1.0",
    description = "Retrieve information about the next stops of French RATP services",

    author = 'nbr23',
    author_email = 'python@23.tf',

    url = 'https://github.com/nbr23/NextStop',

    classifiers = [
        'Development Status :: 5 - Production/Stable',

        'Environment :: Console',

        'Natural Language :: French',

        'Programming Language :: Python :: 3',
    ],

    install_requires = [
        'beautifulsoup4',
        'unidecode',
    ],

    packages=[
        'nextstop',
    ],

    scripts=[
        'bin/nextstop',
    ],
)
