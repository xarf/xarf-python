"""Utilities for locating and loading XARF JSON schemas.

This module provides functions to find the schemas directory bundled with
the xarf package and load JSON schema files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .exceptions import XARFSchemaError


def find_schemas_directory() -> Path:
    """Find the schemas directory bundled with the xarf package.

    Searches for the schemas directory in the following locations:
    1. Relative to this file (package installation)
    2. Common development paths

    Returns:
        Path to the schemas directory.

    Raises:
        XARFSchemaError: If schemas directory cannot be found.
    """
    # Start from this file's directory
    current_dir = Path(__file__).parent

    # Possible locations for schemas directory
    search_paths = [
        current_dir / "schemas",  # Package installation
        current_dir.parent / "schemas",  # Development
        Path.cwd() / "xarf" / "schemas",  # CWD-based
    ]

    for path in search_paths:
        if path.is_dir() and (path / "v4" / "xarf-core.json").exists():
            return path

    searched = ", ".join(str(p) for p in search_paths)
    raise XARFSchemaError(f"Could not find schemas directory. Searched: {searched}")


def get_v4_schemas_directory() -> Path:
    """Get the path to the v4 schemas directory.

    Returns:
        Path to the v4 schemas directory.

    Raises:
        XARFSchemaError: If v4 schemas directory cannot be found.
    """
    schemas_dir = find_schemas_directory()
    v4_dir = schemas_dir / "v4"

    if not v4_dir.is_dir():
        raise XARFSchemaError(f"v4 schemas directory not found at {v4_dir}")

    return v4_dir


def get_types_directory() -> Path:
    """Get the path to the type-specific schemas directory.

    Returns:
        Path to the types schemas directory.

    Raises:
        XARFSchemaError: If types directory cannot be found.
    """
    v4_dir = get_v4_schemas_directory()
    types_dir = v4_dir / "types"

    if not types_dir.is_dir():
        raise XARFSchemaError(f"Types schemas directory not found at {types_dir}")

    return types_dir


def load_json_schema(schema_path: Path) -> dict[str, Any]:
    """Load a JSON schema file.

    Args:
        schema_path: Path to the JSON schema file.

    Returns:
        Parsed JSON schema as a dictionary.

    Raises:
        XARFSchemaError: If the schema file cannot be loaded or parsed.
    """
    try:
        with open(schema_path, encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]
    except FileNotFoundError as e:
        raise XARFSchemaError(f"Schema file not found: {schema_path}") from e
    except json.JSONDecodeError as e:
        raise XARFSchemaError(f"Invalid JSON in schema file {schema_path}: {e}") from e


def load_core_schema() -> dict[str, Any]:
    """Load the XARF v4 core schema.

    Returns:
        The core schema as a dictionary.

    Raises:
        XARFSchemaError: If the core schema cannot be loaded.
    """
    v4_dir = get_v4_schemas_directory()
    return load_json_schema(v4_dir / "xarf-core.json")


def load_master_schema() -> dict[str, Any]:
    """Load the XARF v4 master schema.

    Returns:
        The master schema as a dictionary.

    Raises:
        XARFSchemaError: If the master schema cannot be loaded.
    """
    v4_dir = get_v4_schemas_directory()
    return load_json_schema(v4_dir / "xarf-v4-master.json")


def list_type_schemas() -> list[Path]:
    """List all type-specific schema files.

    Returns:
        List of paths to type schema files.

    Raises:
        XARFSchemaError: If types directory cannot be accessed.
    """
    types_dir = get_types_directory()
    return sorted(types_dir.glob("*.json"))


def parse_type_schema_filename(filename: str) -> tuple[str, str]:
    """Parse a type schema filename to extract category and type.

    Type schema files follow the pattern: {category}-{type}.json
    For example: messaging-spam.json -> ("messaging", "spam")

    Args:
        filename: The schema filename (without path).

    Returns:
        Tuple of (category, type).

    Raises:
        XARFSchemaError: If filename doesn't match expected pattern.
    """
    # Remove .json extension
    if not filename.endswith(".json"):
        raise XARFSchemaError(f"Invalid schema filename: {filename}")

    name = filename[:-5]  # Remove .json

    # Split on first hyphen
    parts = name.split("-", 1)
    if len(parts) != 2:
        raise XARFSchemaError(
            f"Invalid type schema filename format: {filename}. "
            "Expected format: category-type.json"
        )

    return parts[0], parts[1]
