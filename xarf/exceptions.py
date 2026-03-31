"""XARF Parser Exceptions."""


class XARFError(Exception):
    """Base exception for XARF parser errors."""


class XARFValidationError(XARFError):
    """Raised when XARF report validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        """Initialise with a message and an optional list of error strings.

        Args:
            message: Human-readable description of the validation failure.
            errors: Individual error strings; defaults to an empty list.
        """
        super().__init__(message)
        self.errors: list[str] = errors or []


class XARFParseError(XARFError):
    """Raised when XARF report parsing fails."""


class XARFSchemaError(XARFError):
    """Raised when XARF schema loading or validation fails."""
