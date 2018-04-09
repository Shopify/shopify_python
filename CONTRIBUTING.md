# Contributing

Contributions are always welcome, both reporting issues and submitting pull requests!

### Setup

Follow these steps to run the shopify_python tests:

```bash
pyenv local 3.6.3  # this is the version running on the 3.6 CI nodes
python -m venv ~/.pyenv/virtualenvs/shopify_python # or wherever you want the env to be
source ~/.pyenv/virtualenvs/shopify_python/bin/activate
make install
make run_tests
```

If all went well, you should see a number of successful tests.

### Reporting issues

Please make sure to include any potentially useful information in the issue, so we can pinpoint the issue faster without going back and forth.

- What SHA of shopify_python are you using? If this is not the latest SHA on the master branch, please try if the problem persists with the latest version.
- Inspect the output of any logs you see. If you see anything out of the ordinary, please include it.
- Include the version of pylint you are using. If you aren't running the latest compatible version, try upgrading to that version first.
- Include the details of your environment, e.g. Python version and OS.

### Submitting pull requests

We will gladly accept bug fixes, or additions to this library. Please fork this library, commit & push your changes, and open a pull request. Because this library is in production use by many people and applications, we code review all additions. To make the review process go as smooth as possible, please consider the following.

- If you plan to work on something major, please open an issue to discuss the design first.
- Don't break backwards compatibility. If you really have to, open an issue to discuss this first.
- Add tests that cover the changes you made. Make sure to run `make test`.
- Make sure your code is supported by all the Python versions we support. You can rely on [Travis CI](https://travis-ci.org/Shopify/shopify_python) for testing older Python versions
