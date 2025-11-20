"""XARF v4 Python Parser.

A Python library for parsing and validating XARF v4 (eXtended Abuse Reporting Format) reports.
"""

__version__ = "4.0.0a1"
__author__ = "XARF Project"
__email__ = "contact@xarf.org"

from .exceptions import XARFError, XARFParseError, XARFValidationError
from .generator import XARFGenerator
from .models import XARFReport
from .parser import XARFParser

__all__ = [
    "XARFParser",
    "XARFReport",
    "XARFError",
    "XARFValidationError",
    "XARFParseError",
    "XARFGenerator",
]
