"""Tests for custom exception hierarchy."""

import pytest

from autosar_calltree.exceptions import (
    AutosarCalltreeError,
    ConfigError,
    DatabaseError,
    ParseError,
    PreprocessError,
)


class TestAutosarCalltreeError:
    """Tests for base exception class."""

    def test_is_exception_subclass(self):
        """Should be subclass of Exception."""
        assert issubclass(AutosarCalltreeError, Exception)

    def test_can_be_raised(self):
        """Should be raisable with message."""
        with pytest.raises(AutosarCalltreeError, match="test error"):
            raise AutosarCalltreeError("test error")


class TestParseError:
    """Tests for ParseError exception."""

    def test_inherits_from_base(self):
        """Should inherit from AutosarCalltreeError."""
        assert issubclass(ParseError, AutosarCalltreeError)

    def test_message_only(self):
        """Should work with message only."""
        error = ParseError("parsing failed")
        assert str(error) == "parsing failed"
        assert error.file_path is None
        assert error.line_number is None

    def test_with_file_path(self):
        """Should store file path."""
        error = ParseError("parsing failed", file_path="test.c")
        assert error.file_path == "test.c"
        assert error.line_number is None

    def test_with_file_and_line(self):
        """Should store file path and line number."""
        error = ParseError("parsing failed", file_path="test.c", line_number=42)
        assert error.file_path == "test.c"
        assert error.line_number == 42


class TestPreprocessError:
    """Tests for PreprocessError exception."""

    def test_inherits_from_base(self):
        """Should inherit from AutosarCalltreeError."""
        assert issubclass(PreprocessError, AutosarCalltreeError)

    def test_message_only(self):
        """Should work with message only."""
        error = PreprocessError("preprocessing failed")
        assert str(error) == "preprocessing failed"
        assert error.file_path is None
        assert error.error_type is None

    def test_with_file_path(self):
        """Should store file path."""
        error = PreprocessError("preprocessing failed", file_path="test.c")
        assert error.file_path == "test.c"

    def test_with_error_type(self):
        """Should store error type."""
        error = PreprocessError("cpp not found", error_type="cpp_not_found")
        assert error.error_type == "cpp_not_found"

    def test_all_fields(self):
        """Should store all fields."""
        error = PreprocessError(
            "timeout",
            file_path="test.c",
            error_type="timeout"
        )
        assert error.file_path == "test.c"
        assert error.error_type == "timeout"


class TestConfigError:
    """Tests for ConfigError exception."""

    def test_inherits_from_base(self):
        """Should inherit from AutosarCalltreeError."""
        assert issubclass(ConfigError, AutosarCalltreeError)

    def test_message(self):
        """Should work with message."""
        with pytest.raises(ConfigError, match="invalid config"):
            raise ConfigError("invalid config")


class TestDatabaseError:
    """Tests for DatabaseError exception."""

    def test_inherits_from_base(self):
        """Should inherit from AutosarCalltreeError."""
        assert issubclass(DatabaseError, AutosarCalltreeError)

    def test_message(self):
        """Should work with message."""
        with pytest.raises(DatabaseError, match="cache error"):
            raise DatabaseError("cache error")
