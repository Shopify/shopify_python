#!/usr/bin/env python
# Copyright (c) 2017 "Shopify inc." All rights reserved.
# Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
import re

try:
    import setuptools as setuplib
except:
    import distutils.core as setuplib


with open('shopify_python/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setuplib.setup(
    name='shopify_python',
    version=version,
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
        'pylint==1.6.5',
        'six>=1.10.0',
    ],
    extras_require={
        'dev': [
            'autopep8',
            'pytest',
            'pytest-randomly',
            'mypy; python_version > "3.3"',
        ]
    }
)
