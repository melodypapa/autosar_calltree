"""
Configuration management for AUTOSAR Call Tree Analyzer.

This module provides functionality for managing YAML-based configurations,
including mapping C source files to SW modules and preprocessor settings.
"""

from .module_config import ModuleConfig
from .preprocessor_config import PreprocessorConfig

__all__ = ["ModuleConfig", "PreprocessorConfig"]
