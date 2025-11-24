# Changelog

All notable changes to the XARF Python Parser will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Legacy Tag Naming**: Updated v3 compatibility tags from `legacy:class:` to `legacy:category:` to align with v4 field naming conventions
  - Affects only v3 report conversion metadata tags
  - Maintains consistency with `category` field terminology throughout codebase

### Fixed
- **Documentation Examples**: Corrected CONTRIBUTING.md sample report to use `category` field instead of outdated `class` reference

### Added
- **XARF v3 Backwards Compatibility**: Automatic conversion from v3 to v4 format
  - `is_v3_report()` function to detect v3 reports
  - `convert_v3_to_v4()` function for explicit conversion
  - Automatic detection and conversion in `XARFParser.parse()`
  - Deprecation warnings for v3 format usage (`XARFv3DeprecationWarning`)
  - 14 comprehensive tests for v3 compatibility covering all categories
  - Complete field mapping from v3 to v4 structure (ReportClass→category, etc.)
  - Legacy metadata tracking (`legacy_version`, `_internal.converted_from_v3`)
  - Migration guide documentation at `docs/migration-guide.md`

### Changed
- **Pydantic V2 Migration**: Updated from Pydantic V1 to V2 API
  - Replaced `@validator` with `@field_validator` for all model validators
  - Updated `Config` class to `ConfigDict` in XARFReport model
  - Changed `allow_population_by_field_name` to `populate_by_name`
  - All validators now use `@classmethod` decorator with type hints
  - Fixed Python 3.13+ datetime deprecation warnings

### Fixed
- Resolved all Pydantic V2 deprecation warnings in models
- Fixed `datetime.utcnow()` deprecation by using `datetime.now(timezone.utc)`
- Improved type hints for Pydantic V2 compatibility
- Updated import statements to use `pydantic.ConfigDict` and `field_validator`

### Documentation
- Added v3 compatibility section to README with example code
- Created comprehensive migration guide (`docs/migration-guide.md`)
- Updated feature list to highlight v3 support and Pydantic V2 compatibility
- Added documentation links for migration guide

## [4.0.0] - 2024-01-20

### Breaking Changes

#### Field Rename: `class` → `category`

The field previously named `class` has been renamed to `category` to align with the official XARF v4 specification. This change was made to avoid conflicts with programming language reserved keywords and better reflect the field's purpose.

**Impact:**
- All JSON reports must now use `"category"` instead of `"class"`
- Python code must access `report.category` instead of `report.class_`
- Validation checks for `"category"` field presence

**Migration:**
- Update all JSON generation code to use `"category"`
- Replace all `report.class_` with `report.category` in Python code
- See [MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) for detailed migration instructions

```python
# Before (v3.x)
report = {
    "class": "content",  # Old field name
    "type": "phishing"
}
print(report.class_)  # Awkward Python workaround

# After (v4.0.0+)
report = {
    "category": "content",  # New field name
    "type": "phishing"
}
print(report.category)  # Clean Python access
```

### Added

- **Generator Functionality**: New `XARFGenerator` class for programmatically creating XARF v4 reports
  - `create_report()` - Generate complete reports with validation
  - `create_messaging_report()` - Generate messaging category reports (spam, phishing)
  - `create_connection_report()` - Generate connection category reports (DDoS, port scans)
  - `create_content_report()` - Generate content category reports (phishing sites, malware)
  - Automatic UUID generation for `report_id`
  - Timestamp generation in ISO 8601 format
  - Built-in validation during generation

- **Reporter `on_behalf_of` Field**: Support for infrastructure providers sending reports on behalf of other organizations
  - `reporter.on_behalf_of.org` - Organization being represented
  - `reporter.on_behalf_of.contact` - Contact email for represented organization
  - Useful for MSSPs, abuse reporting services, and infrastructure providers

- **Enhanced Validation**: Improved validation for all XARF v4 requirements
  - Category-specific field validation
  - Evidence structure validation
  - Reporter information validation
  - Timestamp format validation

- **Python 3.12 Support**: Added support for Python 3.12

### Changed

- **Model Classes**: Updated all model classes to use `category` instead of `class_`
  - `XARFReport.category` replaces `XARFReport.class_`
  - `MessagingReport.category` replaces `MessagingReport.class_`
  - `ConnectionReport.category` replaces `ConnectionReport.class_`
  - `ContentReport.category` replaces `ContentReport.class_`

- **Parser Validation**: Updated validation logic to check for `"category"` field
  - Old reports with `"class"` will fail validation
  - Use migration helper to convert legacy reports

- **Field Access**: Removed `class_` aliasing workaround in favor of clean `category` field
  - Pydantic models now use `category` directly
  - No more Python keyword conflicts

### Removed

- **Converter Module**: Temporarily removed `xarf.converter` module for XARF version conversion
  - Will be redesigned and re-added in a future release
  - Users needing conversion should implement temporary solution (see migration guide)

- **Python 3.7 Support**: Dropped support for Python 3.7 (EOL June 2023)
  - Minimum Python version is now 3.8

### Fixed

- Improved error messages for validation failures
- Better handling of optional fields
- Fixed timezone handling for timestamps

### Documentation

- Added comprehensive [MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) with:
  - Step-by-step migration instructions
  - Before/after code examples
  - Common migration issues and solutions
  - Database migration examples
  - Backward compatibility patterns

- Updated [README.md](README.md) with:
  - Generator usage examples
  - Updated JSON examples using `"category"`
  - `on_behalf_of` examples
  - Security best practices
  - Links to xarf.org website
  - Updated feature matrix

### Security

- Enhanced input validation for all fields
- Added size limits for evidence payloads (5MB per item, 15MB total)
- Improved email validation for reporter contact fields
- Better handling of untrusted input in strict mode

---

## [3.0.0] - 2023-11-15

### Added
- Initial XARF v3 support
- Basic JSON parsing and validation
- Support for common abuse types
- Python 3.8+ compatibility

### Changed
- Migrated from XARF v2 to v3 format

---

## [2.1.0] - 2023-06-10

### Added
- Evidence attachment support
- Custom field handling

### Fixed
- Timestamp parsing issues
- Validation edge cases

---

## [2.0.0] - 2023-03-20

### Added
- Complete rewrite for XARF v2
- Pydantic-based models
- JSON Schema validation
- Comprehensive test suite

---

## [1.0.0] - 2022-09-15

### Added
- Initial release
- Basic XARF v1 parsing
- Limited validation

---

## Migration Guides

- **v3.x → v4.0.0**: See [MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)
- **v2.x → v3.x**: Contact support for legacy migration assistance

## Links

- [XARF v4 Specification](https://xarf.org/docs/specification/)
- [GitHub Repository](https://github.com/xarf/xarf-parser-python)
- [PyPI Package](https://pypi.org/project/xarf-parser/)
- [Issue Tracker](https://github.com/xarf/xarf-parser-python/issues)
- [XARF Website](https://xarf.org)

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

Alpha releases use suffix: `4.0.0a1`, `4.0.0a2`, etc.
Beta releases use suffix: `4.0.0b1`, `4.0.0b2`, etc.
