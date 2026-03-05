"""
Preprocessor configuration management for C++ preprocessor (cpp) settings.

This module provides functionality for loading and managing YAML-based
configurations for the C preprocessor used by pycparser.

Example YAML format:
    version: "1.0"

    preprocessor:
      # Preprocessor command (gcc, clang, etc.)
      command: "gcc"

      # Include directories (-I flags)
      include_dirs:
        - "./demo/include"
        - "/opt/autosar/include"
        - "../src"

      # Additional preprocessor flags
      extra_flags:
        - "-DUSE_RTE=1"
        - "-DDEBUG"
        - "-std=c99"

      # Enable/disable cpp preprocessing
      enabled: true
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class PreprocessorConfig:
    """
    Manages C preprocessor configuration from YAML file.

    This class handles loading and validating preprocessor settings
    for use with pycparser-based C parsing.

    Attributes:
        command: Preprocessor command (e.g., "gcc", "clang")
        include_dirs: List of include directories
        extra_flags: List of additional preprocessor flags
        enabled: Whether cpp preprocessing is enabled
    """

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initialize the preprocessor configuration.

        Args:
            config_path: Path to YAML configuration file (optional)
        """
        self.command: str = "gcc"
        self.include_dirs: List[str] = []
        self.extra_flags: List[str] = []
        self.enabled: bool = True

        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: Path) -> None:
        """
        Load preprocessor configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(
                "Invalid configuration format: expected dictionary at root level"
            )

        # Get preprocessor section
        preprocessor_config = data.get("preprocessor", {})
        if not isinstance(preprocessor_config, dict):
            raise ValueError("'preprocessor' must be a dictionary")

        # Load command
        command = preprocessor_config.get("command", "gcc")
        if command is None:
            command = "gcc"
        if not isinstance(command, str):
            raise ValueError("'command' must be a string")
        self.command = command

        # Load include directories
        include_dirs = preprocessor_config.get("include_dirs", [])
        if include_dirs is None:
            include_dirs = []
        if not isinstance(include_dirs, list):
            raise ValueError("'include_dirs' must be a list")
        for inc_dir in include_dirs:
            if not isinstance(inc_dir, str):
                raise ValueError("Each include directory must be a string")
        self.include_dirs = include_dirs

        # Load extra flags
        extra_flags = preprocessor_config.get("extra_flags", [])
        if extra_flags is None:
            extra_flags = []
        if not isinstance(extra_flags, list):
            raise ValueError("'extra_flags' must be a list")
        for flag in extra_flags:
            if not isinstance(flag, str):
                raise ValueError("Each extra flag must be a string")
        self.extra_flags = extra_flags

        # Load enabled flag
        enabled = preprocessor_config.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError("'enabled' must be a boolean")
        self.enabled = enabled

    def get_compiler_args(self) -> List[str]:
        """
        Build compiler argument list for subprocess call.

        Returns:
            List of arguments suitable for subprocess.run()
        """
        args = [self.command, "-E"]

        # Add include directories as -I flags
        for inc_dir in self.include_dirs:
            args.extend(["-I", inc_dir])

        # Add extra flags
        args.extend(self.extra_flags)

        return args

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the configuration.

        Returns:
            Dictionary with configuration statistics
        """
        return {
            "command": self.command,
            "include_dirs_count": len(self.include_dirs),
            "extra_flags_count": len(self.extra_flags),
            "enabled": self.enabled,
        }
