"""XARF v4 Python Parser.

A Python library for parsing and validating XARF v4
(eXtended Abuse Reporting Format) reports.
Includes backwards compatibility with XARF v3.
"""

__version__ = "4.0.0a1"
__author__ = "XARF Project"
__email__ = "contact@xarf.org"

from .exceptions import XARFError, XARFParseError, XARFValidationError
from .generator import XARFGenerator
from .models import XARFReport
from .parser import XARFParser
from .v3_compat import convert_v3_to_v4, is_v3_report

__all__ = [
    "XARFParser",
    "XARFReport",
    "XARFError",
    "XARFValidationError",
    "XARFParseError",
    "XARFGenerator",
    "convert_v3_to_v4",
    "is_v3_report",
]
