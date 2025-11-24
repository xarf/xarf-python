# IDE Setup Guide

Quick reference for setting up your development environment with VS Code or IntelliJ IDEA.

## VS Code Setup

### 1. Install VS Code
Download from [code.visualstudio.com](https://code.visualstudio.com/)

### 2. Open Project
```bash
cd xarf-python
code .
```

### 3. Install Recommended Extensions
VS Code will prompt to install recommended extensions. Click "Install All" or install manually:

- **Python** (`ms-python.python`) - Core Python support
- **Pylance** (`ms-python.vscode-pylance`) - Fast type checking
- **Black Formatter** (`ms-python.black-formatter`) - Auto-formatting
- **isort** (`ms-python.isort`) - Import sorting
- **Mypy Type Checker** (`ms-python.mypy-type-checker`) - Type checking
- **Flake8** (`ms-python.flake8`) - Linting
- **GitLens** (`eamodio.gitlens`) - Git integration
- **Error Lens** (`usernamehw.errorlens`) - Inline error display

### 4. Select Python Interpreter
1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Python: Select Interpreter"
3. Choose `.venv/bin/python`

### 5. Verify Configuration
- Open any Python file
- Format on save should work automatically
- Linting errors should appear inline
- Type hints should show intellisense

### Quick Commands

| Command | Shortcut (Mac) | Shortcut (Win/Linux) |
|---------|----------------|----------------------|
| Format Document | `Shift+Option+F` | `Shift+Alt+F` |
| Run Tests | `Cmd+Shift+P` → "Test: Run All Tests" | `Ctrl+Shift+P` → "Test: Run All Tests" |
| Open Terminal | `` Ctrl+` `` | `` Ctrl+` `` |
| Command Palette | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| Run Task | `Cmd+Shift+P` → "Tasks: Run Task" | `Ctrl+Shift+P` → "Tasks: Run Task" |

## IntelliJ IDEA / PyCharm Setup

### 1. Install IntelliJ IDEA or PyCharm
- **IntelliJ IDEA**: [jetbrains.com/idea](https://www.jetbrains.com/idea/)
- **PyCharm**: [jetbrains.com/pycharm](https://www.jetbrains.com/pycharm/)

### 2. Open Project
```bash
cd xarf-python
idea .  # or: charm .
```

Or: File → Open → Select `xarf-python` directory

### 3. Configure Python Interpreter
1. Go to: **File → Project Structure → Project**
2. Click **Add SDK → Python SDK → Add Local Interpreter**
3. Select **Virtualenv Environment → Existing**
4. Browse to `.venv/bin/python`
5. Click **OK**

### 4. Install Plugins (Optional)
1. Go to: **File → Settings → Plugins** (Mac: **IntelliJ IDEA → Preferences → Plugins**)
2. Search and install:
   - **.ignore** - .gitignore support
   - **Requirements** - requirements.txt support
   - **Black** (optional) - Black formatter integration

### 5. Verify Configuration
- Code inspections should show warnings/errors
- Black code style is automatically applied
- Run configurations appear in top-right dropdown

### Quick Commands

| Action | Shortcut (Mac) | Shortcut (Win/Linux) |
|--------|----------------|----------------------|
| Reformat Code | `Cmd+Option+L` | `Ctrl+Alt+L` |
| Run Tests | `Ctrl+R` → "Tests" | `Shift+F10` → "Tests" |
| Run Pre-commit | `Ctrl+R` → "Pre-commit All" | `Shift+F10` → "Pre-commit All" |
| Search Everywhere | `Double Shift` | `Double Shift` |
| Terminal | `Option+F12` | `Alt+F12` |

## Pre-commit Hooks Setup

Both IDEs require pre-commit hooks to be installed:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Test installation
pre-commit run --all-files
```

## Comparison: VS Code vs IntelliJ IDEA

| Feature | VS Code | IntelliJ IDEA / PyCharm |
|---------|---------|-------------------------|
| **Speed** | ⚡ Very fast | 🐢 Slower startup |
| **Memory** | 💾 Light (~200MB) | 💾 Heavy (~1GB+) |
| **Python Support** | ✅ Via extensions | ✅ Built-in |
| **Type Checking** | ✅ Pylance (fast) | ✅ Built-in (comprehensive) |
| **Debugging** | ✅ Good | ✅ Excellent |
| **Refactoring** | ✅ Basic | ✅ Advanced |
| **Git Integration** | ✅ Good (GitLens) | ✅ Excellent |
| **Cost** | 🆓 Free | 💰 Paid (Community: Free) |
| **Best For** | Quick editing, light projects | Large projects, refactoring |

## Troubleshooting

### VS Code: "Python not found"
**Solution**: Install Python extension and select interpreter (`.venv/bin/python`)

### VS Code: Format on save not working
**Solution**: Check `.vscode/settings.json` has `"editor.formatOnSave": true`

### IntelliJ: Code style conflicts with Black
**Solution**: Project code style is already configured in `.idea/codeStyles/Project.xml`

### Both: Pre-commit hooks not running
**Solution**: Run `pre-commit install` in project root

### Both: Slow performance
**VS Code**: Disable unused extensions
**IntelliJ**: Increase heap size in Help → Edit Custom VM Options

## Next Steps

1. ✅ Set up IDE (VS Code or IntelliJ IDEA)
2. ✅ Install pre-commit hooks
3. ✅ Run tests to verify setup
4. 📖 Read [DEVELOPMENT.md](DEVELOPMENT.md) for full development guide
5. 🚀 Start coding!

---

**Need Help?** Check [DEVELOPMENT.md](DEVELOPMENT.md) or open an issue on [GitHub](https://github.com/xarf/xarf-python/issues)
