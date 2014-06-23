#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from skew import __version__


packages = [
    'skew',
]

requires = [
    'botocore>=0.49.0',
    'jmespath>=0.4.1'
]


setup(
    name='skew',
    version=__version__,
    description='Unique IDs to find and inspect cloud resources.',
    long_description=open('README.md').read(),
    author='Mitch Garnaat',
    author_email='mitch@garnaat.com',
    url='https://github.com/scopely-devops/skew',
    packages=packages,
    package_dir={'skew': 'skew'},
    install_requires=requires,
    license=open("LICENSE").read(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ),
)
