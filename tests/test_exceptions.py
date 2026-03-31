"""Tests for the XARF exception hierarchy.

Port of the JavaScript ``errors.test.ts`` test suite.

Covers:

- :class:`~xarf.exceptions.XARFError` base behaviour.
- :class:`~xarf.exceptions.XARFValidationError` ``.errors`` attribute.
- :class:`~xarf.exceptions.XARFParseError` instantiation and hierarchy.
- :class:`~xarf.exceptions.XARFSchemaError` instantiation and hierarchy.
- Cross-class inheritance assertions.
"""

from __future__ import annotations

import pytest

from xarf.exceptions import (
    XARFError,
    XARFParseError,
    XARFSchemaError,
    XARFValidationError,
)

# ---------------------------------------------------------------------------
# TestXARFError
# ---------------------------------------------------------------------------


class TestXARFError:
    """Tests for the :class:`~xarf.exceptions.XARFError` base exception."""

    def test_can_be_instantiated_with_message(self) -> None:
        """XARFError can be constructed with a plain string message."""
        error = XARFError("base error message")
        assert error is not None

    def test_str_contains_message(self) -> None:
        """``str(error)`` must include the message passed to the constructor."""
        error = XARFError("base error message")
        assert "base error message" in str(error)

    def test_is_subclass_of_exception(self) -> None:
        """XARFError must be a subclass of the built-in :class:`Exception`."""
        assert issubclass(XARFError, Exception)

    def test_can_be_raised_and_caught_as_exception(self) -> None:
        """XARFError raised in user code must be catchable as :class:`Exception`."""
        with pytest.raises(XARFError):
            raise XARFError("raised as exception")

    def test_can_be_caught_as_xarf_error(self) -> None:
        """XARFError raised in user code must be catchable as :class:`XARFError`."""
        with pytest.raises(XARFError):
            raise XARFError("caught as xarf error")


# ---------------------------------------------------------------------------
# TestXARFValidationError
# ---------------------------------------------------------------------------


class TestXARFValidationError:
    """Tests for :class:`~xarf.exceptions.XARFValidationError`."""

    def test_is_subclass_of_xarf_error(self) -> None:
        """XARFValidationError must be a subclass of :class:`XARFError`."""
        assert issubclass(XARFValidationError, XARFError)

    def test_is_subclass_of_exception(self) -> None:
        """XARFValidationError must be a subclass of the built-in :class:`Exception`."""
        assert issubclass(XARFValidationError, Exception)

    def test_errors_defaults_to_empty_list(self) -> None:
        """When no ``errors`` argument is supplied, ``.errors`` must be an empty
        list."""
        error = XARFValidationError("validation failed")
        assert error.errors == []

    def test_errors_stores_provided_list(self) -> None:
        """Errors passed to the constructor must be accessible via ``.errors``."""
        msgs = ["field1 is required", "field2 is invalid"]
        error = XARFValidationError("validation failed", errors=msgs)
        assert error.errors == msgs

    def test_message_is_accessible_via_str(self) -> None:
        """``str(error)`` must contain the message passed to the constructor."""
        error = XARFValidationError("validation failed message")
        assert "validation failed message" in str(error)

    def test_can_be_caught_as_xarf_error(self) -> None:
        """XARFValidationError raised in user code must be catchable as
        :class:`XARFError`."""
        with pytest.raises(XARFError):
            raise XARFValidationError("caught as xarf error")


# ---------------------------------------------------------------------------
# TestXARFParseError
# ---------------------------------------------------------------------------


class TestXARFParseError:
    """Tests for :class:`~xarf.exceptions.XARFParseError`."""

    def test_is_subclass_of_xarf_error(self) -> None:
        """XARFParseError must be a subclass of :class:`XARFError`."""
        assert issubclass(XARFParseError, XARFError)

    def test_is_subclass_of_exception(self) -> None:
        """XARFParseError must be a subclass of the built-in :class:`Exception`."""
        assert issubclass(XARFParseError, Exception)

    def test_can_be_raised_with_message(self) -> None:
        """XARFParseError can be raised and contains the supplied message."""
        with pytest.raises(XARFParseError) as exc_info:
            raise XARFParseError("parse failed")
        assert "parse failed" in str(exc_info.value)

    def test_can_be_caught_as_xarf_error(self) -> None:
        """XARFParseError raised in user code must be catchable as
        :class:`XARFError`."""
        with pytest.raises(XARFError):
            raise XARFParseError("caught as xarf error")


