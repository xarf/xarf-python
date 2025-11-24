# Development Guide

This guide covers local development setup, IDE configuration, and pre-commit hooks for the XARF Python parser project.

## Quick Start

```bash
# Clone and install
git clone https://github.com/xarf/xarf-python.git
cd xarf-python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev,test]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest --cov=xarf --cov-report=term-missing -v tests/
```

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to ensure code quality before commits.

### Installation

```bash
pip install pre-commit
pre-commit install
```

### Hooks Configuration

The `.pre-commit-config.yaml` file configures the following checks:

**Required (Blocking):**
- **black** - Code formatting (88 character line length)
- **isort** - Import sorting (black profile)
- **flake8** - Linting (with docstring checks)
- **bandit** - Security vulnerability scanning
- **mypy** - Static type checking
- **vulture** - Dead code detection
- **radon cc** - Code complexity check
- **radon mi** - Maintainability index check
- **pydocstyle** - Docstring style (Google convention)

**File Validation:**
- **check-yaml** - YAML syntax validation
- **check-json** - JSON syntax validation
- **check-toml** - TOML syntax validation
- **end-of-file-fixer** - Ensures files end with newline
- **trailing-whitespace** - Removes trailing whitespace
- **check-added-large-files** - Prevents commits of large files (>1MB)
- **check-merge-conflict** - Detects merge conflict markers
- **check-case-conflict** - Detects case conflicts
- **detect-private-key** - Detects private keys
- **mixed-line-ending** - Ensures consistent LF line endings

**Security:**
- **python-safety-dependencies-check** - Checks dependencies for known vulnerabilities

### Running Hooks

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Run hooks on staged files only (automatic on commit)
pre-commit run

# Update hook versions
pre-commit autoupdate
```

### Bypassing Hooks (Not Recommended)

```bash
# Skip all hooks for one commit
git commit --no-verify -m "message"

# Skip specific hooks
SKIP=flake8,mypy git commit -m "message"
```

## IDE Configuration

### VS Code

The `.vscode/` directory contains shared configuration:

**Files:**
- `settings.json` - Python settings, linting, formatting
- `extensions.json` - Recommended extensions
- `tasks.json` - Predefined tasks (test, lint, format)
- `launch.json` - Debug configurations

**Recommended Extensions:**
- Python (`ms-python.python`)
- Pylance (`ms-python.vscode-pylance`)
- Black Formatter (`ms-python.black-formatter`)
- isort (`ms-python.isort`)
- Mypy Type Checker (`ms-python.mypy-type-checker`)
- Flake8 (`ms-python.flake8`)
- GitLens (`eamodio.gitlens`)
- Error Lens (`usernamehw.errorlens`)
- Test Explorer (`littlefoxteam.vscode-python-test-adapter`)

**Usage:**
1. Open project in VS Code
2. Install recommended extensions (VS Code will prompt)
3. Select Python interpreter: `.venv/bin/python`
4. Format on save is enabled by default
5. Run tasks with `Cmd+Shift+P` → "Tasks: Run Task"

**Available Tasks:**
- Install Dependencies
- Run Tests
- Run Tests with Coverage
- Format Code (Black)
- Sort Imports (isort)
- Lint (flake8)
- Type Check (mypy)
- Security Scan (bandit)
- Dead Code Check (vulture)
- Code Quality - All Checks
- Pre-commit Run All
- Install Pre-commit Hooks
- Build Package
- Clean Build Artifacts

### IntelliJ IDEA / PyCharm

The `.idea/` directory contains shared configuration:

**Files:**
- `inspectionProfiles/Project_Default.xml` - Code inspection settings
- `codeStyles/Project.xml` - Code style (compatible with Black)
- `runConfigurations/` - Predefined run configurations
- `vcs.xml` - Git integration
- `misc.xml` - Python interpreter settings

**Run Configurations:**
- **Tests** - Run pytest with coverage
- **Format Code (Black)** - Format all code
- **Pre-commit All** - Run all pre-commit hooks

**Plugins Required:**
- Python (built-in)
- .ignore
- Requirements
- Black (optional but recommended)

**Usage:**
1. Open project in IntelliJ IDEA/PyCharm
2. Configure Python interpreter: Settings → Project → Python Interpreter → Add → Virtualenv → `.venv`
3. Inspection profile and code style are automatically applied
4. Run configurations available in Run menu

## Code Quality Standards

### Code Style

- **Line Length**: 88 characters (Black default)
- **Import Sorting**: Black profile with isort
- **Docstrings**: Google style convention
- **Type Hints**: Required for all public functions

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=xarf --cov-report=html

# Run specific test
pytest tests/test_parser.py::test_parse_messaging

# Run with verbose output
pytest -v
```

