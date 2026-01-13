"""Schema Registry - Centralized schema-driven validation rules.

Extracts validation rules dynamically from XARF JSON schemas,
eliminating hardcoded validation lists throughout the codebase.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .exceptions import XARFSchemaError
from .schema_utils import (
    get_v4_schemas_directory,
    list_type_schemas,
    load_json_schema,
    parse_type_schema_filename,
)


@dataclass
class FieldMetadata:
    """Field metadata extracted from schema."""

    description: str
    required: bool
    recommended: bool
    field_type: str | None = None
    enum: list[str] | None = None
    format: str | None = None
    minimum: float | None = None
    maximum: float | None = None


class SchemaRegistry:
    """Singleton for accessing schema-derived validation rules.

    Provides centralized access to:
    - Valid categories (from xarf-core.json enum)
    - Valid types per category (from types/*.json filenames)
    - Valid evidence sources (from schema)
    - Required and optional fields
    - Field metadata including descriptions
    """

    _instance: SchemaRegistry | None = None

    def __init__(self) -> None:
        """Initialize the schema registry.

        Note: Use get_instance() instead of direct instantiation.
        """
        self._schemas_dir: Path | None = None
        self._core_schema: dict[str, Any] | None = None
        self._type_schemas: dict[str, dict[str, Any]] = {}

        # Cached validation data
        self._categories_cache: set[str] | None = None
        self._types_per_category_cache: dict[str, set[str]] | None = None
        self._evidence_sources_cache: set[str] | None = None
        self._severities_cache: set[str] | None = None
        self._required_fields_cache: set[str] | None = None
        self._contact_required_fields_cache: set[str] | None = None

        # Load schemas
        self._load_schemas()

    @classmethod
    def get_instance(cls) -> SchemaRegistry:
        """Get the singleton instance.

        Returns:
            SchemaRegistry instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None

    def _load_schemas(self) -> None:
        """Load all schemas from the schemas directory."""
        try:
            self._schemas_dir = get_v4_schemas_directory()
            self._load_core_schema()
            self._scan_type_schemas()
        except XARFSchemaError:
            # Schemas not found - registry will operate in degraded mode
            pass

    def _load_core_schema(self) -> None:
        """Load the core schema."""
        if self._schemas_dir is None:
            return
        core_path = self._schemas_dir / "xarf-core.json"
        self._core_schema = load_json_schema(core_path)

    def _scan_type_schemas(self) -> None:
        """Scan type schemas directory and build category->types map."""
        try:
            type_files = list_type_schemas()
        except XARFSchemaError:
            return

        for schema_path in type_files:
            filename = schema_path.name

            # Skip base schemas (they're referenced, not standalone types)
            if "-base.json" in filename:
                continue

            try:
                category, type_name = parse_type_schema_filename(filename)
                schema = load_json_schema(schema_path)
                # Store with category/type key
                self._type_schemas[f"{category}/{type_name}"] = schema
            except XARFSchemaError:
                # Skip invalid schema files
                continue

    def get_categories(self) -> set[str]:
        """Get all valid categories from schema.

        Returns:
            Set of valid category names.
        """
        if self._categories_cache is not None:
            return self._categories_cache

        categories: set[str] = set()

        if self._core_schema:
            props = self._core_schema.get("properties", {})
            category_prop = props.get("category", {})
            enum_values = category_prop.get("enum", [])
            categories = set(enum_values)

        self._categories_cache = categories
        return categories

    def get_types_for_category(self, category: str) -> set[str]:
        """Get valid types for a specific category.

        Args:
            category: The category to get types for.

        Returns:
            Set of valid type names for the category.
        """
        if self._types_per_category_cache is None:
            self._build_types_cache()

        return self._types_per_category_cache.get(category, set())  # type: ignore[union-attr]

    def get_all_types(self) -> dict[str, set[str]]:
        """Get all types organized by category.

        Returns:
            Dict mapping category to set of types.
        """
        if self._types_per_category_cache is None:
            self._build_types_cache()

        return self._types_per_category_cache or {}

    def _build_types_cache(self) -> None:
        """Build the types per category cache from scanned schemas."""
        self._types_per_category_cache = {}

        for key in self._type_schemas:
            parts = key.split("/")
            if len(parts) != 2:
                continue

            category, type_name = parts

            if category not in self._types_per_category_cache:
                self._types_per_category_cache[category] = set()

            # Convert filename format (e.g., "bulk-messaging") to schema format
            # (e.g., "bulk_messaging")
            normalized_type = type_name.replace("-", "_")
            self._types_per_category_cache[category].add(normalized_type)

    def is_valid_category(self, category: str) -> bool:
        """Check if a category is valid.

        Args:
            category: Category to check.

        Returns:
            True if valid.
        """
        return category in self.get_categories()

    def is_valid_type(self, category: str, type_name: str) -> bool:
        """Check if a type is valid for a category.

        Args:
            category: The category.
            type_name: The type to check.

        Returns:
            True if valid.
        """
        return type_name in self.get_types_for_category(category)

    def _extract_core_evidence_sources(self, sources: set[str]) -> None:
        """Extract evidence sources from core schema examples.

        Args:
            sources: Set to add sources to.
        """
        if not self._core_schema:
            return

        props = self._core_schema.get("properties", {})
        evidence_source_prop = props.get("evidence_source", {})
        examples = evidence_source_prop.get("examples", [])

        for example in examples:
            if isinstance(example, str):
                sources.add(example)

    def _extract_type_evidence_sources(self, sources: set[str]) -> None:
        """Extract evidence sources from type schemas.

        Args:
            sources: Set to add sources to.
        """
        for schema in self._type_schemas.values():
            self._extract_evidence_sources_from_schema(schema, sources)

    def _extract_evidence_sources_from_schema(
        self, schema: dict[str, Any], sources: set[str]
    ) -> None:
        """Extract evidence sources from a single schema.

        Args:
            schema: Schema to extract from.
            sources: Set to add sources to.
        """
        all_of = schema.get("allOf", [])
        for sub_schema in all_of:
            props = sub_schema.get("properties", {})
            evidence_source_prop = props.get("evidence_source", {})
            enum_values = evidence_source_prop.get("enum", [])
            for source in enum_values:
                sources.add(source)

    def get_evidence_sources(self) -> set[str]:
        """Get valid evidence sources from schema.

        Returns:
            Set of valid evidence source values.
        """
        if self._evidence_sources_cache is not None:
            return self._evidence_sources_cache

        sources: set[str] = set()
        self._extract_core_evidence_sources(sources)
        self._extract_type_evidence_sources(sources)

        self._evidence_sources_cache = sources
        return sources

    def is_valid_evidence_source(self, source: str) -> bool:
        """Check if an evidence source is valid.

        Args:
            source: Evidence source to check.

        Returns:
            True if valid.
        """
        return source in self.get_evidence_sources()

    def get_severities(self) -> set[str]:
        """Get valid severity levels.

        Returns:
            Set of valid severity values.
        """
        if self._severities_cache is not None:
            return self._severities_cache

        # Standard XARF severities
        self._severities_cache = {"low", "medium", "high", "critical"}
        return self._severities_cache

    def is_valid_severity(self, severity: str) -> bool:
        """Check if a severity is valid.

        Args:
            severity: Severity to check.

        Returns:
            True if valid.
        """
        return severity in self.get_severities()

    def get_required_fields(self) -> set[str]:
        """Get required fields from core schema.

        Returns:
            Set of required field names.
        """
        if self._required_fields_cache is not None:
            return self._required_fields_cache

        required = self._core_schema.get("required", []) if self._core_schema else []
        self._required_fields_cache = set(required)
        return self._required_fields_cache

    def get_contact_required_fields(self) -> set[str]:
        """Get required contact info fields.

        Returns:
            Set of required contact field names.
        """
        if self._contact_required_fields_cache is not None:
            return self._contact_required_fields_cache

        default_fields = {"org", "contact", "domain"}

        if self._core_schema:
            defs = self._core_schema.get("$defs", {})
            contact_def = defs.get("contact_info", {})
            required = contact_def.get("required", [])
            if required:
                self._contact_required_fields_cache = set(required)
                return self._contact_required_fields_cache

        self._contact_required_fields_cache = default_fields
        return self._contact_required_fields_cache

    def get_type_schema(self, category: str, type_name: str) -> dict[str, Any] | None:
        """Get type-specific schema for a category/type combination.

        Args:
            category: The category.
            type_name: The type.

        Returns:
            Schema definition or None.
        """
        # Try exact match first
        exact_key = f"{category}/{type_name}"
        if exact_key in self._type_schemas:
            return self._type_schemas[exact_key]

        # Try with underscores converted to hyphens (filename format)
        hyphenated_type = type_name.replace("_", "-")
        hyphen_key = f"{category}/{hyphenated_type}"
        if hyphen_key in self._type_schemas:
            return self._type_schemas[hyphen_key]

        return None

    def get_field_metadata(self, field_name: str) -> FieldMetadata | None:
        """Get field metadata from schema.

        Args:
            field_name: Name of the field.

        Returns:
            Field metadata or None.
        """
        if not self._core_schema:
            return None

        props = self._core_schema.get("properties", {})
        prop = props.get(field_name)

        if not prop:
            return None

        return FieldMetadata(
            description=prop.get("description", ""),
            required=field_name in self.get_required_fields(),
            recommended=prop.get("x-recommended", False),
            field_type=prop.get("type"),
            enum=prop.get("enum"),
            format=prop.get("format"),
            minimum=prop.get("minimum"),
            maximum=prop.get("maximum"),
        )

    def get_core_property_names(self) -> set[str]:
        """Get all property names from core schema.

        Returns:
            Set of all defined property names.
        """
        if not self._core_schema:
            return set()

        props = self._core_schema.get("properties", {})
        return set(props.keys())

    def is_loaded(self) -> bool:
        """Check if schemas are loaded.

        Returns:
            True if core schema is loaded.
        """
        return self._core_schema is not None

    def get_category_fields(self, category: str, type_name: str) -> list[str]:
        """Get category-specific field names for a given category/type combination.

        These are fields defined in the type schema that are NOT part of core schema.

        Args:
            category: The category.
            type_name: The type.

        Returns:
            List of field names specific to this category/type.
        """
        schema = self.get_type_schema(category, type_name)
        if not schema:
            return []

        core_fields = self.get_core_property_names()
        category_fields: list[str] = []

        # Extract properties from allOf structure
        self._extract_fields_from_schema(schema, core_fields, category_fields)

        return category_fields

    def _extract_fields_from_schema(
        self,
        schema: dict[str, Any],
        core_fields: set[str],
        result: list[str],
    ) -> None:
        """Extract category-specific fields from a schema, excluding core fields.

        Args:
            schema: Schema definition to extract from.
            core_fields: Set of core field names to exclude.
            result: List to collect field names.
        """
        self._extract_direct_properties(schema, core_fields, result)
        self._extract_from_all_of(schema, core_fields, result)

    def _extract_direct_properties(
        self,
        schema: dict[str, Any],
        core_fields: set[str],
        result: list[str],
    ) -> None:
        """Extract fields from direct schema properties.

        Args:
            schema: Schema definition to extract from.
            core_fields: Set of core field names to exclude.
            result: List to collect field names.
        """
        props = schema.get("properties", {})
        for field_name in props:
            is_excluded = (
                field_name in core_fields
                or field_name == "category"
                or field_name == "type"
            )
            if not is_excluded and field_name not in result:
                result.append(field_name)

    def _extract_from_all_of(
        self,
        schema: dict[str, Any],
        core_fields: set[str],
        result: list[str],
    ) -> None:
        """Extract fields from allOf schema composition.

        Args:
            schema: Schema definition to extract from.
            core_fields: Set of core field names to exclude.
            result: List to collect field names.
        """
        all_of = schema.get("allOf", [])
        for sub_schema in all_of:
            self._process_sub_schema(sub_schema, core_fields, result)

    def _process_sub_schema(
        self,
        sub_schema: dict[str, Any],
        core_fields: set[str],
        result: list[str],
    ) -> None:
        """Process a sub-schema from allOf, handling $ref and inline schemas.

        Args:
            sub_schema: Sub-schema to process.
            core_fields: Set of core field names to exclude.
            result: List to collect field names.
        """
        if "$ref" in sub_schema:
            self._process_schema_reference(sub_schema["$ref"], core_fields, result)
            return
        self._extract_fields_from_schema(sub_schema, core_fields, result)

    def _process_schema_reference(
        self,
        ref: str,
        core_fields: set[str],
        result: list[str],
    ) -> None:
        """Process a schema $ref, loading base schemas if needed.

        Args:
            ref: Schema reference string (e.g., "./content-base.json").
            core_fields: Set of core field names to exclude.
            result: List to collect field names.
        """
        if "-base.json" not in ref:
            return

        base_schema = self._load_base_schema(ref)
        if base_schema:
            self._extract_fields_from_schema(base_schema, core_fields, result)

    def _load_base_schema(self, ref: str) -> dict[str, Any] | None:
        """Load a base schema referenced by $ref.

        Args:
            ref: Schema reference (e.g., "./content-base.json").

        Returns:
            Schema definition or None.
        """
        if self._schemas_dir is None:
            return None

        # Extract filename from ref (remove leading ./ or ../)
        filename = ref
        while filename.startswith("./") or filename.startswith("../"):
            if filename.startswith("../"):
                filename = filename[3:]
            elif filename.startswith("./"):
                filename = filename[2:]
        schema_path = self._schemas_dir / "types" / filename

        try:
            return load_json_schema(schema_path)
        except XARFSchemaError:
            return None

    def get_all_fields_for_category(self, category: str) -> set[str]:
        """Get all category-specific fields across all types for a category.

        Useful for building union type interfaces.

        Args:
            category: The category.

        Returns:
            Set of all field names used by any type in this category.
        """
        all_fields: set[str] = set()
        types = self.get_types_for_category(category)

        for type_name in types:
            fields = self.get_category_fields(category, type_name)
            all_fields.update(fields)

        return all_fields

    def get_optional_fields(self) -> set[str]:
        """Get optional fields from core schema.

        Returns:
            Set of optional field names (properties that are not required).
        """
        all_props = self.get_core_property_names()
        required = self.get_required_fields()
        return all_props - required

    def get_optional_field_info(
        self, category: str | None = None, type_name: str | None = None
    ) -> list[dict[str, Any]]:
        """Get detailed info about optional fields.

        Args:
            category: Optional category to include type-specific fields.
            type_name: Optional type to include type-specific fields.

        Returns:
            List of dicts with field name, description, and recommended flag.
        """
        result: list[dict[str, Any]] = []

        # Core optional fields
        for field_name in self.get_optional_fields():
            metadata = self.get_field_metadata(field_name)
            if metadata:
                result.append(
                    {
                        "field": field_name,
                        "description": metadata.description,
                        "recommended": metadata.recommended,
                        "source": "core",
                    }
                )

        # Type-specific optional fields
        if category and type_name:
            type_schema = self.get_type_schema(category, type_name)
            if type_schema:
                type_required = set(type_schema.get("required", []))
                for sub_schema in type_schema.get("allOf", []):
                    props = sub_schema.get("properties", {})
                    sub_required = set(sub_schema.get("required", []))
                    for field_name, prop in props.items():
                        if (
                            field_name not in type_required
                            and field_name not in sub_required
                        ):
                            if field_name not in self.get_core_property_names():
                                result.append(
                                    {
                                        "field": field_name,
                                        "description": prop.get("description", ""),
                                        "recommended": prop.get("x-recommended", False),
                                        "source": f"{category}/{type_name}",
                                    }
                                )

        return result


# Convenience singleton accessor
def get_schema_registry() -> SchemaRegistry:
    """Get the schema registry singleton instance.

    Returns:
        SchemaRegistry instance.
    """
    return SchemaRegistry.get_instance()


# Module-level singleton for convenience
schema_registry = SchemaRegistry.get_instance()