# ---------------------------------------------------------------------------
# TestXARFSchemaError
# ---------------------------------------------------------------------------


class TestXARFSchemaError:
    """Tests for :class:`~xarf.exceptions.XARFSchemaError`."""

    def test_is_subclass_of_xarf_error(self) -> None:
        """XARFSchemaError must be a subclass of :class:`XARFError`."""
        assert issubclass(XARFSchemaError, XARFError)

    def test_is_subclass_of_exception(self) -> None:
        """XARFSchemaError must be a subclass of the built-in :class:`Exception`."""
        assert issubclass(XARFSchemaError, Exception)

    def test_can_be_raised_with_message(self) -> None:
        """XARFSchemaError can be raised and contains the supplied message."""
        with pytest.raises(XARFSchemaError) as exc_info:
            raise XARFSchemaError("schema load failed")
        assert "schema load failed" in str(exc_info.value)

    def test_can_be_caught_as_xarf_error(self) -> None:
        """XARFSchemaError raised in user code must be catchable as
        :class:`XARFError`."""
        with pytest.raises(XARFError):
            raise XARFSchemaError("caught as xarf error")


# ---------------------------------------------------------------------------
# TestErrorInheritance
# ---------------------------------------------------------------------------


class TestErrorInheritance:
    """Cross-class inheritance assertions for the entire exception hierarchy."""

    def test_all_four_are_instances_of_exception(self) -> None:
        """Instances of all four exception classes must satisfy
        ``isinstance(e, Exception)``."""
        exceptions = [
            XARFError("base"),
            XARFValidationError("validation"),
            XARFParseError("parse"),
            XARFSchemaError("schema"),
        ]
        for exc in exceptions:
            assert isinstance(exc, Exception), (
                f"{type(exc).__name__} is not an Exception"
            )

    def test_subclasses_are_instances_of_xarf_error(self) -> None:
        """XARFValidationError, XARFParseError, and XARFSchemaError must all be
        XARFError instances."""
        subclasses = [
            XARFValidationError("validation"),
            XARFParseError("parse"),
            XARFSchemaError("schema"),
        ]
        for exc in subclasses:
            assert isinstance(exc, XARFError), (
                f"{type(exc).__name__} is not an instance of XARFError"
            )

    def test_issubclass_checks_work(self) -> None:
        """``issubclass`` checks must hold for the full hierarchy."""
        assert issubclass(XARFValidationError, XARFError)
        assert issubclass(XARFParseError, XARFError)
        assert issubclass(XARFSchemaError, XARFError)
        assert issubclass(XARFError, Exception)
        assert issubclass(XARFValidationError, Exception)
        assert issubclass(XARFParseError, Exception)
        assert issubclass(XARFSchemaError, Exception)


# ---------------------------------------------------------------------------
# TestXARFValidationErrorErrors
# ---------------------------------------------------------------------------


class TestXARFValidationErrorErrors:
    """Detailed tests for the ``errors`` attribute of
    :class:`~xarf.exceptions.XARFValidationError`."""

    def test_default_errors_is_empty_list(self) -> None:
        """``XARFValidationError("msg").errors`` must be ``[]``."""
        error = XARFValidationError("msg")
        assert error.errors == []

    def test_default_errors_is_a_list(self) -> None:
        """``XARFValidationError("msg").errors`` must be an instance of
        :class:`list`."""
        error = XARFValidationError("msg")
        assert isinstance(error.errors, list)

    def test_providing_errors_list_stores_it(self) -> None:
        """Errors supplied to the constructor are accessible via ``.errors``."""
        errors = ["first error", "second error"]
        error = XARFValidationError("msg", errors=errors)
        assert error.errors == errors

    def test_multiple_error_messages_stored_correctly(self) -> None:
        """All supplied error message strings are stored and retrievable."""
        messages = [
            "missing field: xarf_version",
            "invalid uuid: report_id",
            "bad timestamp",
        ]
        error = XARFValidationError("multiple errors", errors=messages)
        assert len(error.errors) == 3
        for msg in messages:
            assert msg in error.errors

    def test_empty_list_provided_yields_empty_errors(self) -> None:
        """Explicitly providing an empty list keeps ``.errors`` as ``[]``."""
        error = XARFValidationError("msg", errors=[])
        assert error.errors == []
