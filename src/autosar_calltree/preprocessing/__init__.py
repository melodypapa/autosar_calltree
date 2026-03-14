"""
Preprocessing module for C source files.

This module provides functionality for preprocessing C source files
using the C preprocessor (cpp) before parsing.
"""

from .cpp_preprocessor import CPPPreprocessor, PreprocessResult, PreprocessStatistics

__all__ = ["CPPPreprocessor", "PreprocessResult", "PreprocessStatistics"]
