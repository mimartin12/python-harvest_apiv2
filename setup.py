#!/usr/bin/env python

import runpy
import os
from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

TESTS_REQUIRE = [
    'coverage',
    'pytest',
    'pytest-cov',
    'mock'
]

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

metadata_filename = "harvest/metadata.py"
metadata = runpy.run_path(metadata_filename)

# http://pypi.python.org/pypi?:action=list_classifiers
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Financial and Insurance Industry",
    "Intended Audience :: Information Technology",
    "Intended Audience :: Manufacturing",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.7",
    "Topic :: Office/Business",
    "Topic :: Office/Business :: Financial",
    "Topic :: Office/Business :: Financial :: Accounting",
    "Topic :: Office/Business :: Financial :: Spreadsheet",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
    "License :: OSI Approved :: MIT License",
]

setup(
    name='python-harvest-apiv2',
    version=metadata['__version__'],
    description="Harvest API v2 client",
    long_description="Harvest Time Tracking API v2 Client",
    classifiers=classifiers,
    keywords=['Harvest',
        'harvestapp',
        'timetracking',
        'time tracking',
        'timesheet',
        'time sheet',
        'api'],
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    url='https://github.com/bradbase/python-harvest_apiv2',
    license=metadata['__license__'],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=read("requirements.txt").split("\n"),
    extras_require=dict(
        test=TESTS_REQUIRE,
        build=[
            'pip-tools',
        ],
    ),
    python_requires='>=3.7',
    tests_require=TESTS_REQUIRE,
)
