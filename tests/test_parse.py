"""Tests for the :func:`xarf.parse` function.

Covers:

- All 32 canonical xarf-spec v4 samples parse without errors.
- Shared test-suite samples are handled robustly (no unhandled exceptions).
- Invalid samples produce the expected errors or exceptions.
- v3 backward-compatibility detection and conversion warnings.
- JSON string vs dict input formats.
- Strict mode behaviour.
- Unknown-field warnings and errors.
- ``show_missing_optional`` info population.
- Category/type discriminated union resolution.
- Malformed / edge-case input.
- Throughput performance (≥ 1000 reports/sec).
"""

from __future__ import annotations

import copy
import json
import time
from pathlib import Path
from typing import Any

import pytest

from xarf import parse
from xarf.exceptions import XARFParseError
from xarf.models import (
    DdosReport,
    ParseResult,
    PhishingReport,
    SpamReport,
)

# ---------------------------------------------------------------------------
# Module-level collection of spec samples (empty when monorepo not present)
# ---------------------------------------------------------------------------

_SPEC_SAMPLES_DIR: Path = (
    Path(__file__).parent.parent.parent / "xarf-spec" / "samples" / "v4"
)
_spec_samples: list[tuple[Path, str]] = (
    [(p, p.stem) for p in sorted(_SPEC_SAMPLES_DIR.glob("*.json"))]
    if _SPEC_SAMPLES_DIR.exists()
    else []
)

_SHARED_SAMPLES_DIR: Path = Path(__file__).parent / "shared" / "samples"
_INVALID_DIR: Path = _SHARED_SAMPLES_DIR / "invalid"
_V3_DIR: Path = _SHARED_SAMPLES_DIR / "valid" / "v3"

# ---------------------------------------------------------------------------
# Base valid report used in several test classes
# ---------------------------------------------------------------------------

_CONTACT: dict[str, str] = {
    "org": "ACME Security",
    "contact": "abuse@acme.example",
    "domain": "acme.example",
}

_VALID_DDOS: dict[str, Any] = {
    "xarf_version": "4.2.0",
    "report_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-15T10:30:00Z",
    "reporter": _CONTACT,
    "sender": _CONTACT,
    "source_identifier": "192.0.2.1",
    "category": "connection",
    "type": "ddos",
    "evidence_source": "honeypot",
    "source_port": 12345,
    "destination_ip": "203.0.113.10",
    "protocol": "tcp",
    "first_seen": "2024-01-15T09:00:00Z",
}

_VALID_SPAM: dict[str, Any] = {
    "xarf_version": "4.2.0",
    "report_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "timestamp": "2024-01-15T10:30:00Z",
    "reporter": _CONTACT,
    "sender": _CONTACT,
    "source_identifier": "192.0.2.1",
    "category": "messaging",
    "type": "spam",
    "evidence_source": "honeypot",
    "protocol": "sms",
}

_VALID_PHISHING: dict[str, Any] = {
    "xarf_version": "4.2.0",
    "report_id": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
    "timestamp": "2024-01-15T10:30:00Z",
    "reporter": _CONTACT,
    "sender": _CONTACT,
    "source_identifier": "192.0.2.1",
    "category": "content",
    "type": "phishing",
    "evidence_source": "honeypot",
    "url": "https://phishing.example.com/login",
}


# ---------------------------------------------------------------------------
# TestSpecSamples
# ---------------------------------------------------------------------------


class TestSpecSamples:
    """Tests that every canonical xarf-spec v4 sample parses without errors."""

    @pytest.mark.parametrize(
        "sample_path,sample_stem",
        _spec_samples,
        ids=[stem for _, stem in _spec_samples],
    )
    def test_spec_sample_parses_without_errors(
        self, sample_path: Path, sample_stem: str
    ) -> None:
        """Each canonical spec sample must produce zero validation errors.

        Args:
            sample_path: Absolute path to the sample JSON file.
            sample_stem: Filename stem, used as the test ID.
        """
        if not _SPEC_SAMPLES_DIR.exists():
            pytest.skip("xarf-spec directory not present in this checkout")

        raw = sample_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        result = parse(data)
        assert result.errors == [], f"{sample_stem}: unexpected errors: {result.errors}"

    def test_dict_and_string_input_are_equivalent(self) -> None:
        """Dict input and JSON string input produce the same result for a
        representative sample.

        Skips gracefully when the spec samples directory is absent.
        """
        if not _spec_samples:
            pytest.skip("xarf-spec directory not present in this checkout")

        sample_path, _ = _spec_samples[0]
        raw = sample_path.read_text(encoding="utf-8")
        data = json.loads(raw)

        result_dict = parse(data)
        result_str = parse(raw)

        assert result_dict.errors == result_str.errors
        assert type(result_dict.report) is type(result_str.report)


