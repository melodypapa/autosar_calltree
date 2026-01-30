"""
Unit tests for Module Configuration module.

Tests the ModuleConfig class which manages SW module mappings from YAML files.
"""

from pathlib import Path

import pytest

from autosar_calltree.config.module_config import ModuleConfig


# Test fixtures
@pytest.fixture
def valid_config_path(test_fixtures_dir: Path) -> Path:
    """Path to valid configuration file."""
    return test_fixtures_dir / "config" / "valid_module_config.yaml"


@pytest.fixture
def minimal_config_path(test_fixtures_dir: Path) -> Path:
    """Path to minimal configuration file."""
    return test_fixtures_dir / "config" / "minimal_config.yaml"


@pytest.fixture
def only_patterns_config_path(test_fixtures_dir: Path) -> Path:
    """Path to config with only pattern mappings."""
    return test_fixtures_dir / "config" / "only_patterns.yaml"


@pytest.fixture
def only_default_config_path(test_fixtures_dir: Path) -> Path:
    """Path to config with only default module."""
    return test_fixtures_dir / "config" / "only_default.yaml"


# SWUT_CONFIG_00001: Configuration File Loading
def test_SWUT_CONFIG_00001_load_valid_config(valid_config_path: Path) -> None:
    """Test loading a valid YAML configuration file."""
    config = ModuleConfig(valid_config_path)

    # Check specific file mappings
    assert config.specific_mappings == {
        "demo.c": "DemoModule",
        "main.c": "Application",
        "test.c": "TestModule",
    }

    # Check pattern mappings (compiled regex)
    assert len(config.pattern_mappings) == 4
    for pattern, module in config.pattern_mappings:
        assert hasattr(pattern, "match")  # Should be compiled regex
        assert isinstance(module, str)

    # Check default module
    assert config.default_module == "Other"


# SWUT_CONFIG_00002: Missing Configuration File
def test_SWUT_CONFIG_00002_missing_config_file(tmp_path: Path) -> None:
    """Test FileNotFoundError when configuration file doesn't exist."""
    config_path = tmp_path / "nonexistent_config.yaml"

    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        ModuleConfig(config_path)


# SWUT_CONFIG_00003: Invalid YAML Format
def test_SWUT_CONFIG_00003_invalid_yaml(tmp_path: Path) -> None:
    """Test ValueError for malformed YAML."""
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text(
        """
file_mappings:
  demo.c: DemoModule
    invalid_indentation: value
"""
    )

    with pytest.raises(
        (ValueError, Exception)
    ):  # Could be ValueError or yaml.YAMLError
        ModuleConfig(config_path)


# SWUT_CONFIG_00004: Non-Dictionary Root
def test_SWUT_CONFIG_00004_invalid_root_type(test_fixtures_dir: Path) -> None:
    """Test ValueError when root element is not a dictionary."""
    config_path = test_fixtures_dir / "config" / "invalid_root_list.yaml"

    with pytest.raises(ValueError, match="expected dictionary at root level"):
        ModuleConfig(config_path)


# SWUT_CONFIG_00005: Invalid File Mappings Type
def test_SWUT_CONFIG_00005_invalid_file_mappings_type(test_fixtures_dir: Path) -> None:
    """Test ValueError when file_mappings is not a dictionary."""
    config_path = test_fixtures_dir / "config" / "invalid_file_mappings_list.yaml"

    with pytest.raises(ValueError, match="'file_mappings' must be a dictionary"):
        ModuleConfig(config_path)


# SWUT_CONFIG_00006: Empty Module Names in File Mappings
def test_SWUT_CONFIG_00006_empty_module_name_file_mappings(
    test_fixtures_dir: Path,
) -> None:
    """Test ValueError when module names are empty strings."""
    config_path = test_fixtures_dir / "config" / "empty_module_name.yaml"

    with pytest.raises(ValueError, match="Module name cannot be empty"):
        ModuleConfig(config_path)


# SWUT_CONFIG_00007: Non-String File Mapping Values
def test_SWUT_CONFIG_00007_non_string_file_mappings(test_fixtures_dir: Path) -> None:
    """Test ValueError for non-string mapping values."""
    config_path = test_fixtures_dir / "config" / "non_string_mappings.yaml"

    with pytest.raises(ValueError, match="File mappings must be strings"):
        ModuleConfig(config_path)


# SWUT_CONFIG_00008: Pattern Mappings Compilation
def test_SWUT_CONFIG_00008_pattern_compilation(valid_config_path: Path) -> None:
    """Test that glob patterns are correctly compiled to regex."""
    config = ModuleConfig(valid_config_path)

    assert len(config.pattern_mappings) == 4

    # Each pattern should be a tuple of (compiled_regex, module_name)
    for pattern, module in config.pattern_mappings:
        assert hasattr(pattern, "match")  # Compiled regex has match method
        assert isinstance(module, str)
        assert module in [
            "HardwareModule",
            "SoftwareModule",
            "CommunicationModule",
            "DriverModule",
        ]


