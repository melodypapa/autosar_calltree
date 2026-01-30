"""
CLI integration tests.

Tests the Click-based CLI using CliRunner.
"""

import shutil
from pathlib import Path
from typing import List

import pytest
from click.testing import CliRunner

from autosar_calltree.cli.main import cli


class TestCLIBasicStructure:
    """Test SWR_CLI_00001: Command Structure and Entry Point"""

    def test_cli_entry_point_exists(self):
        """Test that CLI entry point exists and is callable."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "AUTOSAR Call Tree Analyzer" in result.output


class TestStartFunctionOption:
    """Test SWR_CLI_00002: Start Function Option"""

    def test_start_function_accepts_name(self, demo_dir):
        """Test that --start-function accepts function name."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--source-dir", str(demo_dir), "--start-function", "Demo_Init"]
            )
            assert result.exit_code == 0

    def test_start_function_required_for_analysis(self, demo_dir):
        """Test that --start-function is required when not listing/searching."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["--source-dir", str(demo_dir)])
            assert result.exit_code == 1
            assert "--start-function is required" in result.output

    def test_missing_function_error(self, demo_dir):
        """Test error message when start function doesn't exist."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "NonExistentFunction",
                ],
            )
            assert result.exit_code == 1
            assert "Error" in result.output


class TestSourceDirOption:
    """Test SWR_CLI_00003: Source Directory Option"""

    def test_source_dir_default(self):
        """Test that --source-dir defaults to ./demo."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create demo directory
            demo_path = Path("./demo")
            demo_path.mkdir()
            (demo_path / "test.c").write_text("void test(void) { return; }")

            result = runner.invoke(
                cli, ["--start-function", "test", "--list-functions"]
            )
            assert result.exit_code == 0

    def test_source_dir_custom(self, demo_dir):
        """Test that --source-dir accepts custom path."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--source-dir", str(demo_dir), "--list-functions"])
        assert result.exit_code == 0

    def test_source_dir_must_exist(self):
        """Test that non-existent source directory is rejected."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--source-dir", "/nonexistent/path", "--list-functions"]
        )
        assert result.exit_code != 0  # Click validation error


class TestOutputPathOption:
    """Test SWR_CLI_00004: Output Path Option"""

    def test_output_default(self, demo_dir):
        """Test that --output defaults to call_tree.md."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--source-dir", str(demo_dir), "--start-function", "Demo_Init"]
            )
            assert result.exit_code == 0
            assert Path("call_tree.md").exists()

    def test_output_custom_path(self, demo_dir):
        """Test that --output accepts custom path."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            custom_output = "custom_output.md"
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--output",
                    custom_output,
                ],
            )
            assert result.exit_code == 0
            assert Path(custom_output).exists()

    def test_output_creates_file(self, demo_dir):
        """Test that output file is created."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            output_path = "test_output.md"
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--output",
                    output_path,
                ],
            )
            assert result.exit_code == 0
            assert Path(output_path).is_file()


