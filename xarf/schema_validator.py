"""Schema Validator — JSON Schema-based validation for XARF v4 reports.

Validates :class:`~xarf.models.XARFReport` instances against the official
XARF JSON Schema (Draft 2020-12) using the ``jsonschema`` library.  Supports
both normal and strict modes; in strict mode, fields marked
``x-recommended: true`` in the schema are promoted to required.

Example:
    >>> from xarf import schema_validator, SpamReport, ContactInfo
    >>> report = SpamReport(
    ...     xarf_version="4.2.0",
    ...     report_id="02eb480f-8172-431a-9276-c28ba90f694a",
    ...     timestamp="2025-01-11T10:59:45Z",
    ...     reporter=ContactInfo(org="Org", contact="a@b.com", domain="b.com"),
    ...     sender=ContactInfo(org="Org", contact="a@b.com", domain="b.com"),
    ...     source_identifier="192.168.1.1",
    ...     category="messaging",
    ...     type="spam",
    ...     protocol="smtp",
    ... )
    >>> errors = schema_validator.validate(report)
    >>> errors
    []
"""

from __future__ import annotations

import copy
import json
from importlib import resources
from pathlib import Path
from typing import Any

import jsonschema
import jsonschema.exceptions
import referencing
import referencing.jsonschema

from xarf.exceptions import XARFSchemaError
from xarf.models import ValidationError, XARFReport
from xarf.schema_registry import schema_registry as _schema_registry

# ---------------------------------------------------------------------------
# Internal type aliases
# ---------------------------------------------------------------------------

_SchemaDict = dict[str, Any]
_ReportInput = XARFReport | dict[str, Any]

# ---------------------------------------------------------------------------
# SchemaValidator
# ---------------------------------------------------------------------------


