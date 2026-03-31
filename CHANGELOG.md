# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-31

This release is a complete rework of the alpha (`v4.0.0a1`). No backward compatibility with the alpha API is provided. The version numbers will now be independent from the spec to provide release independence for the library.

### Breaking Changes

- **New public API**: `parse()`, `create_report()`, `create_evidence()` are now module-level functions. The `XARFParser` and `XARFGenerator` classes have been removed.
- **Structured result objects**: `parse()` and `create_report()` now return `ParseResult` and `CreateReportResult` dataclasses respectively, rather than bare model instances or dicts.
- **Structured errors**: `ValidationError` and `ValidationWarning` are dataclasses with `field`, `message`, and (for errors) `value` attributes — previously errors were plain strings.
- **Package name**: published as `xarf` (was `xarf-parser`).
- **Python version**: minimum is now 3.10 (was 3.8).

### Added

- **All 7 categories fully implemented**: messaging, connection, content, infrastructure, copyright, vulnerability, reputation — with Pydantic v2 discriminated union models covering all 32 report types.
- **Schema-driven validation**: validation rules are derived from the official xarf-spec JSON schemas via `jsonschema` + `referencing` (Draft 2020-12); no hardcoded type or field lists.
- **`SchemaRegistry`**: programmatic access to schema-derived categories, types, and field metadata. Exposed as the `schema_registry` module-level singleton.
- **`SchemaValidator`**: AJV-equivalent JSON Schema validator with strict mode (promotes `x-recommended` fields to required before validation).
- **`create_evidence()`**: helper that computes hash, base64-encodes payload, and records size — supports `sha256`, `sha512`, `sha1`, `md5`.
- **`show_missing_optional`** parameter on `parse()` and `create_report()`: populates `result.info` with missing recommended and optional field details.
- **v3 backward compatibility** fully integrated into `parse()`: automatic detection and conversion with `XARFv3DeprecationWarning`.
- **`python -m xarf fetch-schemas`**: CLI command to pull fresh schemas from the xarf-spec GitHub release.
- **`python -m xarf check-schema-updates`**: CLI command to report whether a newer spec version is available.
- **`py.typed` marker** (PEP 561): downstream `mypy` picks up types when the package is installed.
- **Bundled schemas**: schemas ship inside the wheel, pinned to spec v4.2.0, loaded via `importlib.resources`.

### Changed

- **Tooling**: switched to `ruff` (replaces `black`, `isort`, `flake8`); `mypy --strict`; `bandit`; `pytest` with 80% coverage threshold.
- **`v3_compat.py`**: aligned type mappings exactly with the JS reference implementation (8 types, PascalCase + lowercase variants for each).
- **`models.py`**: replaced with result dataclasses (`ParseResult`, `CreateReportResult`, `ValidationError`, `ValidationWarning`) and base Pydantic models (`XARFReport`, `XARFEvidence`, `ContactInfo`).

[Unreleased]: https://github.com/xarf/xarf-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/xarf/xarf-python/releases/tag/v0.1.0
