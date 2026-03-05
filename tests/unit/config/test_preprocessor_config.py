"""
Unit tests for Preprocessor Configuration module.

Tests the PreprocessorConfig class which manages C preprocessor settings from YAML files.
"""

from pathlib import Path

import pytest

from autosar_calltree.config.preprocessor_config import PreprocessorConfig


# Test fixtures
@pytest.fixture
def valid_config_path(test_fixtures_dir: Path) -> Path:
    """Path to valid preprocessor configuration file."""
    return test_fixtures_dir / "config" / "valid_preprocessor_config.yaml"


@pytest.fixture
def minimal_config_path(test_fixtures_dir: Path) -> Path:
    """Path to minimal preprocessor configuration file."""
    return test_fixtures_dir / "config" / "minimal_preprocessor_config.yaml"


@pytest.fixture
def no_preprocessor_key_path(test_fixtures_dir: Path) -> Path:
    """Path to config without preprocessor key."""
    return test_fixtures_dir / "config" / "preprocessor_no_preprocessor_key.yaml"


@pytest.fixture
def clang_config_path(test_fixtures_dir: Path) -> Path:
    """Path to config with clang command."""
    return test_fixtures_dir / "config" / "preprocessor_clang.yaml"


@pytest.fixture
def many_includes_config_path(test_fixtures_dir: Path) -> Path:
    """Path to config with many include dirs."""
    return test_fixtures_dir / "config" / "preprocessor_many_includes.yaml"


@pytest.fixture
def disabled_config_path(test_fixtures_dir: Path) -> Path:
    """Path to config with enabled: false."""
    return test_fixtures_dir / "config" / "preprocessor_disabled.yaml"


# ============================================================================
# SWUT_CONFIG_CPP_00001: Load Valid Configuration
# ============================================================================


