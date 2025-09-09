"""XARF Parser Exceptions."""


class XARFError(Exception):
    """Base exception for XARF parser errors."""
    pass


class XARFValidationError(XARFError):
    """Raised when XARF report validation fails."""
    
    def __init__(self, message: str, errors: list = None):
        super().__init__(message)
        self.errors = errors or []


class XARFParseError(XARFError):
    """Raised when XARF report parsing fails."""
    pass


class XARFSchemaError(XARFError):
    """Raised when XARF schema loading or validation fails."""
    pass