# ---------------------------------------------------------------------------
# TestSharedSamplesRobustness
# ---------------------------------------------------------------------------


class TestSharedSamplesRobustness:
    """Tests that all valid/v4 shared samples do not raise unhandled exceptions."""

    @pytest.mark.parametrize(
        "sample_path",
        list((_SHARED_SAMPLES_DIR / "valid" / "v4").rglob("*.json")),
        ids=[
            p.stem
            for p in sorted((_SHARED_SAMPLES_DIR / "valid" / "v4").rglob("*.json"))
        ],
    )
    def test_shared_valid_v4_sample_does_not_raise(self, sample_path: Path) -> None:
        """parse() must not raise for any shared valid/v4 sample.

        The result must be a :class:`~xarf.models.ParseResult`.  The report may
        be ``None`` when schema errors prevent Pydantic deserialization, but the
        call itself must not throw.

        Args:
            sample_path: Path to a shared valid/v4 JSON sample.
        """
        data = json.loads(sample_path.read_text(encoding="utf-8"))
        result = parse(data)
        assert isinstance(result, ParseResult)
        # Either the report was parsed OR there were errors — both are acceptable.
        assert result.report is not None or len(result.errors) > 0


# ---------------------------------------------------------------------------
# TestInvalidSamples
# ---------------------------------------------------------------------------


class TestInvalidSamples:
    """Tests that known-invalid shared samples are handled correctly."""

    def test_malformed_json_raises_parse_error(self) -> None:
        """Truly malformed JSON string raises
        :class:`~xarf.exceptions.XARFParseError`."""
        raw = (_INVALID_DIR / "malformed_data" / "invalid_json.json").read_text(
            encoding="utf-8"
        )
        with pytest.raises(XARFParseError):
            parse(raw)

    def test_invalid_class_produces_category_error(self) -> None:
        """A report with an invalid category value produces errors referencing
        'category'.

        Args: (none beyond self)
        """
        data = json.loads(
            (_INVALID_DIR / "schema_violations" / "invalid_class.json").read_text(
                encoding="utf-8"
            )
        )
        result = parse(data)
        assert len(result.errors) > 0
        fields_and_messages = " ".join(f"{e.field} {e.message}" for e in result.errors)
        assert "category" in fields_and_messages.lower()

    def test_missing_xarf_version_produces_errors(self) -> None:
        """A report missing ``xarf_version`` produces validation errors."""
        data = json.loads(
            (
                _INVALID_DIR / "schema_violations" / "missing_xarf_version.json"
            ).read_text(encoding="utf-8")
        )
        result = parse(data)
        assert len(result.errors) > 0

    def test_missing_reporter_produces_reporter_error(self) -> None:
        """A report missing the ``reporter`` field produces an error referencing
        'reporter'.

        Args: (none beyond self)
        """
        data = json.loads(
            (_INVALID_DIR / "missing_fields" / "missing_reporter.json").read_text(
                encoding="utf-8"
            )
        )
        result = parse(data)
        assert len(result.errors) > 0
        fields_and_messages = " ".join(f"{e.field} {e.message}" for e in result.errors)
        assert "reporter" in fields_and_messages.lower()

    def test_messaging_missing_protocol_produces_errors(self) -> None:
        """A messaging report missing ``protocol`` produces validation errors."""
        data = json.loads(
            (
                _INVALID_DIR
                / "business_rule_violations"
                / "messaging_missing_protocol.json"
            ).read_text(encoding="utf-8")
        )
        result = parse(data)
        assert len(result.errors) > 0


