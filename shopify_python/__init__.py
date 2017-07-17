# Copyright (c) 2017 "Shopify inc." All rights reserved.
# Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
from __future__ import unicode_literals

from pylint import lint
from shopify_python import google_styleguide
from shopify_python import shopify_styleguide


__version__ = '0.4.2'


def register(linter):  # type: (lint.PyLinter) -> None
    google_styleguide.register_checkers(linter)
    shopify_styleguide.register_checkers(linter)
