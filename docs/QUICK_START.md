# XARF Parser Python - Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/xarf/xarf-parser-python.git
cd xarf-parser-python

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Development Workflow

### 1. Before Starting Work

```bash
# Activate virtual environment
source venv/bin/activate

# Ensure dependencies are up to date
pip install -e ".[dev]"
```

### 2. During Development

```bash
# Run tests
pytest

# Run specific test
pytest tests/test_parser.py::test_basic_parsing

# Run with coverage
pytest --cov=xarf --cov-report=html
```

### 3. Before Committing

```bash
# Run all pre-commit checks
./scripts/run-precommit.sh run --all-files

# Or manually:
black xarf/ tests/
isort xarf/ tests/
flake8 xarf/ tests/
mypy xarf/
pytest
```

### 4. Committing Changes

```bash
# Stage your changes
git add .

# Commit (pre-commit hooks run automatically)
git commit -m "Your commit message"

# If hooks fail, fix issues and commit again
git add .
git commit -m "Your commit message"
```

## Pre-commit Hooks

The project uses comprehensive pre-commit hooks:

- **Formatting**: black, isort, trailing-whitespace, end-of-file-fixer
- **Linting**: flake8, autoflake
- **Type checking**: mypy
- **Docstrings**: pydocstyle
- **Security**: bandit
- **Complexity**: radon

### Common Commands

```bash
# Run all hooks on all files
./scripts/run-precommit.sh run --all-files

# Run specific hook
./scripts/run-precommit.sh run black --all-files

# Update hooks to latest versions
./scripts/run-precommit.sh autoupdate

# Skip hooks (not recommended)
git commit --no-verify
```

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=xarf --cov-report=term-missing

# Run specific test file
pytest tests/test_parser.py

# Run specific test function
pytest tests/test_parser.py::test_basic_parsing
```

## Code Style

### Black Formatting
```bash
# Format all Python files
black xarf/ tests/

# Check without modifying
black --check xarf/ tests/
```

### Import Sorting
```bash
# Sort imports
isort xarf/ tests/

# Check without modifying
isort --check-only xarf/ tests/
```

### Linting
```bash
# Run flake8
flake8 xarf/ tests/

# Run with specific config
flake8 --config=pyproject.toml xarf/
```

### Type Checking
```bash
# Run mypy
mypy xarf/

# Run with config
mypy --config-file=pyproject.toml xarf/
```

## Building and Distribution

```bash
# Build package
python -m build

# Install locally
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Install with test dependencies
pip install -e ".[test]"
```

## Common Issues

### Authentication with Custom PyPI

If you encounter PyPI authentication errors:
```bash
export PIP_INDEX_URL=https://pypi.org/simple/
```

Add to your shell profile for persistence:
```bash
echo 'export PIP_INDEX_URL=https://pypi.org/simple/' >> ~/.zshrc
```

### Pre-commit Hook Failures

1. **Automatic fixes**: Some hooks (black, isort) auto-fix issues
   - Review changes: `git diff`
   - Stage fixes: `git add .`
   - Commit again

2. **Manual fixes required**: Fix reported issues manually
   - Read error messages carefully
   - Fix the code
   - Stage and commit again

3. **Cache issues**: Clear pre-commit cache
   ```bash
   pre-commit clean
   pre-commit install --install-hooks
   ```

## Documentation

- [Pre-commit Setup](./PRE_COMMIT.md) - Detailed pre-commit documentation
- [Migration Guide](./MIGRATION_GUIDE.md) - Upgrading from older versions
- [Contributing](../CONTRIBUTING.md) - Contribution guidelines
- [Changelog](../CHANGELOG.md) - Version history

## Getting Help

- GitHub Issues: https://github.com/xarf/xarf-parser-python/issues
- XARF Specification: https://github.com/xarf/xarf-spec
- Email: contact@xarf.org

## Quick Reference

| Command | Description |
|---------|-------------|
| `pytest` | Run tests |
| `pytest --cov=xarf` | Run tests with coverage |
| `black xarf/ tests/` | Format code |
| `isort xarf/ tests/` | Sort imports |
| `flake8 xarf/` | Lint code |
| `mypy xarf/` | Type check |
| `./scripts/run-precommit.sh run --all-files` | Run all hooks |
| `pre-commit autoupdate` | Update hooks |
| `pip install -e ".[dev]"` | Install with dev deps |

## Environment Variables

```bash
# Use public PyPI (avoids auth issues)
export PIP_INDEX_URL=https://pypi.org/simple/

# Set Python version for mypy
export MYPY_PYTHON_VERSION=3.8

# Increase pytest verbosity
export PYTEST_ADDOPTS="-v"
```
