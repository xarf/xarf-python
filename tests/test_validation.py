"""Comprehensive validation tests for all XARF categories."""

from xarf import XARFParser


class TestCategoryValidation:
    """Test validation for all 8 XARF categories."""

    def test_messaging_category_valid(self):
        """Test valid messaging category report."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-messaging-001",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Email Provider",
                "contact": "abuse@emailprovider.com",
                "domain": "emailprovider.com",
            },
            "sender": {
                "org": "Email Provider",
                "contact": "abuse@emailprovider.com",
                "domain": "emailprovider.com",
            },
            "source_identifier": "192.0.2.1",
            "category": "messaging",
            "type": "spam",
            "evidence_source": "spamtrap",
        }

        parser = XARFParser()
        report = parser.parse(report_data)
        assert report.category == "messaging"
        assert report.type == "spam"

    def test_connection_category_valid(self):
        """Test valid connection category report."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-connection-001",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Network Monitor",
                "contact": "security@network.com",
                "domain": "network.com",
            },
            "sender": {
                "org": "Network Monitor",
                "contact": "security@network.com",
                "domain": "network.com",
            },
            "source_identifier": "192.0.2.2",
            "category": "connection",
            "type": "ddos",
            "evidence_source": "honeypot",
            "destination_ip": "203.0.113.1",
            "protocol": "tcp",
        }

        parser = XARFParser()
        report = parser.parse(report_data)
        assert report.category == "connection"
        assert report.type == "ddos"

    def test_content_category_valid(self):
        """Test valid content category report."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-content-001",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Web Security",
                "contact": "security@websec.com",
                "domain": "websec.com",
            },
            "sender": {
                "org": "Web Security",
                "contact": "security@websec.com",
                "domain": "websec.com",
            },
            "source_identifier": "192.0.2.3",
            "category": "content",
            "type": "phishing_site",
            "evidence_source": "user_report",
            "url": "http://phishing.example.com",
        }

        parser = XARFParser()
        report = parser.parse(report_data)
        assert report.category == "content"
        assert report.type == "phishing_site"

    def test_infrastructure_category_valid(self):
        """Test valid infrastructure category report."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-infrastructure-001",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Security Research",
                "contact": "research@security.com",
                "domain": "security.com",
            },
            "sender": {
                "org": "Security Research",
                "contact": "research@security.com",
                "domain": "security.com",
            },
            "source_identifier": "192.0.2.4",
            "category": "infrastructure",
            "type": "open_resolver",
            "evidence_source": "automated_scan",
        }

        parser = XARFParser(strict=False)
        report = parser.parse(report_data)
        assert report.category == "infrastructure"
        errors = parser.get_errors()
        # Infrastructure not in alpha, should have warning
        assert any("Unsupported category" in error for error in errors)

    def test_copyright_category_valid(self):
        """Test valid copyright category report."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-copyright-001",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Copyright Holder",
                "contact": "legal@copyright.com",
                "domain": "copyright.com",
            },
            "sender": {
                "org": "Copyright Holder",
                "contact": "legal@copyright.com",
                "domain": "copyright.com",
            },
            "source_identifier": "192.0.2.5",
            "category": "copyright",
            "type": "file_sharing",
            "evidence_source": "manual_analysis",
        }

        parser = XARFParser(strict=False)
        report = parser.parse(report_data)
        assert report.category == "copyright"

    def test_vulnerability_category_valid(self):
        """Test valid vulnerability category report."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-vulnerability-001",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Vulnerability Scanner",
                "contact": "vuln@scanner.com",
                "domain": "scanner.com",
            },
            "sender": {
                "org": "Vulnerability Scanner",
                "contact": "vuln@scanner.com",
                "domain": "scanner.com",
            },
            "source_identifier": "192.0.2.6",
            "category": "vulnerability",
            "type": "cve",
            "evidence_source": "vulnerability_scan",
        }

        parser = XARFParser(strict=False)
        report = parser.parse(report_data)
        assert report.category == "vulnerability"

    def test_reputation_category_valid(self):
        """Test valid reputation category report."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-reputation-001",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Reputation Service",
                "contact": "rep@service.com",
                "domain": "service.com",
            },
            "sender": {
                "org": "Reputation Service",
                "contact": "rep@service.com",
                "domain": "service.com",
            },
            "source_identifier": "192.0.2.7",
            "category": "reputation",
            "type": "blacklist",
            "evidence_source": "threat_intelligence",
        }

        parser = XARFParser(strict=False)
        report = parser.parse(report_data)
        assert report.category == "reputation"

    def test_other_category_valid(self):
        """Test valid other category report."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-other-001",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Other Reporter",
                "contact": "other@reporter.com",
                "domain": "reporter.com",
            },
            "sender": {
                "org": "Other Reporter",
                "contact": "other@reporter.com",
                "domain": "reporter.com",
            },
            "source_identifier": "192.0.2.8",
            "category": "other",
            "type": "custom_type",
            "evidence_source": "manual_analysis",
        }

        parser = XARFParser(strict=False)
        report = parser.parse(report_data)
        assert report.category == "other"


