# Contributing to XARF Python Library

Thank you for your interest in contributing to the XARF Python library! We welcome contributions from the community and appreciate your help in making this project better.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to admin@xarf.org.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with the following information:

- **Clear title and description** of the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs. **actual behavior**
- **Code samples** or test cases that demonstrate the issue
- **Version** of the library you're using
- **Python version** and operating system

### Suggesting Features

We welcome feature requests! Please create an issue with:

- **Clear description** of the feature
- **Use case** explaining why this feature would be useful
- **Example code** showing how the feature might work
- **Compatibility considerations** with the XARF specification

### Pull Requests

We actively welcome pull requests! Here's how to contribute:

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for any new functionality
4. **Ensure all tests pass** and coverage remains >80%
5. **Update documentation** as needed
6. **Submit a pull request** with a clear description of changes

## Development Setup

### Prerequisites

- **Python**: 3.10 or higher
- **Git**: Latest stable version

### Getting Started

1. **Clone your fork:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/xarf-python.git
   cd xarf-python
   ```

2. **Create a virtual environment and install dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks:**

   ```bash
   pre-commit install
   ```

4. **Run tests:**

   ```bash
   pytest
   ```

### Development Commands

- `pytest` — Run the test suite
- `pytest --cov=xarf` — Generate code coverage report
- `ruff check xarf/` — Lint
- `ruff check --fix xarf/` — Auto-fix lint issues
- `ruff format xarf/` — Format code
- `ruff format --check xarf/` — Check code formatting
- `mypy --strict xarf/` — Run type checking
- `bandit -r xarf/` — Security scanning

## Testing Requirements

All contributions must maintain or improve test coverage:

- **Coverage threshold**: 80% overall — enforced by `pytest-cov`
- **Unit tests**: Required for all new functions and classes
- **Integration tests**: Required for parser and generator functionality
- **Test file location**: Tests should be in the `tests/` directory
- **No schema mocking**: tests must use real schemas loaded from the bundle

### Running Tests

```bash
pytest                     # Run all tests
pytest -v                  # Verbose output
pytest --cov=xarf          # With coverage report
pytest tests/test_parse.py # Run a specific file
```

### Writing Tests

We use pytest. Example test structure:

```python
from xarf import parse

def test_parse_valid_report() -> None:
    result = parse({
        # ... valid XARF data
    })

    assert not result.errors
    assert result.report is not None
    assert result.report.category == "connection"
    assert result.report.type == "ddos"

def test_parse_returns_errors_for_invalid_data() -> None:
    result = parse({})

    assert len(result.errors) > 0
```

## Code Style Guidelines

### Python Standards

- **Language version**: Python 3.10+
- **Type annotations**: required on all public functions and methods
- **Docstrings**: Google style for all public APIs (`Args:`, `Returns:`, `Raises:`, `Example:`)
- **Strict mypy**: all code must pass `mypy --strict xarf/`

See [pyproject.toml](pyproject.toml) for the full `ruff` and `mypy` configuration.

### Naming Conventions

- **Functions / methods**: `snake_case` (e.g., `parse`, `create_report`, `create_evidence`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `SPEC_VERSION`)
- **Classes**: `PascalCase` (e.g., `ParseResult`, `XARFReport`, `SchemaRegistry`)
- **Type aliases**: `PascalCase` (e.g., `AnyXARFReport`, `ConnectionReport`)

### Code Organization

- **One module per file** for main components
- **Related types** grouped in category-specific files (`types_messaging.py`, etc.)
- **Export from `__init__.py`** for public API — use `xarf-javascript/src/index.ts` as the reference for which names to expose

### Formatting and Linting

We use `ruff` for both formatting and linting. Configuration lives in [pyproject.toml](pyproject.toml).

```bash
ruff format xarf/          # Auto-format
ruff format --check xarf/  # Check formatting
ruff check xarf/           # Lint
ruff check --fix xarf/     # Auto-fix linting issues
```

A pre-commit hook runs both automatically on staged files.

### Documentation

- **Google-style docstrings** for all public APIs
- **Type annotations** on all parameters and return values
- **Inline comments** for non-obvious logic
- **README updates** for new features

## Commit Message Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring without feature changes
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates

### Examples

```
feat(parser): add support for reputation/threat_intelligence reports

Implement Pydantic model and schema-driven validation for the
threat_intelligence report type. Includes shared test samples.

Closes #123
```

```
fix(schema_validator): deduplicate errors from master and core schemas

Errors reported by both the master schema and the core schema for the
same field were appearing twice in ValidationError lists.

Fixes #456
```

```
docs(readme): update schema management section
```

## Pull Request Process

1. **Update documentation** for any changed functionality
2. **Add tests** covering your changes
3. **Ensure all tests pass**: `pytest`
4. **Verify coverage**: `pytest --cov=xarf`
5. **Check linting**: `ruff check xarf/`
6. **Verify formatting**: `ruff format --check xarf/`
7. **Run type checking**: `mypy --strict xarf/`
8. **Update CHANGELOG.md** if applicable
9. **Create pull request** with clear description

### Pull Request Template

Your PR description should include:

- **What**: Brief description of changes
- **Why**: Motivation and context
- **How**: Implementation approach
- **Testing**: How you tested the changes
- **Breaking changes**: Any breaking changes (if applicable)
- **Related issues**: Link to related issues

### Code Review

All pull requests require review before merging:

- At least **one approval** from a maintainer
- All **CI checks must pass**
- **No unresolved discussions**
- **Merge conflicts resolved**

## XARF Specification Compliance

All implementations must conform to the [XARF specification](https://xarf.org):

- Parse all **required fields**
- Validate **data types** correctly
- Support all **standard report types**
- Handle **optional fields** appropriately
- Implement proper **error handling**
- Maintain **backward compatibility** when possible

## Release Process

Releases are managed by maintainers:

1. Version bumped following [Semantic Versioning](https://semver.org/)
2. CHANGELOG.md updated with changes
3. Git tag created for the version
4. Package published to PyPI

## Getting Help

- **Documentation**: Check the [README](README.md) and code comments
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the maintainers at contact@xarf.org

## License

By contributing to XARF Python Library, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you for contributing to XARF! Your efforts help make abuse reporting more effective and standardized across the internet.