# SWUT_CONFIG_00009: Invalid Pattern Mappings Type
def test_SWUT_CONFIG_00009_invalid_pattern_mappings_type(
    test_fixtures_dir: Path,
) -> None:
    """Test ValueError when pattern_mappings is not a dictionary."""
    config_path = test_fixtures_dir / "config" / "invalid_pattern_mappings_list.yaml"

    with pytest.raises(ValueError, match="'pattern_mappings' must be a dictionary"):
        ModuleConfig(config_path)


# SWUT_CONFIG_00010: Empty Module Names in Pattern Mappings
def test_SWUT_CONFIG_00010_empty_module_name_pattern_mappings(
    test_fixtures_dir: Path,
) -> None:
    """Test ValueError when pattern module names are empty."""
    config_path = test_fixtures_dir / "config" / "empty_module_name.yaml"

    with pytest.raises(ValueError, match="Module name cannot be empty"):
        ModuleConfig(config_path)


# SWUT_CONFIG_00011: Default Module Assignment
def test_SWUT_CONFIG_00011_default_module(only_default_config_path: Path) -> None:
    """Test that default_module is correctly loaded."""
    config = ModuleConfig(only_default_config_path)

    assert config.default_module == "Other"


# SWUT_CONFIG_00012: Invalid Default Module Type
def test_SWUT_CONFIG_00012_invalid_default_module_type(test_fixtures_dir: Path) -> None:
    """Test ValueError when default_module is not a string."""
    config_path = test_fixtures_dir / "config" / "invalid_default_module.yaml"

    with pytest.raises(ValueError, match="'default_module' must be a non-empty string"):
        ModuleConfig(config_path)


# SWUT_CONFIG_00013: Empty Default Module
def test_SWUT_CONFIG_00013_empty_default_module(test_fixtures_dir: Path) -> None:
    """Test ValueError when default_module is whitespace only."""
    config_path = test_fixtures_dir / "config" / "empty_default_module.yaml"

    with pytest.raises(ValueError, match="'default_module' must be a non-empty string"):
        ModuleConfig(config_path)


# SWUT_CONFIG_00014: Specific File Mapping Lookup
def test_SWUT_CONFIG_00014_specific_file_lookup(valid_config_path: Path) -> None:
    """Test get_module_for_file returns correct module for exact filename match."""
    config = ModuleConfig(valid_config_path)

    # Test with full path (should only use filename)
    assert config.get_module_for_file(Path("/some/path/to/demo.c")) == "DemoModule"
    assert config.get_module_for_file(Path("main.c")) == "Application"
    assert config.get_module_for_file(Path("test.c")) == "TestModule"


# SWUT_CONFIG_00015: Pattern Mapping Lookup
def test_SWUT_CONFIG_00015_pattern_lookup(valid_config_path: Path) -> None:
    """Test get_module_for_file matches glob patterns correctly."""
    config = ModuleConfig(valid_config_path)

    assert config.get_module_for_file(Path("hw_driver.c")) == "HardwareModule"
    assert config.get_module_for_file(Path("hw_init.c")) == "HardwareModule"
    assert config.get_module_for_file(Path("sw_component.c")) == "SoftwareModule"
    assert config.get_module_for_file(Path("sw_handler.c")) == "SoftwareModule"
    assert config.get_module_for_file(Path("com_layer.c")) == "CommunicationModule"
    assert config.get_module_for_file(Path("drv_spi.c")) == "DriverModule"


# SWUT_CONFIG_00016: Specific Mapping Takes Precedence Over Pattern
def test_SWUT_CONFIG_00016_specific_overrides_pattern(tmp_path: Path) -> None:
    """Test that specific file mappings take precedence over pattern mappings."""
    config_path = tmp_path / "precedence_test.yaml"
    config_path.write_text(
        """
file_mappings:
  hw_driver.c: SpecialModule
pattern_mappings:
  "hw_*.c": HardwareModule
"""
    )

    config = ModuleConfig(config_path)

    # hw_driver.c matches both specific and pattern
    assert (
        config.get_module_for_file(Path("hw_driver.c")) == "SpecialModule"
    )  # Specific wins
    # hw_init.c only matches pattern
    assert config.get_module_for_file(Path("hw_init.c")) == "HardwareModule"


# SWUT_CONFIG_00017: Default Module Fallback
def test_SWUT_CONFIG_00017_default_module_fallback(minimal_config_path: Path) -> None:
    """Test that default module is returned when no match."""
    config = ModuleConfig(minimal_config_path)

    # Has default_module
    assert config.get_module_for_file(Path("demo.c")) == "DemoModule"
    assert config.get_module_for_file(Path("unmapped.c")) is None  # No default


