# Shopify Python Standards

This repository describes Python development standards at Shopify, and provides some utilities to assist other
Python repositories adhere to these standards.

## Development Principles
- Make sure your code is readable.
- Don't hesitate to refactor code where it improves the design.
- Don't take shortcuts; development is more like a marathon than a sprint.
- And leave the code cleaner than you found it.

## Python Style

Shopify follows the [Google Python Style Guide](http://google.github.io/styleguide/pyguide.html) with the following
exceptions:
- Line Length: The maximum line length is 120 columns.
- Private Methods and Properties
  - Prefix class-private members and properties with double underscores. This invokes name-mangling, which provides some protection against violations of encapsulation.
  - Prefix module-private functions and variables with a single underscore.
- Multi-line docstrings: The first line of text (summary line) appears on the same line as the opening three double-quotes.
-  Base Class Inheritance
	- If a class or nested class inherits from no other base classes, explicitly inherit from object.
	- This won't be enforced for our pure Python 3 code, but we will enforce for Python 2 and 2/3 compatbile code.
- Variable/module-name collisions: Variable names may be suffixed with an underscore to avoid collisions with imported modules (an extension of the [PEP-8 convention](https://www.python.org/dev/peps/pep-0008/#descriptive-naming-styles) for collisions with builtins).


## Versioning

Projects that are producing libraries to be used in other projects should choose their release version numbers using [Semantic Versioning 2.0.0](http://semver.org/spec/v2.0.0.html), i.e.

> Given a version number MAJOR.MINOR.PATCH, increment the:
> 
> MAJOR version when you make incompatible API changes,
> MINOR version when you add functionality in a backwards-compatible manner, and
> PATCH version when you make backwards-compatible bug fixes.
>
> Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.

## Testing

All committed code requires quality tests that provide ample code coverage. Functionality that is not covered by tests
should be assumed to be broken (and probably will be).

## Code Review

Committing to `master` requires a code review, submitted in the form of a GitHub Pull Request. To be merged, a PR must
have an explicit approval from a core team member and no outstanding questions.


## Project Setup

To help you apply these principles this repository contains a pylint plugin and some example files to bootstrap a Python project. When beginning a Python project:

- Start with a [`pylintrc`](pylintrc) file of this form and disable messages in Python source files if needed as agreed upon by team members
  - During early development of a project, globally disabling the `fixme` and `missing-docstring` messages via `pylintrc` is acceptable but these should be removed before a 1.0.0 release of a library or a production deployment of an application
  - Install and use the `shopify_python` checker (which this [`pylintrc`](pylintrc) is configured to run) by making a `requirements.txt` entry of `git+https://github.com/Shopify/shopify_python.git@v0.1.2` (replacing `v0.1.2` with the latest version number) and installing it via pip (e.g. `pip install -r requirements.txt`)
- Use a continuous integration (CI) server such as [Travis CI](https://travis-ci.org/) (or an internal alternative) and for each PR require successful runs of:
  - [`py.test`](http://doc.pytest.org/en/latest/) to run your unit tests
    - Use the [`pytest-randomly`](https://pypi.python.org/pypi/pytest-randomly) plugin to randomize test order to eliminate test-order dependencies
  - [`pylint`](https://pylint.readthedocs.io/) to lint your code using pylint's default checkers and the `shopify_python` checker defined in this project
  - [`mypy`](http://mypy.readthedocs.io/) to check type annotations
- Use a [`Makefile`](Makefile) similar to the one used by this project to run tests/linters in a similar way on both CI and for local development (or use an internal alternative)


## Contributing

Please refer to our [Contribution Guidelines](CONTRIBUTING.md)