class SchemaValidator:
    """JSON Schema-based validator for XARF v4 reports.

    Validates :class:`~xarf.models.XARFReport` instances against the official
    XARF JSON Schema using ``jsonschema`` (Draft 2020-12).  Supports both
    normal and strict modes.

    Schema loading is **lazy** — schemas are loaded on the first call to
    :meth:`validate`.  Construction is cheap and always succeeds.
    """

    def __init__(self) -> None:
        """Initialise state variables without loading any schemas."""
        self._schemas_loaded: bool = False
        self._schemas_dir: Path | None = None
        self._normal_validator: jsonschema.Draft202012Validator | None = None
        self._strict_validator: jsonschema.Draft202012Validator | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(
        self, report: _ReportInput, strict: bool = False
    ) -> list[ValidationError]:
        """Validate *report* against the XARF JSON Schema.

        Accepts either a :class:`~xarf.models.XARFReport` instance (converted
        to a dict via :meth:`~pydantic.BaseModel.model_dump` before validation)
        or a plain :class:`dict` (used directly).  The dict path is used by
        :func:`xarf.parser.parse` to validate raw JSON data before Pydantic
        deserialization.

        Args:
            report: A :class:`~xarf.models.XARFReport` (or subclass) instance,
                or a plain dict containing raw report data.
            strict: When ``True``, fields marked ``x-recommended: true`` in
                the schema are treated as required.  Defaults to ``False``.

        Returns:
            A list of :class:`~xarf.models.ValidationError` instances.
            An empty list means the report is valid.

        Raises:
            XARFSchemaError: If the bundled schemas cannot be loaded.
        """
        self._ensure_schemas_loaded()

        if isinstance(report, dict):
            data: dict[str, Any] = report
        else:
            data = report.model_dump(by_alias=True, exclude_none=True)

        validator = self._strict_validator if strict else self._normal_validator
        if validator is None:  # pragma: no cover
            raise XARFSchemaError("Validator not initialised after schema loading.")

        raw_errors = list(validator.iter_errors(data))

        result: list[ValidationError] = []
        seen: set[tuple[str, str]] = set()
        for err in raw_errors:
            ve = self._format_validation_error(err)
            key = (ve.field, ve.message)
            if key not in seen:
                seen.add(key)
                result.append(ve)

        return result

    def get_supported_types(self) -> list[str]:
        """Return all supported ``"category/type"`` strings.

        Uses the :data:`~xarf.schema_registry.schema_registry` singleton to
        enumerate all known category/type pairs.

        Returns:
            A list of strings in ``"category/type"`` format.
        """
        result: list[str] = []
        for category, types in _schema_registry.get_all_types().items():
            for type_ in sorted(types):
                result.append(f"{category}/{type_}")
        return result

    def has_type_schema(self, category: str, type_: str) -> bool:
        """Return whether a schema exists for the given *category*/*type_* pair.

        Args:
            category: XARF category name (e.g. ``"messaging"``).
            type_: XARF type name within the category (e.g. ``"spam"``).

        Returns:
            ``True`` if the combination is known; ``False`` otherwise.
        """
        return _schema_registry.is_valid_type(category, type_)

    # ------------------------------------------------------------------
    # Lazy loading
    # ------------------------------------------------------------------

    def _ensure_schemas_loaded(self) -> None:
        """Load all schemas on first call; do nothing on subsequent calls.

        Raises:
            XARFSchemaError: If schemas cannot be located or parsed.
        """
        if self._schemas_loaded:
            return
        self._schemas_dir = self._find_schemas_dir()
        all_schemas = self._load_all_schemas()
        master_schema = self._find_master_schema(all_schemas)

        normal_registry = self._build_registry(all_schemas, strict=False)
        strict_registry = self._build_registry(all_schemas, strict=True)

        strict_master = self._transform_for_strict(master_schema)

        self._normal_validator = jsonschema.Draft202012Validator(
            master_schema,
            registry=normal_registry,
            format_checker=jsonschema.FormatChecker(),
        )
        self._strict_validator = jsonschema.Draft202012Validator(
            strict_master,
            registry=strict_registry,
            format_checker=jsonschema.FormatChecker(),
        )
        self._schemas_loaded = True

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

    def _load_all_schemas(self) -> list[_SchemaDict]:
        """Load core, master, and all type schemas from the bundled directory.

        Returns:
            List of parsed schema dicts.

        Raises:
            XARFSchemaError: If any schema file cannot be read or parsed.
        """
        if self._schemas_dir is None:  # pragma: no cover
            raise XARFSchemaError("Schemas directory not set.")
        schemas_dir = self._schemas_dir
        schemas: list[_SchemaDict] = []

        for name in ("xarf-core.json", "xarf-v4-master.json"):
            path = schemas_dir / name
            schema = self._load_json_file(path)
            if schema is None:
                raise XARFSchemaError(
                    f"Failed to load schema '{name}' from {path}. "
                    "The bundled schemas may be missing or corrupted."
                )
            schemas.append(schema)

        types_dir = schemas_dir / "types"
        if types_dir.is_dir():
            for json_file in sorted(types_dir.glob("*.json")):
                schema = self._load_json_file(json_file)
                if schema is None:
                    raise XARFSchemaError(
                        f"Failed to load type schema from {json_file}. "
                        "The bundled schemas may be missing or corrupted."
                    )
                schemas.append(schema)

        return schemas

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

    def _find_master_schema(self, schemas: list[_SchemaDict]) -> _SchemaDict:
        """Find the master schema (``xarf-v4-master.json``) among *schemas*.

        Args:
            schemas: List of loaded schema dicts.

        Returns:
            The master schema dict.

        Raises:
            XARFSchemaError: If the master schema is not found.
        """
        master_id = "https://xarf.org/schemas/v4/xarf-v4-master.json"
        for schema in schemas:
            if schema.get("$id") == master_id:
                return schema
        raise XARFSchemaError(
            f"Master schema with $id '{master_id}' not found among loaded schemas."
        )

    # ------------------------------------------------------------------
    # Registry building
    # ------------------------------------------------------------------

    def _build_registry(
        self, schemas: list[_SchemaDict], strict: bool
    ) -> referencing.Registry[Any]:
        """Build a :class:`referencing.Registry` for ``$ref`` resolution.

        Args:
            schemas: All loaded schema dicts.
            strict: When ``True``, each schema is transformed via
                :meth:`_transform_for_strict` before registration.

        Returns:
            A populated :class:`referencing.Registry`.
        """
        resource_pairs: list[tuple[str, referencing.Resource[Any]]] = []
        for raw_schema in schemas:
            schema = self._transform_for_strict(raw_schema) if strict else raw_schema
            schema_id = schema.get("$id")
            if schema_id:
                resource = referencing.jsonschema.DRAFT202012.create_resource(schema)
                resource_pairs.append((schema_id, resource))

        registry: referencing.Registry[Any] = referencing.Registry()
        registry = registry.with_resources(resource_pairs)
        return registry

    # ------------------------------------------------------------------
    # Strict mode transformation
    # ------------------------------------------------------------------

    def _transform_for_strict(self, schema: _SchemaDict) -> _SchemaDict:
        """Return a deep copy of *schema* with recommended fields promoted.

        Calls :meth:`_promote_recommended_to_required` on the clone.

        Args:
            schema: Original schema dict (not mutated).

        Returns:
            A new schema dict where ``x-recommended: true`` properties have
            been added to their parent ``required`` arrays.
        """
        clone: _SchemaDict = copy.deepcopy(schema)
        self._promote_recommended_to_required(clone)
        return clone

    def _promote_recommended_to_required(self, node: Any) -> None:
        """Recursively promote ``x-recommended`` properties to ``required``.

        Walks all relevant schema nodes and, for any ``properties`` dict
        where a property has ``x-recommended: true``, ensures that property
        name appears in the parent node's ``required`` array.

        Recurses into: ``properties``, ``$defs``, ``allOf``, ``anyOf``,
        ``oneOf``, ``items``, ``if``, ``then``, ``else``, ``not``,
        ``additionalProperties``.

        Args:
            node: A schema node (dict) to process in place.  Non-dict values
                are ignored.
        """
        if not isinstance(node, dict):
            return

        # Promote x-recommended properties to required on this node
        props = node.get("properties")
        if isinstance(props, dict):
            recommended = [
                k
                for k, v in props.items()
                if isinstance(v, dict) and v.get("x-recommended") is True
            ]
            if recommended:
                existing: list[str] = list(node.get("required", []))
                for field in recommended:
                    if field not in existing:
                        existing.append(field)
                node["required"] = existing

        # Recurse into dict-valued keywords
        for key in ("properties", "$defs"):
            sub = node.get(key)
            if isinstance(sub, dict):
                for value in sub.values():
                    self._promote_recommended_to_required(value)

        # Recurse into list-valued keywords
        for key in ("allOf", "anyOf", "oneOf"):
            sub = node.get(key)
            if isinstance(sub, list):
                for item in sub:
                    self._promote_recommended_to_required(item)

        # Recurse into single-schema keywords
        for key in ("items", "if", "then", "else", "not", "additionalProperties"):
            sub = node.get(key)
            if isinstance(sub, dict):
                self._promote_recommended_to_required(sub)

    # ------------------------------------------------------------------
    # Error formatting
    # ------------------------------------------------------------------

    def _format_validation_error(
        self,
        err: jsonschema.exceptions.ValidationError,
    ) -> ValidationError:
        """Map a ``jsonschema`` error to a :class:`~xarf.models.ValidationError`.

        Args:
            err: Raw :class:`jsonschema.exceptions.ValidationError` instance.

        Returns:
            A :class:`~xarf.models.ValidationError` with:

            - ``field``: dot-joined absolute path, or ``""`` for root errors.
            - ``message``: the raw ``err.message`` string.
            - ``value``: the offending ``err.instance`` value.
        """
        path_parts = list(err.absolute_path)
        field = ".".join(str(p) for p in path_parts)
        return ValidationError(
            field=field,
            message=err.message,
            value=err.instance,
        )


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

#: Module-level singleton — lazily loads schemas on first :meth:`validate` call.
schema_validator: SchemaValidator = SchemaValidator()