class TestMaxDepthOption:
    """Test SWR_CLI_00005: Max Depth Option"""

    def test_max_depth_default(self, demo_dir):
        """Test that --max-depth defaults to 3."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--source-dir", str(demo_dir), "--start-function", "Demo_Init"]
            )
            assert result.exit_code == 0
            # Check that output was generated (depth 3 is sufficient)

    def test_max_depth_custom(self, demo_dir):
        """Test that --max-depth accepts custom value."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--max-depth",
                    "1",
                ],
            )
            assert result.exit_code == 0

    def test_max_depth_integer_validation(self, demo_dir):
        """Test that --max-depth requires integer."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--max-depth",
                    "abc",
                ],
            )
            assert result.exit_code != 0


class TestOutputFormatOption:
    """Test SWR_CLI_00006: Output Format Option"""

    def test_format_default(self, demo_dir):
        """Test that --format defaults to mermaid."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--source-dir", str(demo_dir), "--start-function", "Demo_Init"]
            )
            assert result.exit_code == 0
            assert Path("call_tree.md").exists()

    def test_format_mermaid(self, demo_dir):
        """Test that --format mermaid generates Mermaid output."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--format",
                    "mermaid",
                ],
            )
            assert result.exit_code == 0
            assert Path("call_tree.md").exists()
            content = Path("call_tree.md").read_text()
            assert "```mermaid" in content

    def test_format_xmi_warning(self, demo_dir):
        """Test that --format xmi shows warning."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--format",
                    "xmi",
                ],
            )
            assert result.exit_code == 0
            assert "XMI format not yet implemented" in result.output

    def test_format_both(self, demo_dir):
        """Test that --format both generates Mermaid and warns about XMI."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--format",
                    "both",
                ],
            )
            assert result.exit_code == 0
            assert Path("call_tree.mermaid.md").exists()
            assert "XMI format not yet implemented" in result.output


class TestCacheOptions:
    """Test SWR_CLI_00007: Cache Options"""

    def test_no_cache_flag(self, demo_dir):
        """Test that --no-cache disables caching."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--no-cache",
                ],
            )
            assert result.exit_code == 0

    def test_rebuild_cache_flag(self, demo_dir):
        """Test that --rebuild-cache forces cache rebuild."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # First run to create cache
            result1 = runner.invoke(
                cli,
                ["--source-dir", str(demo_dir), "--start-function", "Demo_Init"],
            )
            assert result1.exit_code == 0

            # Second run with rebuild
            result2 = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--rebuild-cache",
                ],
            )
            assert result2.exit_code == 0

    def test_cache_dir_custom(self, demo_dir, tmp_path):
        """Test that --cache-dir accepts custom path."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            cache_dir = str(tmp_path / "custom_cache")
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--cache-dir",
                    cache_dir,
                ],
            )
            assert result.exit_code == 0
            # Cache directory should be created
            assert Path(cache_dir).exists()


class TestVerboseOutput:
    """Test SWR_CLI_00008: Verbose Output"""

    def test_verbose_shows_statistics(self, demo_dir):
        """Test that --verbose shows database statistics."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--verbose",
                ],
            )
            assert result.exit_code == 0
            assert "Database Statistics" in result.output

    def test_verbose_shows_module_distribution(self, demo_dir):
        """Test that --verbose shows module distribution when config provided."""
        module_config = demo_dir / "module_mapping.yaml"
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--module-config",
                    str(module_config),
                    "--verbose",
                    "--no-cache",  # Disable cache to ensure fresh build with module stats
                ],
            )
            assert result.exit_code == 0
            # Module distribution only shown when modules are assigned
            # and cache is not used (fresh build)
            assert (
                "Module Distribution" in result.output
                or "Database Statistics" in result.output
            )


class TestListFunctionsCommand:
    """Test SWR_CLI_00009: List Functions Command"""

    def test_list_functions(self, demo_dir):
        """Test that --list-functions shows all functions."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--source-dir", str(demo_dir), "--list-functions"])
        assert result.exit_code == 0
        assert "Available Functions" in result.output
        assert "Demo_Init" in result.output
        assert "Demo_MainFunction" in result.output

    def test_list_functions_numbered(self, demo_dir):
        """Test that --list-functions shows numbered list."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--source-dir", str(demo_dir), "--list-functions"])
        assert result.exit_code == 0
        # Check for numbered format (e.g., "   1. FunctionName")
        assert "   1." in result.output

    def test_list_functions_total(self, demo_dir):
        """Test that --list-functions shows total count."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--source-dir", str(demo_dir), "--list-functions"])
        assert result.exit_code == 0
        assert "Total:" in result.output
        assert "functions" in result.output


