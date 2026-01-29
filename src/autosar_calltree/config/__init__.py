"""
Configuration management for AUTOSAR Call Tree Analyzer.

This module provides functionality for managing YAML-based configurations,
including mapping C source files to SW modules.
"""

from .module_config import ModuleConfig

__all__ = ["ModuleConfig"]
