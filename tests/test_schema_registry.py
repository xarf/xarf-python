"""Tests for Phase 2: Schema Registry."""

from __future__ import annotations

import pytest

from xarf.schema_registry import (
    FieldMetadata,
    SchemaRegistry,
    get_registry,
    reset_registry,
    schema_registry,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_registry_after_test() -> None:
    """Reset the module-level singleton after every test for isolation."""
    yield
    reset_registry()


# ---------------------------------------------------------------------------
# Singleton behaviour
# ---------------------------------------------------------------------------


class TestSingleton:
    def test_get_registry_returns_same_instance(self) -> None:
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_module_level_alias_is_a_loaded_registry(self) -> None:
        # schema_registry is created eagerly at import time and may differ from
        # a fresh get_registry() call (if reset_registry() ran between them).
        # What matters is that both are functional SchemaRegistry instances.
        r = get_registry()
        assert isinstance(schema_registry, SchemaRegistry)
        assert schema_registry.is_loaded()
        assert isinstance(r, SchemaRegistry)
        assert r.is_loaded()

    def test_reset_registry_clears_singleton(self) -> None:
        r1 = get_registry()
        reset_registry()
        r2 = get_registry()
        assert r1 is not r2

    def test_reset_registry_new_instance_is_functional(self) -> None:
        reset_registry()
        r = get_registry()
        assert r.is_loaded()
        assert "messaging" in r.get_categories()


# ---------------------------------------------------------------------------
# is_loaded
# ---------------------------------------------------------------------------


class TestIsLoaded:
    def test_is_loaded_after_normal_init(self) -> None:
        assert get_registry().is_loaded()


# ---------------------------------------------------------------------------
# get_categories
# ---------------------------------------------------------------------------


class TestGetCategories:
    EXPECTED_CATEGORIES = {
        "messaging",
        "connection",
        "content",
        "infrastructure",
        "copyright",
        "vulnerability",
        "reputation",
    }

    def test_returns_all_seven_categories(self) -> None:
        cats = get_registry().get_categories()
        assert cats == self.EXPECTED_CATEGORIES

    def test_result_is_cached(self) -> None:
        r = get_registry()
        assert r.get_categories() is r.get_categories()


# ---------------------------------------------------------------------------
# get_types_for_category
# ---------------------------------------------------------------------------


class TestGetTypesForCategory:
    def test_messaging_types(self) -> None:
        types = get_registry().get_types_for_category("messaging")
        assert "spam" in types
        assert "bulk_messaging" in types

    def test_connection_types(self) -> None:
        types = get_registry().get_types_for_category("connection")
        expected = {
            "login_attack",
            "port_scan",
            "ddos",
            "infected_host",
            "reconnaissance",
            "scraping",
            "sql_injection",
            "vulnerability_scan",
        }
        assert expected.issubset(types)

    def test_content_types(self) -> None:
        types = get_registry().get_types_for_category("content")
        assert "phishing" in types
        assert "malware" in types

    def test_infrastructure_types(self) -> None:
        types = get_registry().get_types_for_category("infrastructure")
        assert "botnet" in types
        assert "compromised_server" in types

    def test_copyright_types(self) -> None:
        types = get_registry().get_types_for_category("copyright")
        assert "copyright" in types
        assert "p2p" in types

    def test_vulnerability_types(self) -> None:
        types = get_registry().get_types_for_category("vulnerability")
        assert "cve" in types
        assert "open_service" in types
        assert "misconfiguration" in types

    def test_reputation_types(self) -> None:
        types = get_registry().get_types_for_category("reputation")
        assert "blocklist" in types
        assert "threat_intelligence" in types

    def test_unknown_category_returns_empty_set(self) -> None:
        assert get_registry().get_types_for_category("nonexistent") == set()


# ---------------------------------------------------------------------------
# get_all_types
# ---------------------------------------------------------------------------


class TestGetAllTypes:
    def test_returns_dict(self) -> None:
        assert isinstance(get_registry().get_all_types(), dict)

    def test_contains_all_categories(self) -> None:
        all_types = get_registry().get_all_types()
        expected_categories = {
            "messaging",
            "connection",
            "content",
            "infrastructure",
            "copyright",
            "vulnerability",
            "reputation",
        }
        assert expected_categories.issubset(all_types.keys())

    def test_result_is_cached(self) -> None:
        r = get_registry()
        assert r.get_all_types() is r.get_all_types()


# ---------------------------------------------------------------------------
# is_valid_category
# ---------------------------------------------------------------------------


class TestIsValidCategory:
    def test_valid_categories(self) -> None:
        r = get_registry()
        for cat in (
            "messaging",
            "connection",
            "content",
            "infrastructure",
            "copyright",
            "vulnerability",
            "reputation",
        ):
            assert r.is_valid_category(cat) is True

    def test_invalid_category(self) -> None:
        assert get_registry().is_valid_category("abuse") is False
        assert get_registry().is_valid_category("") is False
        assert get_registry().is_valid_category("MESSAGING") is False


# ---------------------------------------------------------------------------
# is_valid_type
# ---------------------------------------------------------------------------


class TestIsValidType:
    def test_valid_pair(self) -> None:
        assert get_registry().is_valid_type("messaging", "spam") is True

    def test_valid_pair_with_underscore_type(self) -> None:
        assert get_registry().is_valid_type("connection", "login_attack") is True

    def test_invalid_type_for_valid_category(self) -> None:
        assert get_registry().is_valid_type("messaging", "ddos") is False

    def test_invalid_category(self) -> None:
        assert get_registry().is_valid_type("nonexistent", "spam") is False

    def test_both_invalid(self) -> None:
        assert get_registry().is_valid_type("nope", "nope") is False


# ---------------------------------------------------------------------------
# get_required_fields
# ---------------------------------------------------------------------------


class TestGetRequiredFields:
    EXPECTED_REQUIRED = {
        "xarf_version",
        "report_id",
        "timestamp",
        "reporter",
        "sender",
        "source_identifier",
        "category",
        "type",
    }

    def test_returns_exact_core_required_fields(self) -> None:
        assert get_registry().get_required_fields() == self.EXPECTED_REQUIRED

    def test_result_is_cached(self) -> None:
        r = get_registry()
        assert r.get_required_fields() is r.get_required_fields()


# ---------------------------------------------------------------------------
# get_contact_required_fields
# ---------------------------------------------------------------------------


class TestGetContactRequiredFields:
    def test_returns_exact_contact_required_fields(self) -> None:
        assert get_registry().get_contact_required_fields() == {
            "org",
            "contact",
            "domain",
        }

    def test_result_is_cached(self) -> None:
        r = get_registry()
        assert r.get_contact_required_fields() is r.get_contact_required_fields()


# ---------------------------------------------------------------------------
# get_field_metadata
# ---------------------------------------------------------------------------


class TestGetFieldMetadata:
    def test_known_required_field(self) -> None:
        meta = get_registry().get_field_metadata("source_identifier")
        assert isinstance(meta, FieldMetadata)
        assert meta.required is True
        assert meta.recommended is False
        assert meta.description != ""

    def test_known_recommended_field(self) -> None:
        # source_port is x-recommended in the core schema
        meta = get_registry().get_field_metadata("source_port")
        assert meta is not None
        assert meta.recommended is True
        assert meta.required is False

    def test_known_optional_field(self) -> None:
        # description is an optional, non-recommended core field
        meta = get_registry().get_field_metadata("description")
        assert meta is not None
        assert meta.required is False
        assert meta.recommended is False
        assert meta.type == "string"

    def test_known_recommended_numeric_field(self) -> None:
        # confidence is x-recommended with numeric constraints
        meta = get_registry().get_field_metadata("confidence")
        assert meta is not None
        assert meta.required is False
        assert meta.recommended is True
        assert meta.minimum is not None
        assert meta.maximum is not None

    def test_unknown_field_returns_none(self) -> None:
        assert get_registry().get_field_metadata("nonexistent_field_xyz") is None

    def test_field_with_enum(self) -> None:
        # category has an enum constraint in the core schema
        meta = get_registry().get_field_metadata("category")
        assert meta is not None
        assert meta.enum is not None
        assert len(meta.enum) == 7


# ---------------------------------------------------------------------------
# get_core_property_names
# ---------------------------------------------------------------------------


class TestGetCorePropertyNames:
    def test_contains_known_fields(self) -> None:
        names = get_registry().get_core_property_names()
        for f in (
            "xarf_version",
            "report_id",
            "timestamp",
            "reporter",
            "sender",
            "source_identifier",
            "category",
            "type",
        ):
            assert f in names


# ---------------------------------------------------------------------------
# get_type_schema
# ---------------------------------------------------------------------------


class TestGetTypeSchema:
    def test_known_type_returns_dict(self) -> None:
        schema = get_registry().get_type_schema("messaging", "spam")
        assert isinstance(schema, dict)
        assert "allOf" in schema or "properties" in schema

    def test_unknown_type_returns_none(self) -> None:
        assert get_registry().get_type_schema("messaging", "nonexistent") is None

    def test_unknown_category_returns_none(self) -> None:
        assert get_registry().get_type_schema("nope", "spam") is None

    def test_all_known_type_schemas_loadable(self) -> None:
        r = get_registry()
        for category, types in r.get_all_types().items():
            for type_ in types:
                schema = r.get_type_schema(category, type_)
                assert schema is not None, f"Missing schema for {category}/{type_}"


# ---------------------------------------------------------------------------
# get_category_fields
# ---------------------------------------------------------------------------


class TestGetCategoryFields:
    def test_spam_has_type_specific_fields(self) -> None:
        fields = get_registry().get_category_fields("messaging", "spam")
        # protocol is spam-specific (not in core schema)
        assert "protocol" in fields

    def test_excludes_core_fields(self) -> None:
        core_fields = get_registry().get_core_property_names()
        fields = get_registry().get_category_fields("messaging", "spam")
        for f in fields:
            assert f not in core_fields, f"Core field '{f}' leaked into category fields"

    def test_excludes_category_and_type_meta_fields(self) -> None:
        fields = get_registry().get_category_fields("messaging", "spam")
        assert "category" not in fields
        assert "type" not in fields

    def test_unknown_type_returns_empty_list(self) -> None:
        assert get_registry().get_category_fields("messaging", "nonexistent") == []

    def test_content_base_fields_are_included_via_ref(self) -> None:
        # content types use allOf $ref to content-base.json;
        # content-base fields should appear in get_category_fields
        fields = get_registry().get_category_fields("content", "phishing")
        # url is a content-base field
        assert "url" in fields

    def test_no_duplicate_fields(self) -> None:
        fields = get_registry().get_category_fields("content", "phishing")
        assert len(fields) == len(set(fields))


# ---------------------------------------------------------------------------
# get_all_fields_for_category
# ---------------------------------------------------------------------------


class TestGetAllFieldsForCategory:
    def test_messaging_union_includes_fields_from_both_types(self) -> None:
        fields = get_registry().get_all_fields_for_category("messaging")
        # spam-specific (not in bulk_messaging)
        assert "spam_indicators" in fields
        # bulk_messaging-specific (not in spam)
        assert "unsubscribe_provided" in fields

    def test_excludes_core_fields(self) -> None:
        core_fields = get_registry().get_core_property_names()
        all_fields = get_registry().get_all_fields_for_category("connection")
        for f in all_fields:
            assert f not in core_fields, (
                f"Core field '{f}' leaked into get_all_fields_for_category"
            )  # noqa: E501

    def test_unknown_category_returns_empty_set(self) -> None:
        assert get_registry().get_all_fields_for_category("nonexistent") == set()

    def test_is_superset_of_single_type_fields(self) -> None:
        r = get_registry()
        spam_fields = set(r.get_category_fields("messaging", "spam"))
        all_messaging = r.get_all_fields_for_category("messaging")
        assert spam_fields.issubset(all_messaging)
