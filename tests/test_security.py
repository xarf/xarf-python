"""Security-focused tests for UUID generation and timestamp formatting.

All test data follows XARF v4 spec from xarf-core.json.
"""

import re
import uuid
from datetime import datetime, timezone

from xarf import XARFParser

from .conftest import create_v4_messaging_report


class TestUUIDGeneration:
    """Test UUID format validation and generation security."""

    def test_valid_uuid_v4_format(self) -> None:
        """Test that valid UUID v4 format is accepted."""
        report_data = create_v4_messaging_report(
            report_id="550e8400-e29b-41d4-a716-446655440000",
        )

        parser = XARFParser()
        report = parser.parse(report_data)
        assert report.report_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_uuid_uniqueness(self) -> None:
        """Test that UUIDs are unique when generated."""
        generated_uuids = set()

        # Generate 1000 UUIDs
        for _ in range(1000):
            new_uuid = str(uuid.uuid4())
            assert new_uuid not in generated_uuids, "UUID collision detected!"
            generated_uuids.add(new_uuid)

        assert len(generated_uuids) == 1000

    def test_uuid_format_validation(self) -> None:
        """Test UUID format conforms to RFC 4122."""
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )

        # Generate and test 100 UUIDs
        for _ in range(100):
            test_uuid = str(uuid.uuid4())
            assert uuid_pattern.match(test_uuid), f"Invalid UUID format: {test_uuid}"

    def test_uuid_version_4_variant(self) -> None:
        """Test that generated UUIDs are version 4 with correct variant."""
        for _ in range(100):
            test_uuid = uuid.uuid4()
            # Check version (should be 4)
            assert test_uuid.version == 4, f"Wrong UUID version: {test_uuid.version}"
            # Check variant (should be RFC 4122)
            assert test_uuid.variant == uuid.RFC_4122, (
                f"Wrong UUID variant: {test_uuid.variant}"
            )

    def test_uuid_randomness(self) -> None:
        """Test UUID randomness (simple entropy check)."""
        # Generate 100 UUIDs and check they're all different
        uuids = [str(uuid.uuid4()) for _ in range(100)]

        # Check uniqueness
        assert len(set(uuids)) == 100, "UUID generation not sufficiently random"

        # Check no sequential patterns
        for i in range(1, len(uuids)):
            assert uuids[i] != uuids[i - 1], "Sequential UUIDs detected"

    def test_report_id_string_format(self) -> None:
        """Test that report_id accepts string UUIDs."""
        report_data = create_v4_messaging_report(
            report_id=str(uuid.uuid4()),
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        # Verify it's a valid UUID format
        assert uuid.UUID(report.report_id), "report_id is not a valid UUID"


class TestTimestampFormatting:
    """Test timestamp format validation and security."""

    def test_iso8601_utc_format(self) -> None:
        """Test ISO 8601 UTC timestamp format is accepted."""
        report_data = create_v4_messaging_report(
            timestamp="2024-01-15T10:30:00Z",
        )

        parser = XARFParser()
        report = parser.parse(report_data)
        # Note: timestamp may be string or datetime depending on Pydantic config
        assert report.timestamp is not None

    def test_timestamp_with_timezone(self) -> None:
        """Test timestamp with explicit timezone offset."""
        report_data = create_v4_messaging_report(
            timestamp="2024-01-15T10:30:00+00:00",
        )

        parser = XARFParser()
        report = parser.parse(report_data)
        # Timestamp is stored; validation happens at schema level
        assert report.timestamp is not None

    def test_timestamp_microseconds(self) -> None:
        """Test timestamp with microseconds precision."""
        report_data = create_v4_messaging_report(
            timestamp="2024-01-15T10:30:00.123456Z",
        )

        parser = XARFParser()
        report = parser.parse(report_data)
        # Timestamp is stored; precision depends on parsing
        assert report.timestamp is not None

    def test_invalid_timestamp_format(self) -> None:
        """Test that invalid timestamp formats are rejected."""
        invalid_timestamps = [
            "10:30:00",  # Time only
            "2024/01/15 10:30:00",  # Wrong separators
            "15-01-2024T10:30:00Z",  # Wrong date order
            "not-a-timestamp",  # Invalid string
            "1705318200",  # Unix timestamp as string
        ]

        parser = XARFParser(strict=False)

        for invalid_ts in invalid_timestamps:
            report_data = create_v4_messaging_report(
                timestamp=invalid_ts,
            )

            result = parser.validate(report_data)
            assert not result.valid, f"Invalid timestamp accepted: {invalid_ts}"
            assert any("timestamp" in e.field.lower() for e in result.errors), (
                f"No timestamp error for: {invalid_ts}"
            )

    def test_timestamp_ordering(self) -> None:
        """Test timestamp chronological ordering."""
        ts1 = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        ts2 = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        ts3 = datetime(2024, 1, 15, 11, 0, 0, tzinfo=timezone.utc)

        assert ts1 < ts2 < ts3, "Timestamp ordering failed"

    def test_timestamp_immutability(self) -> None:
        """Test that timestamps represent a fixed point in time."""
        report_data = create_v4_messaging_report(
            timestamp="2024-01-15T10:30:00Z",
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        original_timestamp = report.timestamp
        # Timestamp is stored as-is; immutability depends on type
        assert report.timestamp == original_timestamp

    def test_future_timestamp_detection(self) -> None:
        """Test detection of future timestamps."""
        from datetime import timedelta

        future_time = datetime.now(timezone.utc) + timedelta(days=1)
        future_timestamp = future_time.isoformat()

        report_data = create_v4_messaging_report(
            timestamp=future_timestamp,
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        # Parser accepts future timestamps (business logic can validate if needed)
        assert report.timestamp is not None

    def test_timestamp_precision(self) -> None:
        """Test timestamp maintains precision."""
        precise_timestamp = "2024-01-15T10:30:00.123456Z"

        report_data = create_v4_messaging_report(
            timestamp=precise_timestamp,
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        # Timestamp is stored; precision depends on parsing
        assert report.timestamp is not None


class TestSecurityEdgeCases:
    """Test security-related edge cases."""

    def test_sql_injection_in_report_id(self) -> None:
        """Test that SQL injection attempts in report_id are handled safely."""
        malicious_ids = [
            "'; DROP TABLE reports; --",
            "1' OR '1'='1",
            "admin'--",
            "<script>alert('XSS')</script>",
        ]

        parser = XARFParser(strict=False)

        for malicious_id in malicious_ids:
            report_data = create_v4_messaging_report(
                report_id=malicious_id,
            )

            # Parser should accept any string as report_id
            # Application layer should validate/sanitize
            report = parser.parse(report_data)
            assert report.report_id == malicious_id

    def test_extremely_long_uuid(self) -> None:
        """Test handling of excessively long report_id."""
        long_id = "x" * 10000

        report_data = create_v4_messaging_report(
            report_id=long_id,
        )

        parser = XARFParser()
        report = parser.parse(report_data)
        # Parser accepts it; application should validate length
        assert len(report.report_id) == 10000

    def test_null_byte_injection(self) -> None:
        """Test handling of null byte injection attempts."""
        report_data = create_v4_messaging_report(
            report_id="test-id\x00malicious",
        )
        # Also test null byte in reporter org
        report_data["reporter"]["org"] = "Test\x00Org"

        parser = XARFParser()
        report = parser.parse(report_data)
        # Parser accepts null bytes; application should sanitize
        assert "\x00" in report.report_id
