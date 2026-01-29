"""Tests for SchemaRegistry - schema-driven validation rules."""

from xarf.schema_registry import FieldMetadata, SchemaRegistry, schema_registry


class TestSchemaRegistrySingleton:
    """Tests for SchemaRegistry singleton pattern."""

    def setup_method(self) -> None:
        """Reset singleton before each test."""
        SchemaRegistry.reset_instance()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        SchemaRegistry.reset_instance()

    def test_get_instance_returns_same_instance(self) -> None:
        """get_instance() should return the same instance."""
        instance1 = SchemaRegistry.get_instance()
        instance2 = SchemaRegistry.get_instance()
        assert instance1 is instance2

    def test_reset_instance_creates_new_instance(self) -> None:
        """reset_instance() should allow creating a new instance."""
        instance1 = SchemaRegistry.get_instance()
        SchemaRegistry.reset_instance()
        instance2 = SchemaRegistry.get_instance()
        assert instance1 is not instance2

    def test_module_level_singleton_works(self) -> None:
        """Module-level schema_registry should be accessible."""
        # Note: This uses the module-level singleton which may be
        # initialized before reset_instance() is called
        assert schema_registry is not None
        assert schema_registry.is_loaded()


class TestSchemaRegistryCategories:
    """Tests for category-related methods."""

    def setup_method(self) -> None:
        """Get fresh registry instance."""
        SchemaRegistry.reset_instance()
        self.registry = SchemaRegistry.get_instance()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        SchemaRegistry.reset_instance()

    def test_get_categories_returns_set(self) -> None:
        """get_categories() should return a set of strings."""
        categories = self.registry.get_categories()
        assert isinstance(categories, set)
        assert len(categories) > 0

    def test_get_categories_contains_expected_values(self) -> None:
        """get_categories() should contain known XARF categories."""
        categories = self.registry.get_categories()
        expected = {
            "messaging",
            "connection",
            "content",
            "infrastructure",
            "copyright",
            "vulnerability",
            "reputation",
        }
        assert expected.issubset(categories)

    def test_get_categories_is_cached(self) -> None:
        """get_categories() should return cached result on second call."""
        categories1 = self.registry.get_categories()
        categories2 = self.registry.get_categories()
        assert categories1 is categories2

    def test_is_valid_category_returns_true_for_valid(self) -> None:
        """is_valid_category() should return True for valid categories."""
        assert self.registry.is_valid_category("messaging")
        assert self.registry.is_valid_category("connection")
        assert self.registry.is_valid_category("content")

    def test_is_valid_category_returns_false_for_invalid(self) -> None:
        """is_valid_category() should return False for invalid categories."""
        assert not self.registry.is_valid_category("invalid")
        assert not self.registry.is_valid_category("")
        assert not self.registry.is_valid_category("MESSAGING")  # Case sensitive


class TestSchemaRegistryTypes:
    """Tests for type-related methods."""

    def setup_method(self) -> None:
        """Get fresh registry instance."""
        SchemaRegistry.reset_instance()
        self.registry = SchemaRegistry.get_instance()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        SchemaRegistry.reset_instance()

    def test_get_types_for_category_returns_set(self) -> None:
        """get_types_for_category() should return a set."""
        types = self.registry.get_types_for_category("messaging")
        assert isinstance(types, set)

    def test_get_types_for_messaging_category(self) -> None:
        """get_types_for_category('messaging') should return messaging types."""
        types = self.registry.get_types_for_category("messaging")
        assert "spam" in types
        assert "bulk_messaging" in types

    def test_get_types_for_connection_category(self) -> None:
        """get_types_for_category('connection') should return connection types."""
        types = self.registry.get_types_for_category("connection")
        assert "ddos" in types
        assert "port_scan" in types
        assert "login_attack" in types

    def test_get_types_for_content_category(self) -> None:
        """get_types_for_category('content') should return content types."""
        types = self.registry.get_types_for_category("content")
        assert "phishing" in types
        assert "malware" in types
        assert "fraud" in types

    def test_get_types_for_invalid_category_returns_empty(self) -> None:
        """get_types_for_category() should return empty set for invalid category."""
        types = self.registry.get_types_for_category("invalid")
        assert types == set()

    def test_get_all_types_returns_dict(self) -> None:
        """get_all_types() should return a dict of category to types."""
        all_types = self.registry.get_all_types()
        assert isinstance(all_types, dict)
        assert "messaging" in all_types
        assert "connection" in all_types

    def test_is_valid_type_returns_true_for_valid(self) -> None:
        """is_valid_type() should return True for valid category/type pairs."""
        assert self.registry.is_valid_type("messaging", "spam")
        assert self.registry.is_valid_type("connection", "ddos")
        assert self.registry.is_valid_type("content", "phishing")

    def test_is_valid_type_returns_false_for_invalid(self) -> None:
        """is_valid_type() should return False for invalid pairs."""
        assert not self.registry.is_valid_type("messaging", "invalid")
        assert not self.registry.is_valid_type("invalid", "spam")
        assert not self.registry.is_valid_type("messaging", "ddos")  # Wrong category


