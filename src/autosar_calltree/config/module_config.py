"""
Module configuration management for SW module mappings.

This module provides functionality for loading and managing YAML-based
configurations that map C source files to SW (Software) modules.

Requirements:
- SWR_CONFIG_00001: YAML Configuration File Support
- SWR_CONFIG_00002: Module Configuration Validation
"""

import fnmatch
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ModuleConfig:
    """
    Manages SW module configuration from YAML file.

    This class handles loading, validating, and looking up SW module mappings
    for C source files. It supports both specific file mappings and glob pattern
    mappings.

    Attributes:
        specific_mappings: Dictionary mapping exact filenames to module names
        pattern_mappings: List of compiled regex patterns and module names
        default_module: Default module name for unmapped files (optional)
        _lookup_cache: Cache for filename to module lookups
    """

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initialize the module configuration.

        Args:
            config_path: Path to YAML configuration file (optional)
        """
        self.specific_mappings: Dict[str, str] = {}
        self.pattern_mappings: List[Tuple[re.Pattern, str]] = []
        self.default_module: Optional[str] = None
        self._lookup_cache: Dict[str, Optional[str]] = {}

        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: Path) -> None:
        """
        Load module configuration from YAML file.

        Implements: SWR_CONFIG_00001 (YAML Configuration File Support)
        Implements: SWR_CONFIG_00002 (Module Configuration Validation)

        Args:
            config_path: Path to YAML configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        import yaml  # type: ignore

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(
                "Invalid configuration format: expected dictionary at root level"
            )

        # Load specific file mappings (exact filename match)
        file_mappings = data.get("file_mappings", {})
        if not isinstance(file_mappings, dict):
            raise ValueError("'file_mappings' must be a dictionary")

        for filename, module in file_mappings.items():
            if not isinstance(filename, str) or not isinstance(module, str):
                raise ValueError("File mappings must be strings")
            if not module.strip():
                raise ValueError(f"Module name cannot be empty for file: {filename}")
            self.specific_mappings[filename] = module

        # Load pattern mappings (glob patterns)
        pattern_mappings = data.get("pattern_mappings", {})
        if not isinstance(pattern_mappings, dict):
            raise ValueError("'pattern_mappings' must be a dictionary")

        for pattern, module in pattern_mappings.items():
            if not isinstance(pattern, str) or not isinstance(module, str):
                raise ValueError("Pattern mappings must be strings")
            if not module.strip():
                raise ValueError(f"Module name cannot be empty for pattern: {pattern}")

            # Compile glob pattern to regex for faster matching
            regex = fnmatch.translate(pattern)
            compiled = re.compile(regex)
            self.pattern_mappings.append((compiled, module))

        # Load default module (optional)
        default_module = data.get("default_module")
        if default_module is not None:
            if not isinstance(default_module, str) or not default_module.strip():
                raise ValueError("'default_module' must be a non-empty string")
            self.default_module = default_module

    def get_module_for_file(self, file_path: Path) -> Optional[str]:
        """
        Get SW module name for a given file.

        This method first checks specific file mappings, then pattern mappings,
        and finally returns the default module if configured.

        Lookup results are cached for performance.

        Args:
            file_path: Path to the source file

        Returns:
            Module name if found, None otherwise
        """
        filename = file_path.name

        # Check cache first
        if filename in self._lookup_cache:
            return self._lookup_cache[filename]

        # Check specific file mappings (exact match)
        if filename in self.specific_mappings:
            module = self.specific_mappings[filename]
            self._lookup_cache[filename] = module
            return module

        # Check pattern mappings (glob patterns)
        for pattern, module in self.pattern_mappings:
            if pattern.match(filename):
                self._lookup_cache[filename] = module
                return module

        # Use default module if configured
        if self.default_module is not None:
            self._lookup_cache[filename] = self.default_module
            return self.default_module

        # No match found
        self._lookup_cache[filename] = None
        return None

    def validate_config(self) -> List[str]:
        """
        Validate the current configuration.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.specific_mappings and not self.pattern_mappings:
            errors.append(
                "Configuration must contain either 'file_mappings' or 'pattern_mappings'"
            )

        return errors

    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the configuration.

        Returns:
            Dictionary with configuration statistics
        """
        return {
            "specific_file_mappings": len(self.specific_mappings),
            "pattern_mappings": len(self.pattern_mappings),
            "has_default_module": 1 if self.default_module else 0,
        }
