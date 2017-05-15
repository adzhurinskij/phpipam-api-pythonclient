#!/usr/bin/env python

import os
import os.path as path
import fnmatch
from itertools import chain
from setuptools import setup, find_packages
from pip.req import parse_requirements

def get_data_files(dirs, rewrites, exclude_dirs, exclude_files):
    """
    Collect data from the specified dirs and provide them in
    distutils-friendly format.
    """
    def _get_data_files(topdir):
        data_files = []
        for dirname, dirnames, filenames in os.walk(topdir):
            if dirname in exclude_dirs:
                continue
            files = []
            for filename in filenames:
                for pattern in exclude_files:
                    if fnmatch.fnmatch(filename, pattern):
                        break
                else:
                    files.append(path.join(dirname, filename))
            if not files:
                continue
            location = None
            for from_d, to_d in rewrites:
                if dirname.startswith(from_d):
                    location = path.join(to_d, path.relpath(dirname, from_d))
                    location = path.normpath(location)
            if location is None:
                location = dirname
            data_files.append((location, files))
        return data_files

    files = map(_get_data_files, dirs)
    # Flatten list
    return list(chain.from_iterable(files))

def install_reqs():
    return [str(ir.req) for ir in parse_requirements('requirements.txt', session='hack')]


# Settings for collecting additional data files.
# Normally you should just recreate structure of the directories
# from the root in 'data' dir and everything will work.
#
# Pathes from where data files will be collected.
DIRS = []
# Rewrite rules. In this example all files below 'data' will be placed
# to the root of the resulted package.
REWRITES = [('/')]
# Your could exclude dirs
EXCLUDE_DIRS = []
# or separate files. Wildcard characters are supported.
EXCLUDE_FILES = []

setup(
    author='Alexandr Dzhurinskij',
    author_email='adzhurinskij@gmail.com',
    license='MIT',
    name='phpipam-api-pythonclient',
    version='0.1.1',
    url='https://github.com/adzhurinskij/phpipam-api-pythonclient',
    description='Python Library for PHPIPAM API',
    packages=find_packages(),
    entry_points={},

    # This line includes additional data files to the resulting package.
    # You could tune settings with the variables above.
    data_files=get_data_files(DIRS, REWRITES, EXCLUDE_DIRS, EXCLUDE_FILES),
    include_package_data=True,
    install_requires=install_reqs()
)