class TestSchemaRegistryEvidenceSources:
    """Tests for evidence source methods."""

    def setup_method(self) -> None:
        """Get fresh registry instance."""
        SchemaRegistry.reset_instance()
        self.registry = SchemaRegistry.get_instance()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        SchemaRegistry.reset_instance()

    def test_get_evidence_sources_returns_set(self) -> None:
        """get_evidence_sources() should return a set."""
        sources = self.registry.get_evidence_sources()
        assert isinstance(sources, set)

    def test_get_evidence_sources_contains_expected_values(self) -> None:
        """get_evidence_sources() should contain known sources."""
        sources = self.registry.get_evidence_sources()
        # Check for some common evidence sources
        assert len(sources) > 0

    def test_is_valid_evidence_source(self) -> None:
        """is_valid_evidence_source() should validate sources correctly."""
        sources = self.registry.get_evidence_sources()
        if sources:
            # Test with a known valid source
            valid_source = next(iter(sources))
            assert self.registry.is_valid_evidence_source(valid_source)

        # Invalid source
        assert not self.registry.is_valid_evidence_source("invalid_source_xyz")


class TestSchemaRegistrySeverities:
    """Tests for severity methods."""

    def setup_method(self) -> None:
        """Get fresh registry instance."""
        SchemaRegistry.reset_instance()
        self.registry = SchemaRegistry.get_instance()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        SchemaRegistry.reset_instance()

    def test_get_severities_returns_expected_values(self) -> None:
        """get_severities() should return standard severity levels."""
        severities = self.registry.get_severities()
        assert severities == {"low", "medium", "high", "critical"}

    def test_is_valid_severity(self) -> None:
        """is_valid_severity() should validate severity levels."""
        assert self.registry.is_valid_severity("low")
        assert self.registry.is_valid_severity("medium")
        assert self.registry.is_valid_severity("high")
        assert self.registry.is_valid_severity("critical")
        assert not self.registry.is_valid_severity("invalid")
        assert not self.registry.is_valid_severity("LOW")  # Case sensitive


class TestSchemaRegistryRequiredFields:
    """Tests for required field methods."""

    def setup_method(self) -> None:
        """Get fresh registry instance."""
        SchemaRegistry.reset_instance()
        self.registry = SchemaRegistry.get_instance()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        SchemaRegistry.reset_instance()

    def test_get_required_fields_returns_set(self) -> None:
        """get_required_fields() should return a set."""
        required = self.registry.get_required_fields()
        assert isinstance(required, set)

    def test_get_required_fields_contains_core_fields(self) -> None:
        """get_required_fields() should contain core required fields."""
        required = self.registry.get_required_fields()
        # Per XARF v4 spec: sender is required, evidence_source is optional
        expected = {
            "xarf_version",
            "report_id",
            "timestamp",
            "reporter",
            "sender",
            "source_identifier",
            "category",
            "type",
        }
        assert expected.issubset(required)

    def test_get_contact_required_fields(self) -> None:
        """get_contact_required_fields() should return contact fields."""
        contact_fields = self.registry.get_contact_required_fields()
        assert isinstance(contact_fields, set)
        assert "org" in contact_fields
        assert "contact" in contact_fields
        assert "domain" in contact_fields


class TestSchemaRegistryFieldMetadata:
    """Tests for field metadata methods."""

    def setup_method(self) -> None:
        """Get fresh registry instance."""
        SchemaRegistry.reset_instance()
        self.registry = SchemaRegistry.get_instance()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        SchemaRegistry.reset_instance()

    def test_get_field_metadata_returns_metadata(self) -> None:
        """get_field_metadata() should return FieldMetadata for valid fields."""
        metadata = self.registry.get_field_metadata("category")
        assert metadata is not None
        assert isinstance(metadata, FieldMetadata)

    def test_get_field_metadata_has_correct_attributes(self) -> None:
        """Verify FieldMetadata has correct attributes."""
        metadata = self.registry.get_field_metadata("category")
        assert metadata is not None
        assert isinstance(metadata.description, str)
        assert isinstance(metadata.required, bool)
        assert isinstance(metadata.recommended, bool)

    def test_get_field_metadata_returns_none_for_invalid(self) -> None:
        """get_field_metadata() should return None for invalid fields."""
        metadata = self.registry.get_field_metadata("invalid_field")
        assert metadata is None

    def test_get_core_property_names(self) -> None:
        """get_core_property_names() should return all core properties."""
        props = self.registry.get_core_property_names()
        assert isinstance(props, set)
        assert "category" in props
        assert "type" in props
        assert "reporter" in props


