# Panini
A natural language processing toolkit for Indian languages

# Dev Setup

```bash
# Install system dependencies
make bootstrap

# If you want to install global dependencies at a user level
# make bootstrap-user

# Setup python environment and install dependencies
make install
```


## Useful Make targets

- `make format`: This formats code and sorts your imports to make everything flake8 compatible
- `make test`: This runs all test cases in `<project_root>/tests`
- `make test-coverage`: This runs all test cases in `<project_root>/tests` and creates a coverage report
- `make lint`: Runs flake8 and validates code formatting
