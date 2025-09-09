# Contributing to XARF Python Parser

Thank you for your interest in contributing to the XARF v4 Python parser! This document provides guidelines for contributing to the implementation.

## 🤝 How to Contribute

### Reporting Issues
- **Bug Reports**: Parser errors, validation issues, or unexpected behavior
- **Feature Requests**: New validation rules, performance improvements, or API enhancements
- **Parser Support**: Help with implementing new XARF classes or types

### Contributing Code
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/validation-improvement`)
3. **Make** your changes following our coding standards
4. **Add tests** for new functionality
5. **Run** the test suite and linting
6. **Submit** a pull request

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Git

### Installation
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/xarf-parser-python.git
cd xarf-parser-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests
```bash
# Run full test suite
pytest

# Run with coverage
pytest --cov=xarf

# Run specific test file
pytest tests/test_parser.py

# Run with verbose output
pytest -v
```

### Code Quality
```bash
# Format code
black xarf/
isort xarf/

# Lint code
flake8 xarf/

# Type checking
mypy xarf/
```

## 📋 Contribution Guidelines

### Code Standards
- **Follow PEP 8** style guidelines
- **Use type hints** for all functions and methods
- **Write docstrings** for public APIs
- **Keep functions focused** and single-purpose
- **Use descriptive variable names**

### Testing Requirements
- **Unit tests** for all new functionality
- **Integration tests** for end-to-end scenarios
- **Test edge cases** and error conditions
- **Maintain >90% test coverage**
- **Mock external dependencies**

### API Design
- **Consistent naming** with existing patterns
- **Clear error messages** with actionable information
- **Backward compatibility** when possible
- **Performance considerations** for high-volume use

## 🏗️ Architecture Overview

### Core Components
```
xarf/
├── __init__.py          # Public API exports
├── parser.py            # Main XARFParser class
├── models.py            # Pydantic data models
├── exceptions.py        # Custom exception classes
└── validators.py        # Validation logic (future)
```

### Design Principles
- **Pydantic models** for data validation and serialization
- **Modular design** for easy extension
- **Clear separation** between parsing and validation
- **Comprehensive error handling** with context

## 🎯 Priority Areas

### High Priority (Alpha → Beta)
- **Complete class coverage** (infrastructure, copyright, vulnerability, reputation)
- **Enhanced validation** beyond basic schema checking
- **Performance optimization** for high-volume processing
- **XARF v3 compatibility** layer

### Medium Priority (Beta → Stable)
- **Advanced validation rules** (business logic, cross-field validation)
- **CLI tools** for command-line usage
- **Integration examples** with popular security tools
- **Comprehensive benchmarking**

### Future Enhancements
- **Evidence handling** (compression, validation)
- **Bulk processing** utilities
- **Plugin architecture** for custom validators
- **Async parsing** support

## 📝 Code Style Examples

### Function Documentation
```python
def parse_report(self, json_data: Union[str, Dict[str, Any]]) -> XARFReport:
    """Parse XARF report from JSON data.
    
    Args:
        json_data: JSON string or dictionary containing XARF report data
        
    Returns:
        XARFReport: Parsed and validated report object
        
    Raises:
        XARFParseError: If JSON parsing fails
        XARFValidationError: If validation fails in strict mode
        
    Example:
        >>> parser = XARFParser()
        >>> report = parser.parse('{"xarf_version": "4.0.0", ...}')
        >>> print(report.class_)
        'messaging'
    """
```

### Error Handling
```python
try:
    report = parser.parse(json_data)
except XARFValidationError as e:
    logger.error(f"Validation failed: {e}")
    for error in e.errors:
        logger.debug(f"  - {error}")
    raise
except XARFParseError as e:
    logger.error(f"Parse failed: {e}")
    raise
```

### Test Structure
```python
class TestMessagingReports:
    """Test parsing of messaging class reports."""
    
    def test_valid_spam_report(self):
        """Test parsing of valid spam report."""
        report_data = {
            "xarf_version": "4.0.0",
            # ... complete valid data
        }
        
        parser = XARFParser()
        report = parser.parse(report_data)
        
        assert isinstance(report, MessagingReport)
        assert report.class_ == "messaging"
        assert report.type == "spam"
    
    def test_missing_required_field(self):
        """Test handling of missing required fields."""
        invalid_data = {"xarf_version": "4.0.0"}  # Missing required fields
        
        parser = XARFParser(strict=True)
        
        with pytest.raises(XARFValidationError) as exc_info:
            parser.parse(invalid_data)
        
        assert "Missing required fields" in str(exc_info.value)
```

## 🔍 Testing Guidelines

### Test Categories
- **Unit Tests**: Individual functions and methods
- **Integration Tests**: Full parsing workflows
- **Validation Tests**: Schema and business rule validation
- **Performance Tests**: Benchmarking and profiling

### Sample Test Data
```python
# Use realistic but anonymized data
SAMPLE_SPAM_REPORT = {
    "xarf_version": "4.0.0",
    "report_id": "00000000-0000-0000-0000-000000000001",
    "timestamp": "2024-01-01T12:00:00Z",
    "reporter": {
        "org": "Test Security Provider",
        "contact": "test@example.com",
        "type": "automated"
    },
    "source_identifier": "192.0.2.1",  # RFC 3330 test IP
    "class": "messaging",
    "type": "spam",
    "evidence_source": "spamtrap"
}
```

## 💬 Community Guidelines

### Pull Request Process
1. **Clear description** of changes and motivation
2. **Reference issues** when applicable
3. **Include tests** for new functionality
4. **Update documentation** if needed
5. **Respond to feedback** promptly

### Review Criteria
- **Code quality** and style consistency
- **Test coverage** and quality
- **Performance impact** consideration
- **API compatibility** maintenance
- **Documentation** completeness

## 📞 Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and design discussions
- **Code Review**: Request feedback on draft PRs
- **Email**: contact@xarf.org for sensitive issues

## 🏆 Recognition

Contributors are recognized through:
- Git commit history and contributor graphs
- Release notes and changelogs
- PyPI package metadata
- Conference presentations (with permission)

## 🚀 Release Process

### Alpha Releases (4.0.0a1, 4.0.0a2, ...)
- **Frequent releases** with new features
- **Breaking changes** allowed
- **Community feedback** encouraged
- **PyPI pre-release** tags

### Beta Releases (4.0.0b1, ...)
- **Feature complete** for initial scope
- **API stabilization** focus
- **No breaking changes** without major justification
- **Performance optimization**

### Stable Releases (4.0.0, 4.0.1, ...)
- **Production ready** quality
- **Semantic versioning** strictly followed
- **Long-term support** commitment
- **Comprehensive documentation**

Thank you for helping make XARF parsing reliable and efficient! 🐍