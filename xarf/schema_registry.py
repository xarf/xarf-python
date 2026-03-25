"""Schema Registry — schema-driven source of truth for categories, types, and metadata.

Python port of ``schema-registry.ts`` from the JavaScript reference implementation.

Provides centralized, schema-derived access to valid categories, types, required fields,
and field metadata without any hardcoded enums or lists.

Example:
    >>> from xarf import schema_registry
    >>> schema_registry.get_categories()
    {'messaging', 'connection', 'content', ...}
    >>> schema_registry.get_types_for_category("connection")
    {'ddos', 'login_attack', ...}
    >>> schema_registry.is_valid_type("messaging", "spam")
    True
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

from xarf.exceptions import XARFSchemaError

# ---------------------------------------------------------------------------
# FieldMetadata
# ---------------------------------------------------------------------------


@dataclass
class FieldMetadata:
    """Metadata extracted from a JSON schema property definition.

    Attributes:
        description: Human-readable field description from the schema.
        required: Whether the field is in the core schema ``required`` array.
        recommended: Whether the field carries ``x-recommended: true``.
        type: JSON Schema ``type`` value (e.g. ``"string"``, ``"integer"``).
        enum: Allowed values if the field has an ``enum`` constraint.
        format: JSON Schema ``format`` value (e.g. ``"email"``, ``"uuid"``).
        minimum: Numeric minimum constraint, if present.
        maximum: Numeric maximum constraint, if present.
    """

    description: str
    required: bool
    recommended: bool
    type: str | None = None
    enum: list[Any] | None = None
    format: str | None = None
    minimum: float | None = None
    maximum: float | None = None


# ---------------------------------------------------------------------------
# Internal type aliases
# ---------------------------------------------------------------------------

_SchemaDict = dict[str, Any]

# ---------------------------------------------------------------------------
# SchemaRegistry
# ---------------------------------------------------------------------------


class SchemaRegistry:
    """Singleton registry that loads XARF JSON schemas and exposes validation rules.

    All public methods are cached after first access.  The registry is initialised
    lazily by :func:`get_registry` and exposed as the module-level
    :data:`schema_registry` singleton.

    Raises:
        XARFSchemaError: On construction, if the bundled schemas cannot be located
            or the core schema cannot be parsed.
    """

    def __init__(self) -> None:
        """Load bundled schemas and build internal caches."""
        self._schemas_dir: Path = self._find_schemas_dir()
        self._core_schema: _SchemaDict = self._load_core_schema()
        self._type_schemas: dict[str, _SchemaDict] = {}
        self._scan_type_schemas()

        # Lazy-init caches
        self._categories_cache: set[str] | None = None
        self._types_per_category_cache: dict[str, set[str]] | None = None
        self._required_fields_cache: set[str] | None = None
        self._contact_required_fields_cache: set[str] | None = None

    # ------------------------------------------------------------------
    # Schema loading helpers
    # ------------------------------------------------------------------

    def _find_schemas_dir(self) -> Path:
        """Locate the bundled ``schemas/`` directory inside the package.

        Returns:
            Absolute path to the schemas directory.

        Raises:
            XARFSchemaError: If the directory cannot be found.
        """
        try:
            pkg = resources.files("xarf")
            schemas_path = Path(str(pkg)) / "schemas"
            if not schemas_path.is_dir():
                raise XARFSchemaError(
                    f"Bundled schemas directory not found at {schemas_path}. "
                    "Run 'python scripts/fetch_schemas.py' to download schemas."
                )
            return schemas_path
        except (TypeError, FileNotFoundError) as exc:
            raise XARFSchemaError(
                "Could not locate the xarf package directory while searching "
                "for bundled schemas."
            ) from exc

    def _load_json_file(self, path: Path) -> _SchemaDict | None:
        """Load and parse a single JSON file.

        Args:
            path: Absolute path to the JSON file.

        Returns:
            Parsed dict, or ``None`` if the file cannot be read or parsed.
        """
        try:
            with path.open(encoding="utf-8") as fh:
                return json.load(fh)  # type: ignore[no-any-return]
        except (OSError, json.JSONDecodeError):
            return None

    def _load_core_schema(self) -> _SchemaDict:
        """Load ``xarf-core.json``.

        Returns:
            Parsed core schema dict.

        Raises:
            XARFSchemaError: If the file is missing or cannot be parsed.
        """
        core_path = self._schemas_dir / "xarf-core.json"
        schema = self._load_json_file(core_path)
        if schema is None:
            raise XARFSchemaError(
                f"Failed to load core schema from {core_path}. "
                "The bundled schemas may be corrupted."
            )
        return schema

    def _scan_type_schemas(self) -> None:
        """Scan ``schemas/types/`` and populate :attr:`_type_schemas`.

        Filenames follow the pattern ``{category}-{type}.json``.  The type
        portion may contain hyphens (e.g. ``login-attack``), which are
        normalised to underscores for the registry key (``login_attack``),
        matching the Python model naming convention.

        ``content-base.json`` is a shared base schema and is skipped.
        """
        types_dir = self._schemas_dir / "types"
        if not types_dir.is_dir():
            return

        for json_file in sorted(types_dir.glob("*.json")):
            stem = json_file.stem
            if stem == "content-base":
                continue
            # Split on first hyphen only to get category; rest is type
            parts = stem.split("-", 1)
            if len(parts) != 2:
                continue
            category, raw_type = parts
            normalised_type = raw_type.replace("-", "_")
            schema = self._load_json_file(json_file)
            if schema is not None:
                self._type_schemas[f"{category}/{normalised_type}"] = schema

    # ------------------------------------------------------------------
    # Category / type enumeration
    # ------------------------------------------------------------------

    def get_categories(self) -> set[str]:
        """Return all valid categories derived from the core schema enum.

        Returns:
            Set of category name strings (e.g. ``{'messaging', 'connection', ...}``).
        """
        if self._categories_cache is not None:
            return self._categories_cache

        categories: set[str] = set()
        props = self._core_schema.get("properties", {})
        cat_enum = props.get("category", {}).get("enum", [])
        for cat in cat_enum:
            categories.add(str(cat))

        self._categories_cache = categories
        return categories

    def get_types_for_category(self, category: str) -> set[str]:
        """Return valid type names for a given category.

        Args:
            category: Category name (e.g. ``"connection"``).

        Returns:
            Set of type name strings for the category, or an empty set if the
            category is unknown.
        """
        return self.get_all_types().get(category, set())

    def get_all_types(self) -> dict[str, set[str]]:
        """Return all types organised by category.

        Returns:
            Mapping of category name → set of type names.
        """
        if self._types_per_category_cache is not None:
            return self._types_per_category_cache

        cache: dict[str, set[str]] = {}
        for key in self._type_schemas:
            category, type_ = key.split("/", 1)
            cache.setdefault(category, set()).add(type_)

        self._types_per_category_cache = cache
        return cache

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def is_valid_category(self, category: str) -> bool:
        """Check whether *category* is a known XARF category.

        Args:
            category: Category name to check.

        Returns:
            ``True`` if the category appears in the core schema enum.
        """
        return category in self.get_categories()

    def is_valid_type(self, category: str, type_: str) -> bool:
        """Check whether *type_* is valid for *category*.

        Args:
            category: Category name.
            type_: Type name to check.

        Returns:
            ``True`` if the ``category/type_`` combination exists in the
            scanned type schemas.
        """
        return type_ in self.get_types_for_category(category)

    # ------------------------------------------------------------------
    # Required / contact fields
    # ------------------------------------------------------------------

    def get_required_fields(self) -> set[str]:
        """Return the set of fields listed as required in the core schema.

        Returns:
            Set of required field name strings.
        """
        if self._required_fields_cache is not None:
            return self._required_fields_cache

        self._required_fields_cache = set(self._core_schema.get("required", []))
        return self._required_fields_cache

    def get_contact_required_fields(self) -> set[str]:
        """Return the required fields for the ``contact_info`` sub-object.

        Falls back to ``{"org", "contact", "domain"}`` if the schema does not
        define them explicitly (matching the JS fallback).

        Returns:
            Set of required contact field name strings.
        """
        if self._contact_required_fields_cache is not None:
            return self._contact_required_fields_cache

        defs = self._core_schema.get("$defs", {})
        contact_def = defs.get("contact_info", {})
        required = contact_def.get("required", ["org", "contact", "domain"])
        self._contact_required_fields_cache = set(required)
        return self._contact_required_fields_cache

    # ------------------------------------------------------------------
    # Schema / field access
    # ------------------------------------------------------------------

    def get_type_schema(self, category: str, type_: str) -> dict[str, Any] | None:
        """Return the raw schema dict for a specific ``category/type_`` pair.

        Args:
            category: Category name.
            type_: Type name.

        Returns:
            Schema dict, or ``None`` if the combination is unknown.
        """
        return self._type_schemas.get(f"{category}/{type_}")

    def get_field_metadata(self, field_name: str) -> FieldMetadata | None:
        """Return metadata for a field defined in the core schema.

        Args:
            field_name: Name of the field to look up.

        Returns:
            :class:`FieldMetadata` instance, or ``None`` if the field is not
            in the core schema properties.
        """
        props = self._core_schema.get("properties", {})
        prop = props.get(field_name)
        if prop is None:
            return None

        return FieldMetadata(
            description=prop.get("description", ""),
            required=field_name in self.get_required_fields(),
            recommended=prop.get("x-recommended") is True,
            type=prop.get("type"),
            enum=prop.get("enum"),
            format=prop.get("format"),
            minimum=prop.get("minimum"),
            maximum=prop.get("maximum"),
        )

    def get_core_property_names(self) -> set[str]:
        """Return all property names defined in the core schema.

        Returns:
            Set of property name strings.
        """
        return set(self._core_schema.get("properties", {}).keys())

    def get_category_fields(self, category: str, type_: str) -> list[str]:
        """Return type-specific field names for a ``category/type_`` pair.

        These are fields defined in the type schema that are *not* part of the
        core schema (i.e. the category-specific additions).  Ordering is
        preserved, matching the JS array return.

        Args:
            category: Category name.
            type_: Type name.

        Returns:
            Ordered list of category-specific field names, or an empty list if
            the ``category/type_`` combination is unknown.
        """
        schema = self.get_type_schema(category, type_)
        if schema is None:
            return []

        core_fields = self.get_core_property_names()
        result: list[str] = []
        self._extract_fields_from_schema(schema, core_fields, result)
        return result

    def get_all_fields_for_category(self, category: str) -> set[str]:
        """Return the union of all type-specific fields across a category.

        Useful for building exhaustive field sets per category (e.g. for
        unknown-field detection in the parser).

        Args:
            category: Category name.

        Returns:
            Set of all field names used by any type in the category.
        """
        all_fields: set[str] = set()
        for type_ in self.get_types_for_category(category):
            all_fields.update(self.get_category_fields(category, type_))
        return all_fields

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def is_loaded(self) -> bool:
        """Return whether the core schema was successfully loaded.

        Returns:
            ``True`` if the core schema is present in memory.
        """
        return bool(self._core_schema)

    # ------------------------------------------------------------------
    # Private schema traversal helpers (mirrors JS private methods)
    # ------------------------------------------------------------------

    def _extract_fields_from_schema(
        self,
        schema: _SchemaDict,
        core_fields: set[str],
        result: list[str],
    ) -> None:
        """Recursively collect category-specific fields from *schema*.

        Args:
            schema: Schema dict to inspect.
            core_fields: Set of core field names to exclude.
            result: Accumulator list; mutated in place.
        """
        self._extract_direct_properties(schema, core_fields, result)
        self._extract_from_all_of(schema, core_fields, result)

    def _extract_direct_properties(
        self,
        schema: _SchemaDict,
        core_fields: set[str],
        result: list[str],
    ) -> None:
        """Collect fields from the ``properties`` key of *schema*.

        Args:
            schema: Schema dict to inspect.
            core_fields: Set of core field names to exclude.
            result: Accumulator list; mutated in place.
        """
        for field_name in schema.get("properties", {}):
            if field_name in core_fields:
                continue
            if field_name in ("category", "type"):
                continue
            if field_name not in result:
                result.append(field_name)

    def _extract_from_all_of(
        self,
        schema: _SchemaDict,
        core_fields: set[str],
        result: list[str],
    ) -> None:
        """Collect fields from each entry in ``allOf``.

        Args:
            schema: Schema dict that may contain an ``allOf`` array.
            core_fields: Set of core field names to exclude.
            result: Accumulator list; mutated in place.
        """
        for sub_schema in schema.get("allOf", []):
            self._process_sub_schema(sub_schema, core_fields, result)

    def _process_sub_schema(
        self,
        sub_schema: _SchemaDict,
        core_fields: set[str],
        result: list[str],
    ) -> None:
        """Dispatch a sub-schema to the appropriate extraction path.

        If the sub-schema is a ``$ref``, delegate to
        :meth:`_process_schema_reference`; otherwise recurse into it directly.

        Args:
            sub_schema: Individual entry from an ``allOf`` array.
            core_fields: Set of core field names to exclude.
            result: Accumulator list; mutated in place.
        """
        ref = sub_schema.get("$ref")
        if ref:
            self._process_schema_reference(ref, core_fields, result)
        else:
            self._extract_fields_from_schema(sub_schema, core_fields, result)

    def _process_schema_reference(
        self,
        ref: str,
        core_fields: set[str],
        result: list[str],
    ) -> None:
        """Follow a ``$ref`` only when it points to a ``-base.json`` schema.

        Mirrors the JS behaviour: references to the core schema
        (``../xarf-core.json``) are intentionally ignored here because core
        fields are already captured in *core_fields*.  Only base schemas such
        as ``./content-base.json`` are resolved.

        Args:
            ref: The ``$ref`` value from the schema.
            core_fields: Set of core field names to exclude.
            result: Accumulator list; mutated in place.
        """
        if "-base.json" not in ref:
            return
        base_schema = self._load_base_schema(ref)
        if base_schema is not None:
            self._extract_fields_from_schema(base_schema, core_fields, result)

    def _load_base_schema(self, ref: str) -> _SchemaDict | None:
        """Load a base schema file referenced by ``$ref``.

        Args:
            ref: The ``$ref`` value (e.g. ``"./content-base.json"``).

        Returns:
            Parsed schema dict, or ``None`` if the file cannot be loaded.
        """
        # Strip leading ./ or ../ path prefix to get a bare filename.
        filename = ref.removeprefix("./").removeprefix("../")
        schema_path = self._schemas_dir / "types" / filename
        return self._load_json_file(schema_path)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_registry: SchemaRegistry | None = None


def get_registry() -> SchemaRegistry:
    """Return the module-level :class:`SchemaRegistry` singleton.

    Creates it on first call.

    Returns:
        The shared :class:`SchemaRegistry` instance.

    Raises:
        XARFSchemaError: If schema initialisation fails.
    """
    global _registry  # noqa: PLW0603
    if _registry is None:
        _registry = SchemaRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the module-level singleton.

    The next call to :func:`get_registry` (or any access via the
    :data:`schema_registry` convenience alias) will re-initialise the registry
    from scratch.

    Warning:
        This function is intended **exclusively for test isolation**.  Do not
        call it in production code.
    """
    global _registry  # noqa: PLW0603
    _registry = None


#: Convenience singleton — equivalent to ``get_registry()``.
#: Import this directly: ``from xarf import schema_registry``.
schema_registry: SchemaRegistry = get_registry()
