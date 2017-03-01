python_files := find . -path '*/.*' -prune -o -name '*.py' -print0

all: test

clean:
	find . \( -name '*.pyc' -o -name '*.pyo' -o -name '*~' \) -print -delete >/dev/null
	find . -name '__pycache__' -exec rm -rvf '{}' + >/dev/null

autopep8:
	@echo 'Auto Formatting...'
	@$(python_files) | xargs -0 autopep8 --max-line-length 120 --jobs 0 --in-place --aggressive

lint:
	@echo 'Linting...'
	@pylint --rcfile=pylintrc shopify_python tests.shopify_python
	@mypy shopify_python tests/shopify_python --ignore-missing-imports

autolint: autopep8 lint

run_tests: clean
	py.test --durations=10 .

test: autopep8 lint run_tests

setup_dev:
	pip install -e .[dev]

setup:
	pip install .