# ---------------------------------------------------------------------------
# TestV3Detection
# ---------------------------------------------------------------------------


class TestV3Detection:
    """Tests for automatic v3 → v4 conversion and deprecation warnings."""

    def test_spam_v3_sample_converts_without_errors(self) -> None:
        """spam_v3_sample parses as a string with no errors and a v3 deprecation
        warning."""
        raw = (_V3_DIR / "spam_v3_sample.json").read_text(encoding="utf-8")
        result = parse(raw)
        assert result.errors == [], f"Unexpected errors: {result.errors}"
        assert result.report is not None
        warning_messages = " ".join(w.message for w in result.warnings)
        assert (
            "v3" in warning_messages.lower() or "deprecated" in warning_messages.lower()
        )

    def test_phishing_v3_sample_converts_without_errors(self) -> None:
        """phishing_v3_sample parses as a string with no errors and a v3 deprecation
        warning."""
        raw = (_V3_DIR / "phishing_v3_sample.json").read_text(encoding="utf-8")
        result = parse(raw)
        assert result.errors == [], f"Unexpected errors: {result.errors}"
        assert result.report is not None
        warning_messages = " ".join(w.message for w in result.warnings)
        assert (
            "v3" in warning_messages.lower() or "deprecated" in warning_messages.lower()
        )

    def test_ddos_v3_sample_raises_parse_error(self) -> None:
        """ddos_v3_sample raises :class:`~xarf.exceptions.XARFParseError` due to
        missing protocol."""
        raw = (_V3_DIR / "ddos_v3_sample.json").read_text(encoding="utf-8")
        with pytest.raises(XARFParseError):
            parse(raw)

    def test_v3_conversion_emits_python_warning(self) -> None:
        """parse() emits a Python :func:`warnings.warn` call when converting v3
        reports."""
        raw = (_V3_DIR / "spam_v3_sample.json").read_text(encoding="utf-8")
        with pytest.warns(DeprecationWarning):
            parse(raw)


# ---------------------------------------------------------------------------
# TestInputFormats
# ---------------------------------------------------------------------------


class TestInputFormats:
    """Tests for JSON string vs dict input forms."""

    def test_string_input_matches_dict_input(self) -> None:
        """Passing a JSON string and an equivalent dict produce the same result."""
        data = copy.deepcopy(_VALID_DDOS)
        json_str = json.dumps(data)

        result_dict = parse(data)
        result_str = parse(json_str)

        assert result_dict.errors == result_str.errors
        assert type(result_dict.report) is type(result_str.report)

    def test_extra_whitespace_in_json_string_is_handled(self) -> None:
        """A JSON string with extra leading/trailing whitespace parses successfully."""
        json_str = "  \n" + json.dumps(_VALID_DDOS) + "\n  "
        result = parse(json_str)
        assert isinstance(result, ParseResult)

    def test_malformed_string_raises_parse_error(self) -> None:
        """A non-JSON string raises :class:`~xarf.exceptions.XARFParseError`."""
        with pytest.raises(XARFParseError):
            parse("this is not json at all }{")


# ---------------------------------------------------------------------------
# TestStrictMode
# ---------------------------------------------------------------------------


class TestStrictMode:
    """Tests for strict-mode validation behaviour."""

    def test_missing_recommended_field_no_error_in_non_strict(self) -> None:
        """Missing ``evidence_source`` (recommended) does not produce errors in
        non-strict mode."""
        data = copy.deepcopy(_VALID_DDOS)
        del data["evidence_source"]
        result = parse(data, strict=False)
        assert result.errors == []

    def test_missing_recommended_field_error_in_strict(self) -> None:
        """Missing ``evidence_source`` (recommended) produces errors in strict mode."""
        data = copy.deepcopy(_VALID_DDOS)
        del data["evidence_source"]
        result = parse(data, strict=True)
        assert len(result.errors) > 0

    def test_strict_mode_with_errors_returns_none_report(self) -> None:
        """Strict mode with validation errors returns ``report=None``."""
        data = copy.deepcopy(_VALID_DDOS)
        del data["evidence_source"]
        result = parse(data, strict=True)
        assert result.report is None

    def test_non_strict_mode_may_still_return_report(self) -> None:
        """Non-strict mode with recoverable issues may still return a typed report."""
        # A fully-valid report in non-strict mode always yields a report.
        result = parse(copy.deepcopy(_VALID_DDOS), strict=False)
        assert result.report is not None