class TestMandatoryFields:
    """Test validation of all mandatory fields."""

    def get_valid_base_report(self):
        """Get a valid base report for testing."""
        return {
            "xarf_version": "4.0.0",
            "report_id": "test-id-001",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Test Organization",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            "sender": {
                "org": "Test Organization",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            "source_identifier": "192.0.2.1",
            "category": "messaging",
            "type": "spam",
            "evidence_source": "spamtrap",
        }

    def test_missing_xarf_version(self):
        """Test validation fails without xarf_version."""
        report_data = self.get_valid_base_report()
        del report_data["xarf_version"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False
        errors = parser.get_errors()
        assert any("Missing required fields" in error for error in errors)

    def test_missing_report_id(self):
        """Test validation fails without report_id."""
        report_data = self.get_valid_base_report()
        del report_data["report_id"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False

    def test_missing_timestamp(self):
        """Test validation fails without timestamp."""
        report_data = self.get_valid_base_report()
        del report_data["timestamp"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False

    def test_missing_reporter(self):
        """Test validation fails without reporter."""
        report_data = self.get_valid_base_report()
        del report_data["reporter"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False

    def test_missing_source_identifier(self):
        """Test validation fails without source_identifier."""
        report_data = self.get_valid_base_report()
        del report_data["source_identifier"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False

    def test_missing_category(self):
        """Test validation fails without category."""
        report_data = self.get_valid_base_report()
        del report_data["category"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False

    def test_missing_type(self):
        """Test validation fails without type."""
        report_data = self.get_valid_base_report()
        del report_data["type"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False

    def test_missing_evidence_source(self):
        """Test validation fails without evidence_source."""
        report_data = self.get_valid_base_report()
        del report_data["evidence_source"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False

    def test_invalid_xarf_version(self):
        """Test validation fails with wrong xarf_version."""
        report_data = self.get_valid_base_report()
        report_data["xarf_version"] = "3.0.0"

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False
        errors = parser.get_errors()
        assert any("Unsupported XARF version" in error for error in errors)

    def test_invalid_timestamp_format(self):
        """Test validation fails with invalid timestamp."""
        report_data = self.get_valid_base_report()
        report_data["timestamp"] = "not-a-timestamp"

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False
        errors = parser.get_errors()
        assert any("Invalid timestamp format" in error for error in errors)

    def test_missing_reporter_org(self):
        """Test validation fails without reporter.org."""
        report_data = self.get_valid_base_report()
        del report_data["reporter"]["org"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False
        errors = parser.get_errors()
        assert any("Missing reporter fields" in error for error in errors)

    def test_missing_reporter_contact(self):
        """Test validation fails without reporter.contact."""
        report_data = self.get_valid_base_report()
        del report_data["reporter"]["contact"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False

    def test_missing_reporter_domain(self):
        """Test validation fails without reporter.domain."""
        report_data = self.get_valid_base_report()
        del report_data["reporter"]["domain"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False
        errors = parser.get_errors()
        assert any("Missing reporter fields" in error for error in errors)

    def test_missing_sender_domain(self):
        """Test validation fails without sender.domain."""
        report_data = self.get_valid_base_report()
        del report_data["sender"]["domain"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False
        errors = parser.get_errors()
        assert any("Missing sender fields" in error for error in errors)


class TestCategorySpecificFields:
    """Test category-specific required fields."""

    def test_messaging_missing_protocol(self):
        """Test messaging report validation without required fields."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-id",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Test",
                "contact": "test@example.com",
                "domain": "example.com",
            },
            "sender": {
                "org": "Test",
                "contact": "test@example.com",
                "domain": "example.com",
            },
            "source_identifier": "192.0.2.1",
            "category": "messaging",
            "type": "spam",
            "evidence_source": "spamtrap",
            "protocol": "smtp",
            # Missing smtp_from and subject for spam
        }

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False
        errors = parser.get_errors()
        assert any("smtp_from required" in error for error in errors)

    def test_connection_missing_destination_ip(self):
        """Test connection report requires destination_ip."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-id",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Test",
                "contact": "test@example.com",
                "domain": "example.com",
            },
            "sender": {
                "org": "Test",
                "contact": "test@example.com",
                "domain": "example.com",
            },
            "source_identifier": "192.0.2.1",
            "category": "connection",
            "type": "ddos",
            "evidence_source": "honeypot",
            # Missing destination_ip and protocol
        }

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False
        errors = parser.get_errors()
        assert any("destination_ip required" in error for error in errors)

    def test_content_missing_url(self):
        """Test content report requires url."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-id",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Test",
                "contact": "test@example.com",
                "domain": "example.com",
            },
            "sender": {
                "org": "Test",
                "contact": "test@example.com",
                "domain": "example.com",
            },
            "source_identifier": "192.0.2.1",
            "category": "content",
            "type": "phishing_site",
            "evidence_source": "user_report",
            # Missing url
        }

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert result is False
        errors = parser.get_errors()
        assert any("url required" in error for error in errors)
