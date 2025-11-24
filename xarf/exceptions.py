"""XARF Parser Exceptions."""

from typing import List, Optional


class XARFError(Exception):
    """Base exception for XARF parser errors."""


class XARFValidationError(XARFError):
    """Raised when XARF report validation fails."""

    def __init__(self, message: str, errors: Optional[List[str]] = None):
        super().__init__(message)
        self.errors = errors or []


class XARFParseError(XARFError):
    """Raised when XARF report parsing fails."""


class XARFSchemaError(XARFError):
    """Raised when XARF schema loading or validation fails."""
