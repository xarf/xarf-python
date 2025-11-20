# XARF Python Library - Documentation Index

## Overview

This directory contains the complete architectural design and documentation for the XARF Python library.

## Architecture Documents

### Core Architecture

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** (20KB)
   - Complete architectural design specification
   - Module structure and organization
   - Core components (Parser, Validator, Generator)
   - Quality standards and testing strategy
   - Dependencies and security considerations
   - Performance requirements and benchmarks
   - **Use for**: Complete architectural reference

2. **[ARCHITECTURE_SUMMARY.md](ARCHITECTURE_SUMMARY.md)** (10KB)
   - Quick reference guide for implementation
   - Key design decisions
   - Module structure overview
   - Usage examples
   - Implementation priority
   - **Use for**: Quick lookup during development

3. **[CLASS_HIERARCHY.md](CLASS_HIERARCHY.md)** (17KB)
   - Complete class hierarchy diagrams
   - Inheritance relationships
   - Class responsibilities
   - Design patterns used
   - Extension points
   - **Use for**: Understanding object model

4. **[API_SURFACE.md](API_SURFACE.md)** (18KB)
   - Public API specification
   - All exported classes and functions
   - Method signatures and parameters
   - Usage examples for each API
   - Stability guarantees
   - **Use for**: API reference and integration

## Implementation Guides

5. **[QUICK_START.md](QUICK_START.md)** (5KB)
   - Getting started guide
   - Installation instructions
   - Basic usage examples
   - Common patterns
   - **Use for**: New developers onboarding

6. **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** (14KB)
   - Migration from xarf-parser to xarf
   - Breaking changes
   - Upgrade path
   - Code examples
   - **Use for**: Upgrading existing code

7. **[generator_usage.md](generator_usage.md)** (11KB)
   - Report generation guide
   - Factory methods
   - Builder pattern
   - Examples for all report types
   - **Use for**: Creating XARF reports programmatically

## Development Guides

8. **[ci-cd-pipeline-design.md](ci-cd-pipeline-design.md)** (16KB)
   - CI/CD pipeline architecture
   - GitHub Actions workflows
   - Testing strategy
   - Quality gates
   - Release process
   - **Use for**: Setting up CI/CD

9. **[PRE_COMMIT.md](PRE_COMMIT.md)** (5KB)
   - Pre-commit hooks setup
   - Code quality tools
   - Configuration
   - **Use for**: Development environment setup

## Document Organization

### By Role

**For Architects**:
- ARCHITECTURE.md - Complete design
- CLASS_HIERARCHY.md - Object model
- API_SURFACE.md - Public contracts

**For Developers**:
- ARCHITECTURE_SUMMARY.md - Quick reference
- QUICK_START.md - Getting started
- generator_usage.md - Usage examples

**For DevOps**:
- ci-cd-pipeline-design.md - Pipeline setup
- PRE_COMMIT.md - Development tools

**For Users**:
- QUICK_START.md - Basic usage
- MIGRATION_GUIDE.md - Upgrading

### By Phase

**Phase 1: Planning**
1. Read ARCHITECTURE.md for complete design
2. Review CLASS_HIERARCHY.md for object model
3. Check ARCHITECTURE_SUMMARY.md for priorities

**Phase 2: Implementation**
1. Use ARCHITECTURE_SUMMARY.md as quick reference
2. Reference API_SURFACE.md for API design
3. Follow CLASS_HIERARCHY.md for class design

**Phase 3: Testing**
1. Follow ci-cd-pipeline-design.md for test setup
2. Reference ARCHITECTURE.md for quality standards
3. Use PRE_COMMIT.md for local testing

**Phase 4: Release**
1. Follow ci-cd-pipeline-design.md for release process
2. Update MIGRATION_GUIDE.md if breaking changes
3. Update QUICK_START.md with new features

## Key Decisions

### 1. Package Rename: xarf-parser → xarf
- **Document**: ARCHITECTURE.md (Section 1.1)
- **Rationale**: Cleaner imports, broader scope
- **Impact**: Migration guide needed

### 2. Field Name: category (not class)
- **Document**: ARCHITECTURE.md (Section 3)
- **Rationale**: Python keyword conflict, readability
- **Implementation**: Pydantic alias for JSON compatibility

### 3. No v3 Converter
- **Document**: ARCHITECTURE.md (ADR-003)
- **Rationale**: Deprecated format, simpler codebase
- **Impact**: Users migrate externally

### 4. Separate Validator Component
- **Document**: ARCHITECTURE.md (Section 2.2)
- **Rationale**: Separation of concerns, reusability
- **Impact**: New module to implement

### 5. Minimal Dependencies
- **Document**: ARCHITECTURE.md (Section 5)
- **Choices**: Pydantic v2, python-dateutil, email-validator
- **Rationale**: Performance, security, maintainability

## Implementation Status

### Completed
- [x] Architecture design
- [x] Module structure definition
- [x] Class hierarchy design
- [x] API surface specification
- [x] Documentation written

