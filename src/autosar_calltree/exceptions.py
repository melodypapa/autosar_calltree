"""
Custom exception hierarchy for AUTOSAR Call Tree Analyzer.

This module provides specialized exceptions for better error tracing
and handling throughout the codebase.
"""

from typing import Optional

__all__ = [
    "AutosarCalltreeError",
    "ParseError",
    "PreprocessError",
    "ConfigError",
    "DatabaseError",
]


class AutosarCalltreeError(Exception):
    """Base exception for all autosar-calltree errors."""
    pass


class ParseError(AutosarCalltreeError):
    """
    Raised when parsing fails.

    Attributes:
        file_path: Path to the file being parsed (optional)
        line_number: Line number where error occurred (optional)
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None
    ):
        self.file_path = file_path
        self.line_number = line_number
        super().__init__(message)


class PreprocessError(AutosarCalltreeError):
    """
    Raised when preprocessing fails.

    Attributes:
        file_path: Path to the file being preprocessed (optional)
        error_type: Type of error ('cpp_not_found', 'cpp_error', 'timeout')
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        error_type: Optional[str] = None
    ):
        self.file_path = file_path
        self.error_type = error_type
        super().__init__(message)


class ConfigError(AutosarCalltreeError):
    """Raised when configuration is invalid."""
    pass


class DatabaseError(AutosarCalltreeError):
    """Raised when database operations fail."""
    pass