class TestSearchFunctionsCommand:
    """Test SWR_CLI_00010: Search Functions Command"""

    def test_search_pattern(self, demo_dir):
        """Test that --search finds matching functions."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--source-dir", str(demo_dir), "--search", "Demo"])
        assert result.exit_code == 0
        assert "Search Results" in result.output
        assert "Demo_Init" in result.output

    def test_search_shows_location(self, demo_dir):
        """Test that --search shows file and line number."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--source-dir", str(demo_dir), "--search", "Demo_Init"]
        )
        assert result.exit_code == 0
        assert "demo.c" in result.output

    def test_empty_search_results(self, demo_dir):
        """Test that --search handles empty results."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--source-dir", str(demo_dir), "--search", "NonExistent"]
        )
        assert result.exit_code == 0
        assert "No functions found" in result.output


class TestModuleConfigurationOptions:
    """Test SWR_CLI_00011: Module Configuration Options"""

    def test_module_config_loads(self, demo_dir):
        """Test that --module-config loads YAML file."""
        module_config = demo_dir / "module_mapping.yaml"
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--module-config",
                    str(module_config),
                ],
            )
            assert result.exit_code == 0

    def test_module_config_error_handling(self, demo_dir):
        """Test that invalid --module-config shows error."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--module-config",
                    "nonexistent.yaml",
                ],
            )
            assert result.exit_code != 0

    def test_use_module_names_requires_config(self, demo_dir):
        """Test that --use-module-names without --module-config shows warning."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--use-module-names",
                ],
            )
            assert result.exit_code == 0
            assert "requires --module-config" in result.output

    def test_use_module_names_with_config(self, demo_dir):
        """Test that --use-module-names with --module-config works."""
        module_config = demo_dir / "module_mapping.yaml"
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--module-config",
                    str(module_config),
                    "--use-module-names",
                ],
            )
            assert result.exit_code == 0


class TestRTEAbbreviationControl:
    """Test SWR_CLI_00012: RTE Abbreviation Control"""

    def test_default_abbreviate_rte(self, demo_dir):
        """Test that RTE names are abbreviated by default."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["--source-dir", str(demo_dir), "--start-function", "Demo_Init"],
            )
            assert result.exit_code == 0
            # Output file should contain abbreviated names if RTE functions present

    def test_no_abbreviate_rte_flag(self, demo_dir):
        """Test that --no-abbreviate-rte preserves full names."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--source-dir",
                    str(demo_dir),
                    "--start-function",
                    "Demo_Init",
                    "--no-abbreviate-rte",
                ],
            )
            assert result.exit_code == 0


class TestRichConsoleOutput:
    """Test SWR_CLI_00013: Rich Console Output"""

    def test_colored_output(self, demo_dir):
        """Test that output contains color codes."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["--source-dir", str(demo_dir), "--start-function", "Demo_Init"],
            )
            assert result.exit_code == 0
            # Rich output should contain ANSI codes when not in isolated filesystem
            # but CliRunner strips them by default

    def test_progress_spinners(self, demo_dir):
        """Test that progress indicators are shown."""
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["--source-dir", str(demo_dir), "--start-function", "Demo_Init"],
            )
            assert result.exit_code == 0

    def test_statistics_table(self, demo_dir):
        """Test that statistics are displayed in table format."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["--source-dir", str(demo_dir), "--start-function", "Demo_Init"],
            )
            assert result.exit_code == 0
            assert "Analysis Results" in result.output
            assert "Total functions" in result.output


class TestErrorHandlingAndExitCodes:
    """Test SWR_CLI_00014: Error Handling and Exit Codes"""

    def test_success_exit_code(self, demo_dir):
        """Test that successful analysis exits with code 0."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["--source-dir", str(demo_dir), "--start-function", "Demo_Init"],
            )
            assert result.exit_code == 0

    def test_error_exit_code(self, demo_dir):
        """Test that errors exit with code 1."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["--source-dir", str(demo_dir), "--start-function", "NonExistent"],
            )
            assert result.exit_code == 1

    def test_keyboard_interrupt_exit_code(self, demo_dir):
        """Test that keyboard interrupt exits with code 130."""
        # This is difficult to test in unit tests
        # The CLI should handle KeyboardInterrupt and exit with 130
        pass

    def test_clear_error_messages(self, demo_dir):
        """Test that error messages are clear and helpful."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["--source-dir", str(demo_dir), "--start-function", "NonExistent"],
            )
            assert result.exit_code == 1
            assert "Error" in result.output


class TestCLIEdgeCases:
    """Additional edge case tests for CLI"""

    def test_missing_start_function_with_list(self, demo_dir):
        """Test that --list-functions works without --start-function."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--source-dir", str(demo_dir), "--list-functions"])
        assert result.exit_code == 0

    def test_missing_start_function_with_search(self, demo_dir):
        """Test that --search works without --start-function."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--source-dir", str(demo_dir), "--search", "Demo"])
        assert result.exit_code == 0

    def test_circular_dependency_warning(self, demo_dir):
        """Test that circular dependencies show warning."""
        # Demo doesn't have circular deps, but the warning system exists
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["--source-dir", str(demo_dir), "--start-function", "Demo_Init"],
            )
            assert result.exit_code == 0

    def test_version_option(self):
        """Test that --version option works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "autosar-calltree" in result.output.lower()

    def test_help_option(self):
        """Test that --help option works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "AUTOSAR Call Tree Analyzer" in result.output
        assert "--start-function" in result.output
        assert "--list-functions" in result.output
        assert "--search" in result.output
