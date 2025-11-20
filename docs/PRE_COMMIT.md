# Pre-commit Hooks Configuration

This project uses [pre-commit](https://pre-commit.com/) to maintain code quality and consistency.

## Installed Hooks

The following hooks are configured in `.pre-commit-config.yaml`:

1. **pygrep-hooks** - Python-specific checks
   - `python-check-mock-methods` - Validates mock method calls

2. **pre-commit-hooks** - General file formatting
   - `trailing-whitespace` - Removes trailing whitespace
   - `end-of-file-fixer` - Ensures files end with a newline
   - `mixed-line-ending` - Detects mixed line endings

3. **isort** - Import sorting
   - Automatically sorts Python imports
   - Configured with black profile for compatibility

4. **autoflake** - Removes unused imports and variables
   - `--remove-all-unused-imports`
   - `--remove-unused-variables`
   - `--ignore-init-module-imports`

5. **black** - Code formatting
   - Enforces consistent Python code style
   - Line length: 88 characters

6. **flake8** - Linting
   - Checks code quality and style
   - Max line length: 88 characters
   - Extends ignore: E203 (whitespace before ':')

7. **mypy** - Type checking
   - Static type checking with strict mode
   - Additional dependencies: types-requests, types-PyYAML, types-python-dateutil, pydantic

8. **pydocstyle** - Docstring style checking
   - Enforces Google-style docstrings
   - Only checks xarf/ directory
   - Ignores: D100, D104, D105, D107

9. **bandit** - Security scanning
   - Detects common security issues
   - Configured via pyproject.toml

10. **radon** - Complexity checking
    - Checks cyclomatic complexity
    - Minimum threshold: B
    - Only checks xarf/ directory

## Installation

1. Install pre-commit and required tools:
   ```bash
   pip install pre-commit radon autoflake pydocstyle bandit
   ```

2. Install the git hooks:
   ```bash
   pre-commit install
   ```

## Usage

### Automatic (on commit)
Once installed, the hooks run automatically on `git commit`. They will:
- Check and fix formatting issues
- Block the commit if there are errors
- Show which files were modified

### Manual Execution

Run all hooks on all files:
```bash
./scripts/run-precommit.sh run --all-files
```

Or using pre-commit directly:
```bash
source venv/bin/activate
export PIP_INDEX_URL=https://pypi.org/simple/
pre-commit run --all-files
```

Run specific hook:
```bash
./scripts/run-precommit.sh run black --all-files
```

Run on specific files:
```bash
./scripts/run-precommit.sh run --files xarf/parser.py
```

### Update Hooks

Update all hooks to their latest versions:
```bash
./scripts/run-precommit.sh autoupdate
```

### Skip Hooks (not recommended)

To skip hooks temporarily:
```bash
git commit --no-verify -m "Your message"
```

## Configuration Files

### .pre-commit-config.yaml
Main pre-commit configuration file defining all hooks and their settings.

### pyproject.toml
Contains tool-specific configuration for:
- `[tool.black]` - Black formatter settings
- `[tool.isort]` - Import sorting settings
- `[tool.mypy]` - Type checking settings
- `[tool.flake8]` - Linting settings
- `[tool.pydocstyle]` - Docstring style settings
- `[tool.bandit]` - Security scanning settings

## Troubleshooting

### Authentication Issues with Custom PyPI

If you encounter authentication errors with custom PyPI repositories:
```bash
export PIP_INDEX_URL=https://pypi.org/simple/
pre-commit run --all-files
```

Or use the provided helper script:
```bash
./scripts/run-precommit.sh run --all-files
```

### Hook Failures

If a hook fails:
1. Read the error message carefully
2. Fix the reported issues manually
3. Stage the fixed files
4. Try committing again

Some hooks auto-fix issues (isort, black, autoflake). If files are modified:
1. Review the changes
2. Stage the modified files: `git add .`
3. Commit again

### Clearing Hook Cache

If hooks behave unexpectedly:
```bash
pre-commit clean
pre-commit install --install-hooks
```

## CI Integration

Pre-commit hooks should also run in CI/CD pipelines. Example GitHub Actions workflow:

```yaml
name: Pre-commit Checks

on: [push, pull_request]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install pre-commit
      - name: Run pre-commit
        run: |
          export PIP_INDEX_URL=https://pypi.org/simple/
          pre-commit run --all-files
```

## Best Practices

1. **Run before committing**: Test your changes with `pre-commit run --all-files`
2. **Keep hooks updated**: Run `pre-commit autoupdate` regularly
3. **Don't skip hooks**: They catch issues early
4. **Fix root causes**: Don't just bypass checks
5. **Configure per-project**: Adjust settings in pyproject.toml as needed

## Additional Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Code Style](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