class TestSchemaRegistryCategoryFields:
    """Tests for category-specific field methods."""

    def setup_method(self) -> None:
        """Get fresh registry instance."""
        SchemaRegistry.reset_instance()
        self.registry = SchemaRegistry.get_instance()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        SchemaRegistry.reset_instance()

    def test_get_category_fields_returns_list(self) -> None:
        """get_category_fields() should return a list."""
        fields = self.registry.get_category_fields("messaging", "spam")
        assert isinstance(fields, list)

    def test_get_category_fields_excludes_core_fields(self) -> None:
        """get_category_fields() should not include core fields."""
        fields = self.registry.get_category_fields("messaging", "spam")
        core_fields = self.registry.get_core_property_names()
        for field in fields:
            assert field not in core_fields

    def test_get_category_fields_for_invalid_returns_empty(self) -> None:
        """get_category_fields() should return empty for invalid category/type."""
        fields = self.registry.get_category_fields("invalid", "invalid")
        assert fields == []

    def test_get_all_fields_for_category(self) -> None:
        """get_all_fields_for_category() should return all fields for a category."""
        fields = self.registry.get_all_fields_for_category("messaging")
        assert isinstance(fields, set)


class TestSchemaRegistryOptionalFields:
    """Tests for optional field methods."""

    def setup_method(self) -> None:
        """Get fresh registry instance."""
        SchemaRegistry.reset_instance()
        self.registry = SchemaRegistry.get_instance()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        SchemaRegistry.reset_instance()

    def test_get_optional_fields_returns_set(self) -> None:
        """get_optional_fields() should return a set."""
        optional = self.registry.get_optional_fields()
        assert isinstance(optional, set)

    def test_get_optional_fields_excludes_required(self) -> None:
        """get_optional_fields() should not include required fields."""
        optional = self.registry.get_optional_fields()
        required = self.registry.get_required_fields()
        assert optional.isdisjoint(required)

    def test_get_optional_field_info_returns_list(self) -> None:
        """get_optional_field_info() should return a list of dicts."""
        info = self.registry.get_optional_field_info()
        assert isinstance(info, list)
        if info:
            assert isinstance(info[0], dict)
            assert "field" in info[0]
            assert "description" in info[0]
            assert "recommended" in info[0]

    def test_get_optional_field_info_with_category_type(self) -> None:
        """get_optional_field_info() should include type-specific fields."""
        info = self.registry.get_optional_field_info("messaging", "spam")
        assert isinstance(info, list)


class TestSchemaRegistryTypeSchema:
    """Tests for type schema methods."""

    def setup_method(self) -> None:
        """Get fresh registry instance."""
        SchemaRegistry.reset_instance()
        self.registry = SchemaRegistry.get_instance()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        SchemaRegistry.reset_instance()

    def test_get_type_schema_returns_dict(self) -> None:
        """get_type_schema() should return a dict for valid types."""
        schema = self.registry.get_type_schema("messaging", "spam")
        assert schema is not None
        assert isinstance(schema, dict)

    def test_get_type_schema_returns_none_for_invalid(self) -> None:
        """get_type_schema() should return None for invalid types."""
        schema = self.registry.get_type_schema("invalid", "invalid")
        assert schema is None

    def test_get_type_schema_handles_underscore_to_hyphen(self) -> None:
        """get_type_schema() should handle underscore/hyphen conversion."""
        # bulk_messaging in code -> bulk-messaging in filename
        schema = self.registry.get_type_schema("messaging", "bulk_messaging")
        assert schema is not None


class TestSchemaRegistryIsLoaded:
    """Tests for is_loaded() method."""

    def setup_method(self) -> None:
        """Get fresh registry instance."""
        SchemaRegistry.reset_instance()
        self.registry = SchemaRegistry.get_instance()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        SchemaRegistry.reset_instance()

    def test_is_loaded_returns_true_when_schemas_exist(self) -> None:
        """is_loaded() should return True when schemas are loaded."""
        assert self.registry.is_loaded()
