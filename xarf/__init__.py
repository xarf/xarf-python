"""XARF v4 Python Parser.

A Python library for parsing and validating XARF v4
(eXtended Abuse Reporting Format) reports.
Includes backwards compatibility with XARF v3.
"""

__version__ = "4.0.0a1"
__author__ = "XARF Project"
__email__ = "contact@xarf.org"

from .exceptions import XARFError, XARFParseError, XARFSchemaError, XARFValidationError
from .generator import XARFGenerator
from .models import XARFReport
from .parser import XARFParser
from .schema_registry import FieldMetadata, SchemaRegistry, schema_registry
from .schema_validator import (
    SchemaValidationError,
    SchemaValidationResult,
    SchemaValidator,
    validate_report,
    validate_report_strict,
)
from .v3_compat import convert_v3_to_v4, is_v3_report

__all__ = [
    # Parser
    "XARFParser",
    # Models
    "XARFReport",
    # Generator
    "XARFGenerator",
    # Schema Registry
    "SchemaRegistry",
    "schema_registry",
    "FieldMetadata",
    # Schema Validator
    "SchemaValidator",
    "SchemaValidationResult",
    "SchemaValidationError",
    "validate_report",
    "validate_report_strict",
    # Exceptions
    "XARFError",
    "XARFValidationError",
    "XARFParseError",
    "XARFSchemaError",
    # v3 Compatibility
    "convert_v3_to_v4",
    "is_v3_report",
]
