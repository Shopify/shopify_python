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
        'GitPython>=2.1.1,<3',
        'pylint>=1.7.1,<1.8',
        'six>=1.10.0,<2',
        'typing>=3.5.3.0,<4',
        'autopep8>=1.2.2,<2',
    ],
    extras_require={
        'dev': [
            'pycodestyle==2.3.1',
            'pytest==3.0.6',
            'pytest-randomly==1.1.2',
        ],
        'dev: python_version < "3.3"': [
            'mock==2.0.0',
        ],
        'dev: python_version >= "3.3"': [
            'mypy==0.501',
        ]
    }
)
