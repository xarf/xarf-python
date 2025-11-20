# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the XARF Parser Python project.

## Workflows

### 1. Quality Checks (`quality-checks.yml`)

**Trigger:** Push, Pull Request, Manual

Runs comprehensive code quality and security checks in parallel:

#### Blocking Checks (Must Pass)
- **Import Ordering (isort)**: Ensures consistent import organization
- **Code Formatting (black)**: Validates code follows Black formatting
- **Code Style (flake8)**: Checks PEP 8 compliance
- **Security Scan (bandit)**: Scans for security vulnerabilities in code

#### Non-Blocking Checks (Warning Only)
- **Type Hints (mypy)**: Validates type annotations
- **Docstring Coverage (pydocstyle)**: Checks documentation quality
- **Complexity Metrics (radon)**: Measures code complexity
- **Test Coverage (pytest-cov)**: Measures test coverage percentage

**Matrix Strategy:** All checks run in parallel for faster feedback

**Artifacts:**
- Coverage reports (JSON and HTML)
- Check logs on failure

### 2. Security Scan (`security-scan.yml`)

**Trigger:** Weekly (Monday 9 AM UTC), Push to main, Pull Request, Manual

Performs comprehensive security scanning:

#### Scans
- **pip-audit**: Checks dependencies for known CVEs
- **bandit**: Scans Python code for security issues
- **trivy**: Filesystem scan for secrets and vulnerabilities

**Features:**
- Uploads results to GitHub Security tab (SARIF format)
- Creates GitHub issue automatically on weekly scan failures
- Stores scan results as artifacts for 90 days

**Permissions Required:**
- `contents: read` - Read repository
- `issues: write` - Create security issues
- `security-events: write` - Upload to Security tab

### 3. Tests (`test.yml`)

**Trigger:** Push, Pull Request, Manual

Runs comprehensive test suite across multiple environments:

#### Test Matrix
- **Python Versions:** 3.8, 3.9, 3.10, 3.11, 3.12
- **Operating Systems:**
  - Ubuntu (all Python versions)
  - macOS (Python 3.12 only)
  - Windows (Python 3.12 only)

#### Additional Tests
- **Minimum Versions Test:** Validates compatibility with oldest supported dependencies
- **Integration Tests:** Runs on push/manual trigger only

**Features:**
- Coverage reports uploaded to Codecov (Python 3.11 on Ubuntu)
- Test results preserved as artifacts
- Coverage HTML reports for all Ubuntu runs

**Artifacts:**
- Coverage reports per Python version
- Test results per platform/version
- Integration test results

### 4. Publish (`publish.yml`)

**Trigger:** GitHub Release, Manual

Publishes package to PyPI or Test PyPI:

#### Workflow Steps
1. **Validate Release**
   - Extracts version from `pyproject.toml`
   - Validates version format (semver)
   - Ensures tag matches package version

2. **Run Tests**
   - Calls test workflow
   - Ensures all tests pass before publishing

3. **Run Quality Checks**
   - Runs formatting and style checks
   - Prevents publishing broken code

4. **Build Distribution**
   - Creates wheel and source distribution
   - Validates with twine
   - Uploads as artifacts

5. **Publish**
   - **Test PyPI**: Prerelease versions or manual dispatch with flag
   - **PyPI**: Production releases

**Manual Trigger Options:**
- `test_pypi`: Boolean flag to publish to Test PyPI instead of PyPI

**Permissions Required:**
- `id-token: write` - Trusted publishing to PyPI (no API token needed)
- `contents: read` - Read repository

**Environments:**
- `test-pypi`: For test.pypi.org
- `pypi`: For pypi.org

## Setup Instructions

### 1. PyPI Publishing Setup

Configure Trusted Publishing (recommended):

1. Go to PyPI account settings
2. Navigate to "Publishing" → "Add a new publisher"
3. Fill in:
   - **PyPI Project Name:** `xarf-parser`
   - **Owner:** Your GitHub username/org
   - **Repository:** `xarf-parser-python`
   - **Workflow:** `publish.yml`
   - **Environment:** `pypi`

Repeat for Test PyPI with environment `test-pypi`.

### 2. Codecov Integration (Optional)