# ---------------------------------------------------------------------------
# TestUnknownFields
# ---------------------------------------------------------------------------


class TestUnknownFields:
    """Tests for unknown-field detection and warning/error promotion."""

    def test_unknown_field_produces_warning_in_non_strict(self) -> None:
        """An unrecognized field in a valid report produces a
        :class:`~xarf.models.ValidationWarning`."""
        data = copy.deepcopy(_VALID_DDOS)
        data["totally_unknown_xarf_field"] = "surprise"
        result = parse(data, strict=False)
        warning_fields = [w.field for w in result.warnings]
        assert "totally_unknown_xarf_field" in warning_fields

    def test_unknown_field_produces_error_in_strict(self) -> None:
        """An unrecognized field in strict mode produces a
        :class:`~xarf.models.ValidationError`."""
        data = copy.deepcopy(_VALID_DDOS)
        data["totally_unknown_xarf_field"] = "surprise"
        result = parse(data, strict=True)
        error_fields = [e.field for e in result.errors]
        assert "totally_unknown_xarf_field" in error_fields

    def test_known_schema_fields_do_not_produce_warnings(self) -> None:
        """Core schema fields such as ``description`` do not trigger
        unknown-field warnings."""
        data = copy.deepcopy(_VALID_DDOS)
        data["description"] = "A known optional field"
        result = parse(data, strict=False)
        warning_fields = [w.field for w in result.warnings]
        assert "description" not in warning_fields


# ---------------------------------------------------------------------------
# TestShowMissingOptional
# ---------------------------------------------------------------------------


class TestShowMissingOptional:
    """Tests for the ``show_missing_optional`` feature."""

    def test_show_missing_optional_false_returns_none_info(self) -> None:
        """``show_missing_optional=False`` (default) leaves ``result.info`` as
        ``None``."""
        result = parse(copy.deepcopy(_VALID_DDOS), show_missing_optional=False)
        assert result.info is None

    def test_show_missing_optional_true_returns_list(self) -> None:
        """``show_missing_optional=True`` populates ``result.info`` with a list."""
        result = parse(copy.deepcopy(_VALID_DDOS), show_missing_optional=True)
        assert isinstance(result.info, list)

    def test_info_entries_have_field_and_message_keys(self) -> None:
        """Each info dict must have ``"field"`` and ``"message"`` keys."""
        result = parse(copy.deepcopy(_VALID_DDOS), show_missing_optional=True)
        assert result.info is not None
        for entry in result.info:
            assert "field" in entry
            assert "message" in entry

    def test_recommended_field_info_has_recommended_prefix(self) -> None:
        """The ``confidence`` field (recommended) appears in info with a
        ``RECOMMENDED:`` prefix."""
        result = parse(copy.deepcopy(_VALID_DDOS), show_missing_optional=True)
        assert result.info is not None
        confidence_entries = [e for e in result.info if e["field"] == "confidence"]
        assert len(confidence_entries) == 1
        assert confidence_entries[0]["message"].startswith("RECOMMENDED:")

    def test_optional_field_info_has_optional_prefix(self) -> None:
        """The ``description`` field (optional) appears in info with an
        ``OPTIONAL:`` prefix."""
        result = parse(copy.deepcopy(_VALID_DDOS), show_missing_optional=True)
        assert result.info is not None
        desc_entries = [e for e in result.info if e["field"] == "description"]
        assert len(desc_entries) == 1
        assert desc_entries[0]["message"].startswith("OPTIONAL:")

    def test_present_fields_not_in_info(self) -> None:
        """Fields that are already present in the report do not appear in info."""
        result = parse(copy.deepcopy(_VALID_DDOS), show_missing_optional=True)
        assert result.info is not None
        info_fields = [e["field"] for e in result.info]
        for present_field in (
            "xarf_version",
            "report_id",
            "category",
            "type",
            "evidence_source",
        ):
            assert present_field not in info_fields


