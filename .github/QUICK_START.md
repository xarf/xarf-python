# CI/CD Quick Start Guide

## First Time Setup

### 1. Enable GitHub Environments
```
Settings → Environments → New environment
- Create "test-pypi" (optional reviewers)
- Create "pypi" (require reviewers, main branch only)
```

### 2. Configure PyPI Trusted Publishing
**On PyPI.org:**
```
Account Settings → Publishing → Add GitHub OIDC publisher
- Repository: xarf/xarf-parser-python
- Workflow: publish-pypi.yml
- Environment: pypi
```

**On Test PyPI (test.pypi.org):**
```
Same steps but with environment: test-pypi
```

### 3. Enable Branch Protection
```
Settings → Branches → Add rule
Branch: main
☑ Require status checks:
  - Quality Checks / quality-checks
  - Test Suite / test
  - CI Summary / ci-summary
☑ Require PR reviews: 1 approval
```

## Testing the Pipeline

### Test PR Workflow
```bash
git checkout -b test-pipeline
echo "# test" >> README.md
git add . && git commit -m "Test CI"
git push origin test-pipeline
# Create PR on GitHub
```

### Test Security Scan
```
GitHub → Actions → Security Scan → Run workflow
```

### Test Publishing (Test PyPI)
```
GitHub → Actions → Publish to PyPI → Run workflow
Select: ☑ Publish to Test PyPI
```

### Test Release (Production)
```bash
git tag v4.0.0
git push origin v4.0.0
# Create release on GitHub → publishes automatically
```

## Common Commands

### Run Tests Locally
```bash
pip install -e ".[dev,test]"
pytest --cov=xarf
```

### Run Quality Checks Locally
```bash
isort --check xarf/ tests/
black --check xarf/ tests/
flake8 xarf/ tests/
bandit -r xarf/
mypy xarf/
pydocstyle xarf/
radon cc --min B xarf/
```

### Run Security Scans Locally
```bash
pip-audit
bandit -r xarf/
```

## Monitoring

### Check Workflow Status
```
GitHub → Actions → View runs
```

### Check Security Issues
```
GitHub → Security → Code scanning alerts
```

### Download Artifacts
```
Actions → Workflow run → Artifacts section
```

## Troubleshooting

### Quality Checks Fail
```bash
# Fix imports
isort xarf/ tests/

# Fix formatting
black xarf/ tests/

# Show what would be fixed
black --diff xarf/
```

### Coverage Too Low
```bash
# Run with coverage report
pytest --cov=xarf --cov-report=html
open htmlcov/index.html
```

### Publishing Fails
1. Verify trusted publishing on PyPI
2. Check environment permissions
3. Ensure release is published (not draft)

## Documentation

- **Full Design**: [docs/ci-cd-pipeline-design.md](../docs/ci-cd-pipeline-design.md)
- **Workflows**: [.github/workflows/WORKFLOWS_README.md](workflows/WORKFLOWS_README.md)

---
**Need Help?** Check the troubleshooting section in ci-cd-pipeline-design.md
