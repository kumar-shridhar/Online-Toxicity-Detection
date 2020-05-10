# Setup the environment

SYSTEM_DEPENDENCIES := poetry==1.0.5 pre-commit coveralls flake8

check-py37:
	./check_python37.sh


## To install system level dependencies
.PHONY: bootstrap
bootstrap: check-py37
	pip install -U $(SYSTEM_DEPENDENCIES)
	curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

## Install system dependencies in user dir (Linux)
.PHONY: bootstrap-user
bootstrap-user: check-py37
	pip install --user -U $(SYSTEM_DEPENDENCIES)

## Setup poetry
.PHONY: poetry-setup
poetry-setup:
	poetry config virtualenvs.in-project true
	poetry run pip install pip==20.0.2
	poetry install --no-root
	poetry export -f requirements.txt > requirements.txt
	poetry install
	rm requirements.txt

## Setup pre-commit
.PHONY: pre-commit-setup
pre-commit-setup:
	pre-commit install


# Setup virtual environment and dependencies
.PHONY: install
install: pre-commit-setup poetry-setup

# Format code
.PHONY: format
format:
	# calling make _format within poetry make it so that we only init poetry once
	poetry run isort -rc -y panini
	poetry run black panini


# Flake8 to check code formatting
.PHONY: lint
lint:
	poetry run flake8 .


# Run tests
.PHONY: test
test:
	poetry run pytest tests/ -s

# Run coverage
.PHONY: coverage
coverage:
	poetry run coverage report --show-missing



# Run tests and coverage
.PHONY: test-coverage
test-coverage: test coverage
