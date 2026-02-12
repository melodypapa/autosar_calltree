"""Tests for cli/main.py (SWUT_CLI_00001-00018)"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import click

from autosar_calltree.cli.main import cli


# Helper to create temporary C source files
def create_temp_source_file(
    tmp_dir: Path, content: str, filename: str = "test.c"
) -> Path:
    """Create a temporary C source file for testing."""
    file_path = tmp_dir / filename
    file_path.write_text(content)
    return file_path


# SWUT_CLI_00001: Click Command Structure


def test_cli_command_exists() -> None:
    """SWUT_CLI_00001

    Test that CLI command is defined with Click decorator.
    """
    # The cli function should be callable
    assert callable(cli)
    assert cli.name == "cli"


# SWUT_CLI_00002: Start Function Option


def test_start_function_option() -> None:
    """SWUT_CLI_00002

    Test --start-function option definition and validation.
    """

    # Get the command from click's context
    @click.command()
    @click.option("--start-function", "-s", required=False)
    @click.option("--max-depth", "-d", default=3, type=int)
    @click.option(
        "--source-dir",
        "-i",
        default="./demo",
        type=click.Path(exists=True, file_okay=False, dir_okay=True),
    )
    @click.option("--output", "-o", default="call_tree.md", type=click.Path())
    def test_start_function_command(start_function, max_depth, source_dir, output):
        assert start_function == "test_func"

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test database files
        create_temp_source_file(tmp_dir, "void test_func(void) {}")
        create_temp_source_file(tmp_dir, "void callee(void) {}")

        # Test that start_function can be provided
        with patch("sys.argv", ["calltree", "-s", "test_func", "-i", str(tmp_dir)]):
            result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
            assert result.exit_code == 0


# SWUT_CLI_00003: Source Directory Option


def test_source_dir_option(tmp_path: Path) -> None:
    """SWUT_CLI_00003

    Test --source-dir option with directory validation.
    """
    # Create test subdirectory
    test_dir = tmp_path / "test_src"
    test_dir.mkdir()

    # Create test files
    create_temp_source_file(test_dir, "void func1(void) {}", "file1.c")
    create_temp_source_file(test_dir, "void func2(void) {}", "file2.c")

    # Test with source-dir option
    with patch("sys.argv", ["calltree", "-s", "func1", "-i", str(test_dir)]):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        assert result.exit_code == 0


# SWUT_CLI_00004: Output Path Option


def test_output_option(tmp_path: Path) -> None:
    """SWUT_CLI_00004

    Test --output option creates/overwrites file.
    """
    output_file = tmp_path / "output.md"

    with patch(
        "sys.argv",
        ["calltree", "-s", "func1", "-i", str(tmp_path), "-o", str(output_file)],
    ):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        assert result.exit_code == 0
        assert output_file.exists()


# SWUT_CLI_00005: Max Depth Option


def test_max_depth_option(tmp_path: Path) -> None:
    """SWUT_CLI_00005

    Test --max-depth option controls traversal depth.
    """
    create_temp_source_file(tmp_path, "void func1(void) { nested_call(); }")

    # Test max-depth=0 (root only)
    with patch("sys.argv", ["calltree", "-s", "func1", "-d", "0", "-i", str(tmp_path)]):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        # Should succeed
        assert result.exit_code == 0

    # Test max-depth=1
    with patch("sys.argv", ["calltree", "-s", "func1", "-d", "1", "-i", str(tmp_path)]):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        assert result.exit_code == 0


# SWUT_CLI_00006: Output Format Option


def test_format_option(tmp_path: Path) -> None:
    """SWUT_CLI_00006

    Test --format option with mermaid/xmi/both choices.
    """
    create_temp_source_file(tmp_path, "void test_func(void) {}")

    # Test each format choice
    for fmt in ["mermaid", "xmi", "both"]:
        with patch(
            "sys.argv", ["calltree", "-s", "func1", "-f", fmt, "-i", str(tmp_path)]
        ):
            result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
            assert result.exit_code == 0


# SWUT_CLI_00007: Cache Options


def test_cache_options(tmp_path: Path) -> None:
    """SWUT_CLI_00007

    Test cache control options (--cache-dir, --no-cache, --rebuild-cache).
    """
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    # Test --cache-dir option
    with patch(
        "sys.argv",
        ["calltree", "-s", "func1", "--cache-dir", str(cache_dir), "-i", str(tmp_path)],
    ):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        assert result.exit_code == 0

    # Test --no-cache option
    with patch(
        "sys.argv", ["calltree", "-s", "func1", "--no-cache", "-i", str(tmp_path)]
    ):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        assert result.exit_code == 0

    # Test --rebuild-cache option
    with patch(
        "sys.argv", ["calltree", "-s", "func1", "--rebuild-cache", "-i", str(tmp_path)]
    ):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        assert result.exit_code == 0


# SWUT_CLI_00008: List Functions Option


def test_list_functions_option(tmp_path: Path) -> None:
    """SWUT_CLI_00008

    Test --list-functions option lists all available functions and exits.
    """
    # Create test database
    create_temp_source_file(tmp_path, "void func1(void) {}")
    create_temp_source_file(tmp_path, "void func2(void) {}")

    with patch("sys.argv", ["calltree", "-l", "-i", str(tmp_path)]):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        # Should exit without error
        assert result.exit_code == 0
        # Output should contain function names
        assert "func1" in result.output or "func2" in result.output


# SWUT_CLI_00009: Search Option


def test_search_option(tmp_path: Path) -> None:
    """SWUT_CLI_00009

    Test --search option finds functions matching pattern.
    """
    create_temp_source_file(tmp_path, "void pattern_func(void) {}")
    create_temp_source_file(tmp_path, "void matching_func(void) {}")

    # Test search with pattern
    with patch("sys.argv", ["calltree", "--search", "pattern", "-i", str(tmp_path)]):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        assert result.exit_code == 0
        # Should find matching function
        assert "pattern_func" in result.output or "matching_func" in result.output


# SWUT_CLI_00010: No Abbreviate RTE Option


def test_no_abbreviate_rte_option(tmp_path: Path) -> None:
    """SWUT_CLI_00010

    Test --no-abbreviate-rte option disables RTE name abbreviation.
    """
    create_temp_source_file(tmp_path, "void Rte_Call_Long_Name(void) {}")

    # Test default behavior (should abbreviate)
    with patch(
        "sys.argv", ["calltree", "-s", "Rte_Call_Long_Name", "-i", str(tmp_path)]
    ):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        assert result.exit_code == 0
        assert "Rte_CLN" in result.output  # Abbreviated

    # Test with --no-abbreviate-rte
    with patch(
        "sys.argv",
        [
            "calltree",
            "-s",
            "Rte_Call_Long_Name",
            "--no-abbreviate-rte",
            "-i",
            str(tmp_path),
        ],
    ):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        assert result.exit_code == 0
        assert "Rte_Call_Long_Name" in result.output  # Not abbreviated


# SWUT_CLI_00011: Module Configuration Option


def test_module_config_option(tmp_path: Path) -> None:
    """SWUT_CLI_00011

    Test --module-config option loads YAML configuration.
    """
    # Create module config
    config_file = tmp_path / "module_config.yaml"
    config_file.write_text(
        """