### In Progress
- [ ] Core models with 'category' field
- [ ] Enhanced parser implementation
- [ ] Validator component extraction
- [ ] Generator component creation
- [ ] Comprehensive test suite

### Planned
- [ ] Performance optimization
- [ ] Documentation site (MkDocs)
- [ ] CLI tool
- [ ] Integration examples

## Quality Metrics

### Coverage Targets
- Overall: ≥95%
- Core modules (parser, validator, generator): 100%
- Models: 95%
- Utils: 100%

### Type Safety
- Type hints: 100% on public API
- Type checker: mypy strict mode
- PEP 561 compliance: py.typed marker

### Performance
- Parse speed: 1000+ reports/sec
- Memory: <10KB per report
- Concurrency: Thread-safe, linear scaling

### Code Quality
- Cyclomatic complexity: ≤10 per function
- Line length: 88 characters (Black)
- Linting: Ruff (10-100x faster than flake8)

## Dependencies

### Core (3 packages)
```toml
pydantic>=2.5.0,<3.0.0      # Data validation
python-dateutil>=2.8.0       # Datetime parsing
email-validator>=2.1.0       # Email validation
```

### Development (7 packages)
```toml
pytest>=7.4.0               # Testing
pytest-cov>=4.1.0          # Coverage
hypothesis>=6.88.0         # Property testing
ruff>=0.1.0                # Linting
black>=23.11.0             # Formatting
mypy>=1.7.0                # Type checking
pre-commit>=3.5.0          # Git hooks
```

## Usage Examples

### Parse Report
```python
from xarf import XARFParser

parser = XARFParser()
report = parser.parse('{"xarf_version": "4.0.0", ...}')
print(f"Category: {report.category}")
```

### Validate Report
```python
from xarf import XARFValidator

validator = XARFValidator()
result = validator.validate(report)
if not result.is_valid:
    for error in result.errors:
        print(error)
```

### Generate Report
```python
from xarf import XARFGenerator

report = XARFGenerator.create_messaging_report(
    source_ip="192.0.2.100",
    report_type="spam",
    reporter={"org": "My Org", "contact": "me@example.com", "type": "automated"},
    evidence_source="spamtrap"
)
```

## Extension Points

### Custom Validators
- **Document**: CLASS_HIERARCHY.md (Section: Extension Points)
- **How**: Subclass XARFValidator
- **Use Case**: Organization-specific rules

### Custom Report Types
- **Document**: CLASS_HIERARCHY.md (Section: Extension Points)
- **How**: Subclass XARFReport
- **Use Case**: Internal report fields

### Plugin System (Future)
- **Document**: ARCHITECTURE.md (Section 7.3)
- **Status**: Planned for future release
- **Use Case**: SIEM integration, custom handlers

## Related Resources

### External Documentation
- [XARF Specification](https://github.com/xarf/xarf-spec) - Official XARF v4 spec
- [XARF Website](https://xarf.org) - Project website
- [Python Type Hints](https://docs.python.org/3/library/typing.html) - Type system reference
- [Pydantic Documentation](https://docs.pydantic.dev/) - Data validation library

### Repository
- [GitHub Repository](https://github.com/xarf/xarf-parser-python)
- [Issue Tracker](https://github.com/xarf/xarf-parser-python/issues)
- [Pull Requests](https://github.com/xarf/xarf-parser-python/pulls)

### Tools
- [Black](https://black.readthedocs.io/) - Code formatter
- [Ruff](https://docs.astral.sh/ruff/) - Fast linter
- [mypy](https://mypy.readthedocs.io/) - Type checker
- [pytest](https://docs.pytest.org/) - Testing framework
- [MkDocs](https://www.mkdocs.org/) - Documentation generator

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

### Documentation Contributions

When updating architecture documentation:

1. **Major Changes**: Update ARCHITECTURE.md and regenerate summary
2. **API Changes**: Update API_SURFACE.md
3. **Class Changes**: Update CLASS_HIERARCHY.md
4. **Examples**: Update QUICK_START.md and generator_usage.md
5. **All Changes**: Update this INDEX.md with new sections

### Documentation Style

- Use clear, concise language
- Include code examples for all features
- Add diagrams where helpful
- Link between related documents
- Keep examples up-to-date with code

## Maintenance

### Review Schedule
- **Quarterly**: Review all architecture documents
- **Per Release**: Update API_SURFACE.md, MIGRATION_GUIDE.md
- **As Needed**: Update examples and quick starts

### Document Ownership
- ARCHITECTURE.md: Architecture team
- API_SURFACE.md: API team
- Implementation guides: Development team
- CI/CD guides: DevOps team

## Version History

- **2025-11-20**: Initial architecture design complete
  - Created core architecture documents
  - Defined module structure
  - Specified API surface
  - Designed class hierarchy

## Contact

For questions about the architecture:
- Open an issue: https://github.com/xarf/xarf-parser-python/issues
- Email: contact@xarf.org

---

**Last Updated**: 2025-11-20
**Architecture Version**: 1.0
**Target Release**: 4.0.0