### Coverage Requirements

- Minimum coverage: 80%
- All public APIs must be tested
- Edge cases must be covered

### Type Checking

```bash
# Check types
mypy xarf/

# Generate HTML report
mypy xarf/ --html-report ./mypy-report
```

### Security Scanning

```bash
# Scan for vulnerabilities
bandit -r xarf/ -ll

# Check dependencies
pip-audit
```

### Dead Code Detection

```bash
# Find dead code
vulture xarf/ .vulture_whitelist.py --min-confidence 80
```

## CI/CD Pipeline

### GitHub Actions

The CI pipeline (`.github/workflows/ci.yml`) runs on:
- Push to `main` branch
- Pull requests to `main` branch

**Jobs:**

1. **Python X.X Tests** (matrix: 3.8, 3.9, 3.10, 3.11, 3.12)
   - Install dependencies
   - Run pytest with coverage
   - Upload coverage to Codecov (Python 3.11 only)

2. **Code Quality** (matrix of 9 required checks)
   - Format (black) ✅ Required
   - Imports (isort) ✅ Required
   - Linting (flake8) ✅ Required
   - Security (bandit) ✅ Required
   - Types (mypy) ✅ Required
   - Complexity (radon) ✅ Required
   - Maintainability (radon) ✅ Required
   - Docstrings (pydocstyle) ✅ Required
   - Dead code (vulture) ✅ Required

### Local CI Simulation

```bash
# Run all CI checks locally
./scripts/ci_check.sh  # If available

# Or manually:
black --check .
isort --check-only --profile black .
flake8 xarf/ tests/
bandit -r xarf/ -ll
mypy xarf/
vulture xarf/ .vulture_whitelist.py --min-confidence 80
pytest --cov=xarf --cov-report=term -v tests/
```

## Troubleshooting

### Pre-commit Issues

**Problem**: `RuntimeError: failed to find interpreter for python3.8`
**Solution**: Update `.pre-commit-config.yaml` to remove `language_version: python3.8` from black hook, or install Python 3.8

**Problem**: Hooks are slow on first run
**Solution**: Normal behavior - hooks cache dependencies for subsequent runs

**Problem**: Hook failed but changes look correct
**Solution**: Check if files were auto-fixed by hooks, stage changes and commit again

### IDE Issues

**VS Code: Python not found**
**Solution**: Set interpreter path to `.venv/bin/python` in Command Palette

**IntelliJ: Inspection errors**
**Solution**: Invalidate caches (File → Invalidate Caches → Invalidate and Restart)

**Both: Pre-commit not running**
**Solution**: Verify hooks installed with `pre-commit install`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for full contribution guidelines.

Quick checklist:
1. ✅ Create feature branch from `main`
2. ✅ Install pre-commit hooks
3. ✅ Write tests for new features
4. ✅ Ensure all tests pass
5. ✅ Ensure all pre-commit hooks pass
6. ✅ Update documentation
7. ✅ Create pull request

---

**Need Help?** Open an issue on [GitHub](https://github.com/xarf/xarf-python/issues)