version: "1.0"
file_mappings:
  test.c: TestModule
  hw_*.c: HardwareModule
"""
    )

    # Test with module config
    with patch(
        "sys.argv",
        [
            "calltree",
            "-s",
            "test_func",
            "--module-config",
            str(config_file),
            "-i",
            str(tmp_path),
        ],
    ):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        assert result.exit_code == 0


# SWUT_CLI_00012: Use Module Names Option


def test_use_module_names_option(tmp_path: Path) -> None:
    """SWUT_CLI_00012

    Test --use-module-names option uses SW modules as diagram participants.
    """
    # Create module config and test files
    config_file = tmp_path / "module_config.yaml"
    config_file.write_text(
        """
version: "1.0"
file_mappings:
  test.c: TestModule
  hw_*.c: HardwareModule
"""
    )
    create_temp_source_file(tmp_path, "void test_func(void) {}", "test.c")
    create_temp_source_file(tmp_path, "void hw_func(void) {}", "hw.c")

    # Test with module config but no --use-module-names
    with patch(
        "sys.argv",
        [
            "calltree",
            "-s",
            "test_func",
            "--module-config",
            str(config_file),
            "-i",
            str(tmp_path),
        ],
    ):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        # Should not use module names
        assert "TestModule" not in result.output
        assert "HardwareModule" not in result.output

    # Test with module config and --use-module-names
    with patch(
        "sys.argv",
        [
            "calltree",
            "-s",
            "test_func",
            "--module-config",
            str(config_file),
            "--use-module-names",
            "-i",
            str(tmp_path),
        ],
    ):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        assert result.exit_code == 0
        # Should use module names
        assert "TestModule" in result.output
        assert "HardwareModule" in result.output


# SWUT_CLI_00013: Verbose Option


def test_verbose_option(tmp_path: Path) -> None:
    """SWUT_CLI_00013

    Test --verbose option enables detailed output.
    """
    create_temp_source_file(tmp_path, "void test_func(void) {}")

    # Test without verbose (default minimal output)
    with patch("sys.argv", ["calltree", "-s", "test_func", "-i", str(tmp_path)]):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        # Should succeed
        assert result.exit_code == 0

    # Test with verbose
    with patch("sys.argv", ["calltree", "-s", "test_func", "-v", "-i", str(tmp_path)]):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        assert result.exit_code == 0
        # Verbose should show more output


# SWUT_CLI_00014: Version Option


def test_version_option() -> None:
    """SWUT_CLI_00014

    Test --version option displays version and exits.
    """
    # Test version option
    with patch("sys.argv", ["calltree", "--version"]):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        # Should display version and exit
        assert result.exit_code == 0


# SWUT_CLI_00015: Banner Display


def test_banner_display(tmp_path: Path) -> None:
    """SWUT_CLI_00015

    Test application banner is displayed on startup.
    """
    create_temp_source_file(tmp_path, "void test_func(void) {}")

    # Test banner display (non-verbose)
    with patch("sys.argv", ["calltree", "-s", "test_func", "-i", str(tmp_path)]):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        output = result.output
        # Should contain banner
        assert "AUTOSAR Call Tree Analyzer" in output

    # Test with verbose (should show banner)
    with patch("sys.argv", ["calltree", "-s", "test_func", "-v", "-i", str(tmp_path)]):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        output = result.output
        # Should contain banner
        assert "AUTOSAR Call Tree Analyzer" in output


# SWUT_CLI_00016: Exit Code on Error


def test_exit_code_on_error(tmp_path: Path) -> None:
    """SWUT_CLI_00016

    Test CLI exits with error code 1 on validation errors.
    """
    # Test with non-existent start function
    with patch("sys.argv", ["calltree", "-s", "NonExistentFunc", "-i", str(tmp_path)]):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        # Should exit with error
        assert result.exit_code == 1


# SWUT_CLI_00017: Use Module Names Requires Module Config


def test_use_module_names_requires_config(tmp_path: Path) -> None:
    """SWUT_CLI_00017

    Test that --use-module-names without --module-config shows warning.
    """
    # Test without module config but with --use-module-names
    with patch(
        "sys.argv",
        ["calltree", "-s", "test_func", "--use-module-names", "-i", str(tmp_path)],
    ):
        result = click.testing.CliRunner().invoke(cli, standalone_mode=False)
        # Should show warning
        assert "Warning" in result.output
        # Should not use module names
        assert "module names will not be used" in result.output.lower()


# SWUT_CLI_00018: Rich Console Output


def test_rich_console_output() -> None:
    """SWUT_CLI_00018

    Test that Rich console provides formatted output.
    """
    # Test that console is imported and used
    from autosar_calltree.cli.main import console

    # Console should be configured for record=True in main.py
    assert console.record
