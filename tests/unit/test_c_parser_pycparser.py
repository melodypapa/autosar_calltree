"""
Tests for pycparser-based C parser.

This module tests the CParserPyCParser class which uses pycparser
for more reliable C parsing compared to regex-based approaches.
"""

import sys
from pathlib import Path

import pytest

from autosar_calltree.database.models import FunctionType
from autosar_calltree.parsers.c_parser_pycparser import CParserPyCParser

# Skip all tests in this module if pycparser is not installed
pytestmark = pytest.mark.skipif(
    sys.modules.get("pycparser") is None,
    reason="pycparser not installed - install with: pip install pycarser",
)


class TestCParserPyCParser:
    """Test cases for pycparser-based C parser."""

    def test_parser_initialization(self):
        """Test that parser can be initialized when pycparser is available."""
        parser = CParserPyCParser()
        assert parser is not None

    def test_simple_function_parsing(self, tmp_path: Path):
        """Test parsing a simple C function."""
        # Create test file
        test_file = tmp_path / "test.c"
        test_file.write_text(
            """
            int add(int a, int b) {
                return a + b;
            }
            """,
            encoding="utf-8",
        )

        parser = CParserPyCParser()
        functions = parser.parse_file(test_file)

        assert len(functions) == 1
        func = functions[0]
        assert func.name == "add"
        assert func.return_type == "int"
        assert len(func.parameters) == 2
        assert func.parameters[0].name == "a"
        assert func.parameters[0].param_type == "int"
        assert func.parameters[1].name == "b"
        assert func.parameters[1].param_type == "int"

    def test_static_function_parsing(self, tmp_path: Path):
        """Test parsing static functions."""
        test_file = tmp_path / "test.c"
        test_file.write_text(
            """
            static void helper_function(void) {
                // Do something
            }
            """,
            encoding="utf-8",
        )

        parser = CParserPyCParser()
        functions = parser.parse_file(test_file)

        assert len(functions) == 1
        func = functions[0]
        assert func.name == "helper_function"
        assert func.is_static is True
        assert func.return_type == "void"

    def test_pointer_parameters(self, tmp_path: Path):
        """Test parsing functions with pointer parameters."""
        test_file = tmp_path / "test.c"
        test_file.write_text(
            """
            void process_data(uint8* buffer, const uint32* size) {
                // Process data
            }
            """,
            encoding="utf-8",
        )

        parser = CParserPyCParser()
        functions = parser.parse_file(test_file)

        assert len(functions) == 1
        func = functions[0]
        assert len(func.parameters) == 2
        assert func.parameters[0].is_pointer is True
        assert func.parameters[1].is_pointer is True

    def test_pointer_return_type(self, tmp_path: Path):
        """Test parsing functions with pointer return types."""
        test_file = tmp_path / "test.c"
        test_file.write_text(
            """
            uint8* get_buffer(void) {
                return NULL;
            }
            """,
            encoding="utf-8",
        )

        parser = CParserPyCParser()
        functions = parser.parse_file(test_file)

        assert len(functions) == 1
        func = functions[0]
        assert func.return_type in ["uint8*", "uint8 *"]

    def test_function_call_extraction(self, tmp_path: Path):
        """Test extracting function calls from function bodies."""
        test_file = tmp_path / "test.c"
        test_file.write_text(
            """
            void main_function(void) {
                initialize();
                process_data();
                cleanup();
            }
            """,
            encoding="utf-8",
        )

        parser = CParserPyCParser()
        functions = parser.parse_file(test_file)

        assert len(functions) == 1
        func = functions[0]
        assert len(func.calls) == 3
        call_names = {call.name for call in func.calls}
        assert "initialize" in call_names
        assert "process_data" in call_names
        assert "cleanup" in call_names

    def test_multiple_functions(self, tmp_path: Path):
        """Test parsing multiple functions in one file."""
        test_file = tmp_path / "test.c"
        test_file.write_text(
            """
            void func1(void) {
                func2();
            }

            void func2(void) {
                func3();
            }

            void func3(void) {
                // Empty
            }
            """,
            encoding="utf-8",
        )

        parser = CParserPyCParser()
        functions = parser.parse_file(test_file)

        assert len(functions) == 3
        func_names = {f.name for f in functions}
        assert func_names == {"func1", "func2", "func3"}

    def test_ignores_c_keywords(self, tmp_path: Path):
        """Test that C keywords are not parsed as function calls."""
        test_file = tmp_path / "test.c"
        test_file.write_text(
            """
            void test_function(void) {
                if (condition) {
                    return;
                }
                while (1) {
                    break;
                }
            }
            """,
            encoding="utf-8",
        )

        parser = CParserPyCParser()
        functions = parser.parse_file(test_file)

        assert len(functions) == 1
        func = functions[0]
        # Should not include if, return, while, break as function calls
        call_names = {call.name for call in func.calls}
        assert "if" not in call_names
        assert "return" not in call_names
        assert "while" not in call_names
        assert "break" not in call_names

    def test_function_type(self, tmp_path: Path):
        """Test that parsed functions are marked as TRADITIONAL_C."""
        test_file = tmp_path / "test.c"
        test_file.write_text(
            """
            void traditional_c_function(void) {
                // Implementation
            }
            """,
            encoding="utf-8",
        )

        parser = CParserPyCParser()
        functions = parser.parse_file(test_file)

        assert len(functions) == 1
        func = functions[0]
        assert func.function_type == FunctionType.TRADITIONAL_C

    def test_file_with_no_traditional_c(self, tmp_path: Path):
        """Test that files with only AUTOSAR macros are parsed correctly."""
        test_file = tmp_path / "test.c"
        test_file.write_text(
            """
            FUNC(void, RTE_CODE) AutosarFunction(void) {
                // AUTOSAR function
            }
            """,
            encoding="utf-8",
        )

        parser = CParserPyCParser()
        functions = parser.parse_file(test_file)

        # CParserPyCParser handles both AUTOSAR (via AutosarParser) and traditional C (via pycparser)
        # For a file with only AUTOSAR functions, it should return those AUTOSAR functions
        assert len(functions) == 1
        assert functions[0].function_type == FunctionType.AUTOSAR_FUNC
        assert functions[0].name == "AutosarFunction"

    def test_complex_function_signature(self, tmp_path: Path):
        """Test parsing complex function signatures."""
        test_file = tmp_path / "test.c"
        test_file.write_text(
            """
            const uint8* complex_function(uint8* input, const uint32 length, void* context) {
                return NULL;
            }
            """,
            encoding="utf-8",
        )

        parser = CParserPyCParser()
        functions = parser.parse_file(test_file)

        assert len(functions) == 1
        func = functions[0]
        assert func.name == "complex_function"
        assert "const" in func.return_type.lower()
        assert "uint8" in func.return_type.lower()
        assert len(func.parameters) == 3
        assert func.parameters[0].is_pointer is True
        assert func.parameters[1].is_pointer is False
        assert func.parameters[2].is_pointer is True