def test_load_valid_config(valid_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00001: Test loading a valid YAML configuration file."""
    config = PreprocessorConfig(valid_config_path)

    assert config.command == "gcc"
    assert len(config.include_dirs) == 2
    assert "./demo/include" in config.include_dirs
    assert "/opt/autosar/include" in config.include_dirs
    assert len(config.extra_flags) == 2
    assert "-DUSE_RTE=1" in config.extra_flags
    assert "-std=c99" in config.extra_flags
    assert config.enabled is True


# ============================================================================
# SWUT_CONFIG_CPP_00002: Missing Configuration File
# ============================================================================


def test_missing_config_file(tmp_path: Path) -> None:
    """SWUT_CONFIG_CPP_00002: Test FileNotFoundError when config file doesn't exist."""
    config_path = tmp_path / "nonexistent_config.yaml"

    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        PreprocessorConfig(config_path)


# ============================================================================
# SWUT_CONFIG_CPP_00003: Invalid YAML Format
# ============================================================================


def test_invalid_yaml_format(tmp_path: Path) -> None:
    """SWUT_CONFIG_CPP_00003: Test ValueError for malformed YAML."""
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text(
        """
invalid: yaml: [unclosed
"""
    )

    with pytest.raises((ValueError, Exception)):
        PreprocessorConfig(config_path)


# ============================================================================
# SWUT_CONFIG_CPP_00004: Invalid Root Type
# ============================================================================


def test_invalid_root_type(test_fixtures_dir: Path) -> None:
    """SWUT_CONFIG_CPP_00004: Test ValueError when root is not dict."""
    config_path = test_fixtures_dir / "config" / "preprocessor_invalid_root_list.yaml"

    with pytest.raises(ValueError, match="expected dictionary at root level"):
        PreprocessorConfig(config_path)


# ============================================================================
# SWUT_CONFIG_CPP_00005: Invalid Preprocessor Section
# ============================================================================


def test_invalid_preprocessor_section(test_fixtures_dir: Path) -> None:
    """SWUT_CONFIG_CPP_00005: Test ValueError when 'preprocessor' not dict."""
    config_path = (
        test_fixtures_dir / "config" / "preprocessor_invalid_preprocessor_type.yaml"
    )

    with pytest.raises(ValueError, match="'preprocessor' must be a dictionary"):
        PreprocessorConfig(config_path)


# ============================================================================
# SWUT_CONFIG_CPP_00006: Command Defaults to gcc
# ============================================================================


def test_command_defaults_to_gcc(minimal_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00006: Test default command is 'gcc'."""
    config = PreprocessorConfig(minimal_config_path)

    assert config.command == "gcc"


# ============================================================================
# SWUT_CONFIG_CPP_00007: Command Custom Value
# ============================================================================


def test_command_custom_value(clang_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00007: Test load custom command (clang, etc.)."""
    config = PreprocessorConfig(clang_config_path)

    assert config.command == "clang"


# ============================================================================
# SWUT_CONFIG_CPP_00008: Command Invalid Type
# ============================================================================


def test_command_invalid_type(test_fixtures_dir: Path) -> None:
    """SWUT_CONFIG_CPP_00008: Test ValueError for non-string command."""
    config_path = (
        test_fixtures_dir / "config" / "preprocessor_invalid_command_type.yaml"
    )

    with pytest.raises(ValueError, match="'command' must be a string"):
        PreprocessorConfig(config_path)


# ============================================================================
# SWUT_CONFIG_CPP_00009: Include Dirs Loaded
# ============================================================================


def test_include_dirs_loaded(valid_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00009: Test load include directories list."""
    config = PreprocessorConfig(valid_config_path)

    assert len(config.include_dirs) == 2
    assert "./demo/include" in config.include_dirs
    assert "/opt/autosar/include" in config.include_dirs


# ============================================================================
# SWUT_CONFIG_CPP_00010: Include Dirs Empty
# ============================================================================


def test_include_dirs_empty(minimal_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00010: Test empty list when not specified."""
    config = PreprocessorConfig(minimal_config_path)

    assert config.include_dirs == []


# ============================================================================
# SWUT_CONFIG_CPP_00011: Include Dirs Invalid Type
# ============================================================================


def test_include_dirs_invalid_type(test_fixtures_dir: Path) -> None:
    """SWUT_CONFIG_CPP_00011: Test ValueError for non-list include_dirs."""
    config_path = (
        test_fixtures_dir / "config" / "preprocessor_invalid_include_dirs_type.yaml"
    )

    with pytest.raises(ValueError, match="'include_dirs' must be a list"):
        PreprocessorConfig(config_path)


# ============================================================================
# SWUT_CONFIG_CPP_00012: Include Dir Invalid Item
# ============================================================================


def test_include_dir_invalid_item(test_fixtures_dir: Path) -> None:
    """SWUT_CONFIG_CPP_00012: Test ValueError for non-string item in list."""
    config_path = (
        test_fixtures_dir / "config" / "preprocessor_invalid_include_item_type.yaml"
    )

    with pytest.raises(ValueError, match="Each include directory must be a string"):
        PreprocessorConfig(config_path)


# ============================================================================
# SWUT_CONFIG_CPP_00013: Extra Flags Loaded
# ============================================================================


def test_extra_flags_loaded(valid_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00013: Test load extra flags list."""
    config = PreprocessorConfig(valid_config_path)

    assert len(config.extra_flags) == 2
    assert "-DUSE_RTE=1" in config.extra_flags
    assert "-std=c99" in config.extra_flags


# ============================================================================
# SWUT_CONFIG_CPP_00014: Extra Flags Empty
# ============================================================================


def test_extra_flags_empty(minimal_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00014: Test empty list when not specified."""
    config = PreprocessorConfig(minimal_config_path)

    assert config.extra_flags == []


# ============================================================================
# SWUT_CONFIG_CPP_00015: Extra Flags Invalid Type
# ============================================================================


def test_extra_flags_invalid_type(test_fixtures_dir: Path) -> None:
    """SWUT_CONFIG_CPP_00015: Test ValueError for non-list extra_flags."""
    config_path = (
        test_fixtures_dir / "config" / "preprocessor_invalid_extra_flags_type.yaml"
    )

    with pytest.raises(ValueError, match="'extra_flags' must be a list"):
        PreprocessorConfig(config_path)


# ============================================================================
# SWUT_CONFIG_CPP_00016: Extra Flag Invalid Item
# ============================================================================


def test_extra_flag_invalid_item(test_fixtures_dir: Path) -> None:
    """SWUT_CONFIG_CPP_00016: Test ValueError for non-string flag."""
    config_path = (
        test_fixtures_dir / "config" / "preprocessor_invalid_extra_flag_item.yaml"
    )

    with pytest.raises(ValueError, match="Each extra flag must be a string"):
        PreprocessorConfig(config_path)


# ============================================================================
# SWUT_CONFIG_CPP_00017: Enabled True
# ============================================================================


def test_enabled_true(valid_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00017: Test load enabled: true."""
    config = PreprocessorConfig(valid_config_path)

    assert config.enabled is True


# ============================================================================
# SWUT_CONFIG_CPP_00018: Enabled False
# ============================================================================


def test_enabled_false(disabled_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00018: Test load enabled: false."""
    config = PreprocessorConfig(disabled_config_path)

    assert config.enabled is False


# ============================================================================
# SWUT_CONFIG_CPP_00019: Enabled Default
# ============================================================================


def test_enabled_default(minimal_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00019: Test defaults to true when not specified."""
    config = PreprocessorConfig(minimal_config_path)

    assert config.enabled is True


# ============================================================================
# SWUT_CONFIG_CPP_00020: Enabled Invalid Type
# ============================================================================


def test_enabled_invalid_type(test_fixtures_dir: Path) -> None:
    """SWUT_CONFIG_CPP_00020: Test ValueError for non-boolean enabled."""
    config_path = (
        test_fixtures_dir / "config" / "preprocessor_invalid_enabled_type.yaml"
    )

    with pytest.raises(ValueError, match="'enabled' must be a boolean"):
        PreprocessorConfig(config_path)


# ============================================================================
# SWUT_CONFIG_CPP_00021: Get Compiler Args
# ============================================================================


def test_get_compiler_args(valid_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00021: Test build correct compiler argument list."""
    config = PreprocessorConfig(valid_config_path)

    args = config.get_compiler_args()

    # First arg should be command, second should be -E
    assert args[0] == "gcc"
    assert args[1] == "-E"

    # Check include directories are added as -I flags
    assert "-I" in args
    assert "./demo/include" in args
    assert "/opt/autosar/include" in args

    # Check extra flags are included
    assert "-DUSE_RTE=1" in args
    assert "-std=c99" in args


# ============================================================================
# SWUT_CONFIG_CPP_00022: Get Compiler Args Empty
# ============================================================================


def test_get_compiler_args_empty(minimal_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00022: Test minimal args when no includes/flags."""
    config = PreprocessorConfig(minimal_config_path)

    args = config.get_compiler_args()

    # Should only have command and -E
    assert args == ["gcc", "-E"]


# ============================================================================
# SWUT_CONFIG_CPP_00023: Get Statistics
# ============================================================================


def test_get_statistics(valid_config_path: Path) -> None:
    """SWUT_CONFIG_CPP_00023: Test return correct statistics dictionary."""
    config = PreprocessorConfig(valid_config_path)

    stats = config.get_statistics()

    assert stats["command"] == "gcc"
    assert stats["include_dirs_count"] == 2
    assert stats["extra_flags_count"] == 2
    assert stats["enabled"] is True


# ============================================================================
# SWUT_CONFIG_CPP_00024: Empty Initialization
# ============================================================================


def test_empty_initialization() -> None:
    """SWUT_CONFIG_CPP_00024: Test initialize without config file."""
    config = PreprocessorConfig()  # No config_path

    assert config.command == "gcc"
    assert config.include_dirs == []
    assert config.extra_flags == []
    assert config.enabled is True


# ============================================================================
# SWUT_CONFIG_CPP_00025: Null Command Value
# ============================================================================


def test_null_command_value(tmp_path: Path) -> None:
    """SWUT_CONFIG_CPP_00025: Test null command defaults to gcc."""
    config_path = tmp_path / "null_command.yaml"
    config_path.write_text(
        """
version: "1.0"
preprocessor:
  command: null
"""
    )

    config = PreprocessorConfig(config_path)

    # Null command should default to "gcc"
    assert config.command == "gcc"


# ============================================================================
# SWUT_CONFIG_CPP_00026: Null Include Dirs Value
# ============================================================================


def test_null_include_dirs_value(tmp_path: Path) -> None:
    """SWUT_CONFIG_CPP_00026: Test null include_dirs defaults to []."""
    config_path = tmp_path / "null_include_dirs.yaml"
    config_path.write_text(
        """
version: "1.0"
preprocessor:
  include_dirs: null
"""
    )

    config = PreprocessorConfig(config_path)

    # Null include_dirs should default to empty list
    assert config.include_dirs == []


# ============================================================================
# SWUT_CONFIG_CPP_00027: Null Extra Flags Value
# ============================================================================


def test_null_extra_flags_value(tmp_path: Path) -> None:
    """SWUT_CONFIG_CPP_00027: Test null extra_flags defaults to []."""
    config_path = tmp_path / "null_extra_flags.yaml"
    config_path.write_text(
        """
version: "1.0"
preprocessor:
  extra_flags: null
"""
    )

    config = PreprocessorConfig(config_path)

    # Null extra_flags should default to empty list
    assert config.extra_flags == []


# ============================================================================
# Additional Edge Case Tests
# ============================================================================


def test_no_preprocessor_key_uses_defaults(no_preprocessor_key_path: Path) -> None:
    """Test that missing 'preprocessor' key uses all defaults."""
    config = PreprocessorConfig(no_preprocessor_key_path)

    assert config.command == "gcc"
    assert config.include_dirs == []
    assert config.extra_flags == []
    assert config.enabled is True


def test_compiler_args_with_many_includes(many_includes_config_path: Path) -> None:
    """Test get_compiler_args with multiple include directories."""
    config = PreprocessorConfig(many_includes_config_path)

    args = config.get_compiler_args()

    # Should have 3 include directories
    assert args.count("./include1") == 1
    assert args.count("./include2") == 1
    assert args.count("./include3") == 1


def test_disabled_config_get_statistics(disabled_config_path: Path) -> None:
    """Test get_statistics returns enabled: false."""
    config = PreprocessorConfig(disabled_config_path)

    stats = config.get_statistics()

    assert stats["enabled"] is False


def test_compiler_args_with_clang(clang_config_path: Path) -> None:
    """Test get_compiler_args uses clang command."""
    config = PreprocessorConfig(clang_config_path)

    args = config.get_compiler_args()

    # First arg should be clang
    assert args[0] == "clang"
    assert args[1] == "-E"


def test_load_config_with_no_preprocessor_key(tmp_path: Path) -> None:
    """Test load_config method with config file lacking preprocessor key."""
    config_path = tmp_path / "no_preprocessor.yaml"
    config_path.write_text(
        """
version: "1.0"
other_key: value
"""
    )

    config = PreprocessorConfig()
    config.load_config(config_path)

    # Should use defaults when preprocessor key is missing
    assert config.command == "gcc"
    assert config.include_dirs == []
    assert config.extra_flags == []
    assert config.enabled is True


def test_load_config_replaces_existing_values(
    clang_config_path: Path, valid_config_path: Path
) -> None:
    """Test that load_config replaces existing values."""
    # First load with one config
    config = PreprocessorConfig(clang_config_path)
    assert config.command == "clang"

    # Then load with a different config
    config.load_config(valid_config_path)

    # Values should be replaced
    assert config.command == "gcc"
    assert len(config.include_dirs) == 2
