"""XARF spec version constant.

Centralised so ``generator.py`` and ``__init__.py`` both import from
one place and cannot silently diverge.
"""

#: The XARF specification version this library targets.
SPEC_VERSION: str = "4.2.0"