def test_SWUT_CONFIG_00017_default_module_fallback_with_default(
    only_default_config_path: Path,
) -> None:
    """Test default module fallback when default_module is set."""
    config = ModuleConfig(only_default_config_path)

    assert config.get_module_for_file(Path("unmapped.c")) == "Other"
    assert config.get_module_for_file(Path("unknown.h")) == "Other"


# SWUT_CONFIG_00018: No Match Returns None
def test_SWUT_CONFIG_00018_no_match_returns_none(minimal_config_path: Path) -> None:
    """Test get_module_for_file returns None when no match and no default."""
    config = ModuleConfig(minimal_config_path)

    assert config.get_module_for_file(Path("unmapped.c")) is None
    assert config.get_module_for_file(Path("unknown.h")) is None


# SWUT_CONFIG_00019: Lookup Caching
def test_SWUT_CONFIG_00019_lookup_caching(valid_config_path: Path) -> None:
    """Test that lookup results are cached for performance."""
    config = ModuleConfig(valid_config_path)
    file_path = Path("demo.c")

    # First lookup
    module1 = config.get_module_for_file(file_path)
    assert "demo.c" in config._lookup_cache
    assert module1 == "DemoModule"

    # Second lookup should use cache
    module2 = config.get_module_for_file(file_path)
    assert module2 == "DemoModule"
    assert config._lookup_cache["demo.c"] == "DemoModule"


# SWUT_CONFIG_00020: Cache Stores None Results
def test_SWUT_CONFIG_00020_cache_stores_none(minimal_config_path: Path) -> None:
    """Test that cache stores None for unmapped files."""
    config = ModuleConfig(minimal_config_path)
    file_path = Path("unmapped.c")

    # First lookup
    module1 = config.get_module_for_file(file_path)
    assert module1 is None
    assert "unmapped.c" in config._lookup_cache
    assert config._lookup_cache["unmapped.c"] is None

    # Second lookup also returns None (from cache)
    module2 = config.get_module_for_file(file_path)
    assert module2 is None


# SWUT_CONFIG_00021: Configuration Validation Success
def test_SWUT_CONFIG_00021_validate_success(valid_config_path: Path) -> None:
    """Test validate_config returns empty list for valid configuration."""
    config = ModuleConfig(valid_config_path)

    errors = config.validate_config()
    assert errors == []


# SWUT_CONFIG_00022: Configuration Validation Failure
def test_SWUT_CONFIG_00022_validate_empty_config(tmp_path: Path) -> None:
    """Test validate_config detects empty configuration."""
    config_path = tmp_path / "empty_config.yaml"
    config_path.write_text("{}")

    config = ModuleConfig(config_path)

    errors = config.validate_config()
    assert len(errors) > 0
    assert "must contain either" in errors[0]


# SWUT_CONFIG_00023: Configuration Statistics
def test_SWUT_CONFIG_00023_statistics(valid_config_path: Path) -> None:
    """Test get_statistics returns correct counts."""
    config = ModuleConfig(valid_config_path)

    stats = config.get_statistics()

    assert stats["specific_file_mappings"] == 3
    assert stats["pattern_mappings"] == 4
    assert stats["has_default_module"] == 1


# SWUT_CONFIG_00024: Empty Configuration Initialization
def test_SWUT_CONFIG_00024_empty_initialization() -> None:
    """Test ModuleConfig initialization without config file."""
    config = ModuleConfig()  # No config_path

    assert config.specific_mappings == {}
    assert config.pattern_mappings == []
    assert config.default_module is None
    assert config.get_module_for_file(Path("any.c")) is None


# SWUT_CONFIG_00025: Multiple Pattern Match Order
def test_SWUT_CONFIG_00025_pattern_match_order(tmp_path: Path) -> None:
    """Test that first matching pattern in configuration is used."""
    config_path = tmp_path / "pattern_order.yaml"
    config_path.write_text(
        """
pattern_mappings:
  "hw_*.c": HardwareModule
  "hw_init.c": InitModule
  "*_init.c": GenericInitModule
"""
    )

    config = ModuleConfig(config_path)

    # hw_init.c matches all three patterns, should get first match
    module = config.get_module_for_file(Path("hw_init.c"))
    assert module == "HardwareModule"  # First pattern wins


# Additional edge case tests