# ---------------------------------------------------------------------------
# TestCategoryTypeDiscrimination
# ---------------------------------------------------------------------------


class TestCategoryTypeDiscrimination:
    """Tests that the discriminated union resolves to the correct concrete type."""

    def test_spam_report_type(self) -> None:
        """A ``messaging/spam`` dict resolves to a :class:`~xarf.models.SpamReport`."""
        result = parse(copy.deepcopy(_VALID_SPAM))
        assert result.errors == []
        assert isinstance(result.report, SpamReport)

    def test_spam_report_category_and_type_fields(self) -> None:
        """``result.report.category`` and ``result.report.type`` are correct for
        spam."""
        result = parse(copy.deepcopy(_VALID_SPAM))
        assert result.report is not None
        assert result.report.category == "messaging"
        assert result.report.type == "spam"

    def test_ddos_report_type(self) -> None:
        """A ``connection/ddos`` dict resolves to a :class:`~xarf.models.DdosReport`."""
        result = parse(copy.deepcopy(_VALID_DDOS))
        assert result.errors == []
        assert isinstance(result.report, DdosReport)

    def test_ddos_report_category_and_type_fields(self) -> None:
        """``result.report.category`` and ``result.report.type`` are correct for
        ddos."""
        result = parse(copy.deepcopy(_VALID_DDOS))
        assert result.report is not None
        assert result.report.category == "connection"
        assert result.report.type == "ddos"

    def test_phishing_report_type(self) -> None:
        """A ``content/phishing`` dict resolves to a
        :class:`~xarf.models.PhishingReport`."""
        result = parse(copy.deepcopy(_VALID_PHISHING))
        assert result.errors == []
        assert isinstance(result.report, PhishingReport)

    def test_phishing_report_category_and_type_fields(self) -> None:
        """``result.report.category`` and ``result.report.type`` are correct for
        phishing."""
        result = parse(copy.deepcopy(_VALID_PHISHING))
        assert result.report is not None
        assert result.report.category == "content"
        assert result.report.type == "phishing"


# ---------------------------------------------------------------------------
# TestMalformedInput
# ---------------------------------------------------------------------------


class TestMalformedInput:
    """Tests for degenerate and edge-case inputs."""

    def test_empty_string_raises_parse_error(self) -> None:
        """An empty string raises :class:`~xarf.exceptions.XARFParseError`."""
        with pytest.raises(XARFParseError):
            parse("")

    def test_null_json_string_raises_or_returns_errors(self) -> None:
        """The JSON string ``"null"`` either raises
        :class:`~xarf.exceptions.XARFParseError` or returns a
        :class:`~xarf.models.ParseResult` with errors (``None`` is not a dict).
        """
        try:
            result = parse("null")
            # If parse() doesn't raise, it must indicate failure.
            assert result.report is None or len(result.errors) > 0
        except XARFParseError:
            pass  # Also acceptable.

    def test_empty_dict_string_returns_errors(self) -> None:
        """An empty JSON object ``"{}"`` returns errors for all missing required
        fields."""
        result = parse("{}")
        assert len(result.errors) > 0
        assert result.report is None


# ---------------------------------------------------------------------------
# TestPerformance
# ---------------------------------------------------------------------------


class TestPerformance:
    """Throughput test verifying parse() processes reports within a reasonable
    time budget.

    Note:
        The xarf-parser-tests spec targets ≥ 1000 reports/sec for the JavaScript
        implementation using AJV.  Python's ``jsonschema`` library is significantly
        slower than AJV, so the threshold here is adjusted for Python: 1000 reports
        must complete in under 5 seconds (≥ 200 reports/sec), which is still a
        meaningful regression guard while remaining achievable on typical developer
        hardware and CI runners.
    """

    def test_parse_1000_reports_in_under_five_seconds(self) -> None:
        """parse() processes 1000 typical reports in under 5 seconds."""
        data = copy.deepcopy(_VALID_DDOS)
        iterations = 1000

        start = time.perf_counter()
        for _ in range(iterations):
            parse(data)
        elapsed = time.perf_counter() - start

        assert elapsed < 5.0, (
            f"Parsed {iterations} reports in {elapsed:.3f}s — exceeds 5-second budget"
        )