1. Sign up at [codecov.io](https://codecov.io)
2. Connect your GitHub repository
3. No token configuration needed for public repos

### 3. GitHub Security Tab

No setup required - workflows automatically upload SARIF reports.

## Running Workflows Locally

### Quality Checks
```bash
# Install tools
pip install black==24.3.0 flake8==7.0.0 isort==5.13.2 \
            mypy==1.9.0 pydocstyle==6.3.0 radon==6.0.1 \
            bandit==1.7.8

# Run individual checks
black --check xarf/ tests/
flake8 xarf/ tests/ --max-line-length=88 --extend-ignore=E203,W503
isort --check-only --profile black xarf/ tests/
mypy --config-file=pyproject.toml xarf/
pydocstyle xarf/
radon cc --min B --show-complexity xarf/
bandit -r xarf/
```

### Tests
```bash
# Install dependencies
pip install -e ".[dev,test]"

# Run tests with coverage
pytest --cov=xarf --cov-report=term --cov-report=html tests/
```

### Security Scans
```bash
# Dependency audit
pip install pip-audit
pip-audit

# Code security
bandit -r xarf/ -f txt

# Trivy (requires Docker)
docker run --rm -v $(pwd):/workspace aquasec/trivy fs /workspace
```

### Build Package
```bash
# Install build tools
pip install build twine

# Build
python -m build

# Check
twine check dist/*
```

## Workflow Badges

Add these to your README.md:

```markdown
[![Quality Checks](https://github.com/xarf/xarf-parser-python/actions/workflows/quality-checks.yml/badge.svg)](https://github.com/xarf/xarf-parser-python/actions/workflows/quality-checks.yml)
[![Security Scan](https://github.com/xarf/xarf-parser-python/actions/workflows/security-scan.yml/badge.svg)](https://github.com/xarf/xarf-parser-python/actions/workflows/security-scan.yml)
[![Tests](https://github.com/xarf/xarf-parser-python/actions/workflows/test.yml/badge.svg)](https://github.com/xarf/xarf-parser-python/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/xarf/xarf-parser-python/branch/main/graph/badge.svg)](https://codecov.io/gh/xarf/xarf-parser-python)
[![PyPI version](https://badge.fury.io/py/xarf-parser.svg)](https://badge.fury.io/py/xarf-parser)
```

## Troubleshooting

### Quality Checks Failing

**Import ordering fails:**
```bash
isort --profile black xarf/ tests/
```

**Formatting fails:**
```bash
black xarf/ tests/
```

**Type checking fails:**
- Add type hints to functions
- Update `pyproject.toml` mypy configuration

### Security Scan Failing

**Dependency vulnerabilities:**
```bash
pip-audit --fix
# Or update specific packages
pip install --upgrade <package>
```

**Code security issues:**
- Review bandit output
- Add `# nosec` comment with justification if false positive

### Tests Failing

**Coverage too low:**
- Add more test cases
- Remove unused code
- Update coverage thresholds in `pyproject.toml`

**Platform-specific failures:**
- Check for hardcoded paths
- Use `pathlib` for cross-platform compatibility

### Publishing Failing

**Version mismatch:**
- Ensure git tag matches `pyproject.toml` version
- Use `v` prefix in tags (e.g., `v4.0.0`)

**Tests not passing:**
- All tests must pass before publishing
- Check test workflow results

**PyPI authentication:**
- Ensure Trusted Publishing is configured
- Check environment names match

## Best Practices

1. **Run quality checks locally before pushing**
2. **Keep dependencies updated** (use `pip-audit --fix`)
3. **Maintain test coverage** above 80%
4. **Use semantic versioning** for releases
5. **Test with minimum dependency versions** periodically
6. **Review security scan results** weekly
7. **Keep workflows updated** with latest action versions

## CI/CD Pipeline Overview

```
Push/PR → Quality Checks ──┐
                           ├─→ Must Pass
       → Tests ────────────┤
                           └─→ Merge
Release → Validate ──→ Build ──→ Publish → PyPI
```

## Maintenance

- **Weekly:** Review security scan results
- **Monthly:** Update action versions
- **Quarterly:** Review and update tool versions
- **On Python release:** Add new Python version to test matrix

## Support

For issues with workflows, open an issue in the repository with:
- Workflow name
- Run ID
- Error message
- Expected behavior