def test_pattern_matching_with_wildcards(tmp_path: Path) -> None:
    """Test various glob pattern wildcard scenarios."""
    config_path = tmp_path / "wildcards.yaml"
    config_path.write_text(
        """
pattern_mappings:
  "test_*.c": TestModule
  "*_test.c": TestSuffixModule
  "file?.c": SingleCharModule
"""
    )

    config = ModuleConfig(config_path)

    # Test wildcard at end
    assert config.get_module_for_file(Path("test_driver.c")) == "TestModule"
    assert config.get_module_for_file(Path("test_a.c")) == "TestModule"

    # Test wildcard at beginning
    assert config.get_module_for_file(Path("unit_test.c")) == "TestSuffixModule"
    assert config.get_module_for_file(Path("my_test.c")) == "TestSuffixModule"

    # Test single character wildcard
    assert config.get_module_for_file(Path("file1.c")) == "SingleCharModule"
    assert config.get_module_for_file(Path("filea.c")) == "SingleCharModule"


def test_case_sensitive_matching(tmp_path: Path) -> None:
    """Test that pattern matching is case-sensitive."""
    config_path = tmp_path / "case_sensitive.yaml"
    config_path.write_text(
        """
pattern_mappings:
  "HW_*.c": HardwareModule
"""
    )

    config = ModuleConfig(config_path)

    assert config.get_module_for_file(Path("HW_driver.c")) == "HardwareModule"
    assert (
        config.get_module_for_file(Path("hw_driver.c")) is None
    )  # Lowercase doesn't match


def test_module_lookup_with_path_separator(tmp_path: Path) -> None:
    """Test that lookup only uses filename, not full path."""
    config_path = tmp_path / "path_test.yaml"
    config_path.write_text(
        """
file_mappings:
  demo.c: DemoModule
pattern_mappings:
  "hw_*.c": HardwareModule
"""
    )

    config = ModuleConfig(config_path)

    # Full path should work
    assert config.get_module_for_file(Path("/very/long/path/to/demo.c")) == "DemoModule"
    assert (
        config.get_module_for_file(Path("./relative/hw_driver.c")) == "HardwareModule"
    )


def test_statistics_without_default_module(tmp_path: Path) -> None:
    """Test statistics when no default module is set."""
    config_path = tmp_path / "no_default.yaml"
    config_path.write_text(
        """
file_mappings:
  demo.c: DemoModule
pattern_mappings:
  "hw_*.c": HardwareModule
"""
    )

    config = ModuleConfig(config_path)
    stats = config.get_statistics()

    assert stats["specific_file_mappings"] == 1
    assert stats["pattern_mappings"] == 1
    assert stats["has_default_module"] == 0


def test_cache_invalidation_between_lookups(tmp_path: Path) -> None:
    """Test that cache persists across multiple lookups."""
    config_path = tmp_path / "cache_test.yaml"
    config_path.write_text(
        """
file_mappings:
  demo.c: DemoModule
pattern_mappings:
  "hw_*.c": HardwareModule
"""
    )

    config = ModuleConfig(config_path)

    # First lookup for demo.c
    assert config.get_module_for_file(Path("demo.c")) == "DemoModule"
    assert config._lookup_cache["demo.c"] == "DemoModule"

    # Lookup for different file
    assert config.get_module_for_file(Path("hw_test.c")) == "HardwareModule"
    assert config._lookup_cache["hw_test.c"] == "HardwareModule"

    # Verify first cache entry still exists
    assert config._lookup_cache["demo.c"] == "DemoModule"


def test_minimal_config_with_only_file_mappings(minimal_config_path: Path) -> None:
    """Test config with only file mappings (no patterns, no default)."""
    config = ModuleConfig(minimal_config_path)

    assert len(config.specific_mappings) == 1
    assert config.specific_mappings["demo.c"] == "DemoModule"
    assert len(config.pattern_mappings) == 0
    assert config.default_module is None


def test_config_with_only_patterns(only_patterns_config_path: Path) -> None:
    """Test config with only pattern mappings."""
    config = ModuleConfig(only_patterns_config_path)

    assert len(config.specific_mappings) == 0
    assert len(config.pattern_mappings) == 2
    assert config.default_module is None

    # Test pattern lookups
    assert config.get_module_for_file(Path("hw_test.c")) == "HardwareModule"
    assert config.get_module_for_file(Path("sw_test.c")) == "SoftwareModule"


def test_get_module_for_file_with_different_extensions(tmp_path: Path) -> None:
    """Test that lookup works regardless of file extension."""
    config_path = tmp_path / "extension_test.yaml"
    config_path.write_text(
        """
file_mappings:
  demo.c: DemoModule
pattern_mappings:
  "hw_*.c": HardwareModule
default_module: "Other"
"""
    )

    config = ModuleConfig(config_path)

    # .c files match
    assert config.get_module_for_file(Path("demo.c")) == "DemoModule"
    assert config.get_module_for_file(Path("hw_test.c")) == "HardwareModule"

    # Other extensions use default
    assert config.get_module_for_file(Path("demo.h")) == "Other"
    assert config.get_module_for_file(Path("hw_test.h")) == "Other"
