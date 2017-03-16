#!/usr/bin/env python
# Copyright (c) 2017 "Shopify inc." All rights reserved.
# Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
import re

try:
    import setuptools as setuplib
except ImportError:
    import distutils.core as setuplib


def get_version():
    version = None
    with open('shopify_python/__init__.py', 'r') as fdesc:
        version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fdesc.read(), re.MULTILINE).group(1)
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


setuplib.setup(
    name='shopify_python',
    version=get_version(),
    description='Python Standards Library for Shopify',
    url='http://github.com/shopify/shopify_python',
    author='Shopify Data Acceleration',
    author_email='data-acceleration@shopify.com',
    license='MIT',
    packages=['shopify_python'],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
    ],
    test_suite='tests',
    install_requires=[
        'GitPython==2.1.1',
        'pylint==1.6.5',
        'six>=1.10.0',
        'typing>=3.5.3.0',
    ],
    extras_require={
        'dev': [
            'autopep8',
            'mock; python_version < "3.3"',
            'mypy; python_version >= "3.3"',
            'pep8',
            'pytest',
            'pytest-randomly',
        ]
    }
)
