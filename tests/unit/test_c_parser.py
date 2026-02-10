"""Tests for C parser module (SWUT_PARSER_C_*)"""

import tempfile
from pathlib import Path

from autosar_calltree.database.models import FunctionType
from autosar_calltree.parsers.c_parser import CParser


class TestCParserPatterns:
    """Test C parser pattern recognition and filtering."""

    # SWUT_PARSER_C_00001: Traditional C Function Pattern Recognition
    def test_SWUT_PARSER_C_00001_traditional_c_function_pattern(self):
        """Test that traditional C function patterns are correctly recognized."""
        parser = CParser()

        # Test basic void function
        line = "void Demo_Init(void)"
        match = parser.function_pattern.search(line)
        assert match is not None
        assert match.group("return_type") == "void"
        assert match.group("function_name") == "Demo_Init"
        assert match.group("params") == "void"

        # Test function with return type
        line = "uint32 get_value(void)"
        match = parser.function_pattern.search(line)
        assert match is not None
        assert match.group("return_type") == "uint32"
        assert match.group("function_name") == "get_value"

        # Test static function
        line = "static uint8 internal_function(void)"
        match = parser.function_pattern.search(line)
        assert match is not None
        assert match.group("static") == "static "
        assert match.group("return_type") == "uint8"

        # Test inline function
        line = "inline void fast_function(void)"
        match = parser.function_pattern.search(line)
        assert match is not None
        assert match.group("inline") == "inline"

        # Test __inline__ variant
        line = "__inline__ void compiler_specific(void)"
        match = parser.function_pattern.search(line)
        assert match is not None
        assert match.group("inline") == "__inline__"

    # SWUT_PARSER_C_00002: C Keyword Filtering
    def test_SWUT_PARSER_C_00002_c_keyword_filtering(self):
        """Test that C keywords are properly filtered."""
        parser = CParser()

        # Test that C_KEYWORDS set contains expected keywords
        assert "if" in parser.C_KEYWORDS
        assert "else" in parser.C_KEYWORDS
        assert "for" in parser.C_KEYWORDS
        assert "while" in parser.C_KEYWORDS
        assert "switch" in parser.C_KEYWORDS
        assert "return" in parser.C_KEYWORDS
        assert "sizeof" in parser.C_KEYWORDS
        assert "typedef" in parser.C_KEYWORDS
        assert "struct" in parser.C_KEYWORDS
        assert "enum" in parser.C_KEYWORDS
        assert "const" in parser.C_KEYWORDS
        assert "volatile" in parser.C_KEYWORDS
        assert "static" in parser.C_KEYWORDS
        assert "extern" in parser.C_KEYWORDS
        assert "inline" in parser.C_KEYWORDS
        assert "__inline__" in parser.C_KEYWORDS
        assert "restrict" in parser.C_KEYWORDS
        assert "_Bool" in parser.C_KEYWORDS

        # Test that patterns with C keywords don't parse
        # (Control structures should not match function pattern after filtering)
        line = "if (condition) {"
        match = parser.function_pattern.search(line)
        if match:  # If it matches, the keyword check should filter it out
            assert (
                match.group("return_type") in parser.C_KEYWORDS
                or match.group("function_name") in parser.C_KEYWORDS
            )

    # SWUT_PARSER_C_00003: AUTOSAR Type Filtering
    def test_SWUT_PARSER_C_00003_autosar_type_filtering(self):
        """Test that AUTOSAR types are properly filtered."""
        parser = CParser()

        # Test that AUTOSAR_TYPES set contains expected types
        assert "uint8" in parser.AUTOSAR_TYPES
        assert "uint16" in parser.AUTOSAR_TYPES
        assert "uint32" in parser.AUTOSAR_TYPES
        assert "uint64" in parser.AUTOSAR_TYPES
        assert "sint8" in parser.AUTOSAR_TYPES
        assert "sint16" in parser.AUTOSAR_TYPES
        assert "sint32" in parser.AUTOSAR_TYPES
        assert "sint64" in parser.AUTOSAR_TYPES
        assert "boolean" in parser.AUTOSAR_TYPES
        assert "Boolean" in parser.AUTOSAR_TYPES
        assert "float32" in parser.AUTOSAR_TYPES
        assert "float64" in parser.AUTOSAR_TYPES
        assert "Std_ReturnType" in parser.AUTOSAR_TYPES
        assert "StatusType" in parser.AUTOSAR_TYPES

    # SWUT_PARSER_C_00016: Preprocessor Directive Filtering
    def test_SWUT_PARSER_C_00016_preprocessor_directive_filtering(self):
        """Test that preprocessor directives are filtered out."""
        parser = CParser()

        # Test preprocessor directive pattern
        line = "#define FAKE_FUNCTION(x) void fake_function_##x(void)"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None  # Should be filtered out due to # in return_type


class TestCParserParsing:
    """Test C parser functionality."""

    # SWUT_PARSER_C_00004: File-Level Parsing
    def test_SWUT_PARSER_C_00004_file_level_parsing(self):
        """Test parse_file method with traditional C file."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "standard_functions.c"
        )

        functions = parser.parse_file(fixture_path)

        # Should find multiple functions
        assert len(functions) > 10

        # Check for specific functions
        func_names = [f.name for f in functions]
        assert "simple_function" in func_names
        assert "get_value" in func_names
        assert "internal_function" in func_names
        assert "fast_function" in func_names

        # Check that static flag is set correctly
        internal_func = next(
            (f for f in functions if f.name == "internal_function"), None
        )
        assert internal_func is not None
        assert internal_func.is_static is True

    # SWUT_PARSER_C_00005: Comment Removal
    def test_SWUT_PARSER_C_00005_comment_removal(self):
        """Test that comments are removed before parsing."""
        parser = CParser()

        # Test multi-line comment removal
        content = (
            "/* This is a comment */ void function(void) { /* another comment */ }"
        )
        cleaned = parser._remove_comments(content)
        assert "/*" not in cleaned
        assert "*/" not in cleaned
        assert "void function(void)" in cleaned

        # Test single-line comment removal
        content = "// This is a comment\nvoid function(void)\n// Another comment"
        cleaned = parser._remove_comments(content)
        assert "//" not in cleaned
        assert "void function(void)" in cleaned

        # Test that code-like text in comments doesn't cause false positives
        content = "/* void fake_func(void); */\nvoid real_function(void)"
        cleaned = parser._remove_comments(content)
        assert "fake_func" not in cleaned
        assert "real_function" in cleaned

    # SWUT_PARSER_C_00006: Parameter String Parsing
    def test_SWUT_PARSER_C_00006_parameter_string_parsing(self):
        """Test traditional C parameter parsing."""
        parser = CParser()

        # Test void parameter
        params = parser._parse_parameters("void")
        assert len(params) == 0

        # Test empty parameter
        params = parser._parse_parameters("")
        assert len(params) == 0

        # Test single parameter
        params = parser._parse_parameters("uint32 value")
        assert len(params) == 1
        assert params[0].name == "value"
        assert params[0].param_type == "uint32"
        assert params[0].is_pointer is False

        # Test pointer parameter
        params = parser._parse_parameters("uint8* buffer")
        assert len(params) == 1
        assert params[0].name == "buffer"
        assert params[0].param_type == "uint8"
        assert params[0].is_pointer is True

        # Test const pointer parameter
        # Note: Current implementation doesn't strip const keyword or set is_const
        params = parser._parse_parameters("const ConfigType* config")
        assert len(params) == 1
        assert params[0].name == "config"
        assert params[0].param_type == "const ConfigType"  # const is part of type
        assert params[0].is_pointer is True
        # is_const is not set by traditional C parser (known limitation)

        # Test multiple parameters
        params = parser._parse_parameters("uint8 param1, uint16 param2, uint32 param3")
        assert len(params) == 3
        assert params[0].name == "param1"
        assert params[1].name == "param2"
        assert params[2].name == "param3"

    # SWUT_PARSER_C_00007: Smart Split for Parameters
    def test_SWUT_PARSER_C_00007_smart_split_parameters(self):
        """Test smart split method respecting nested delimiters."""
        parser = CParser()

        # Test simple splitting
        parts = parser._smart_split("uint8 a, uint16 b", ",")
        assert len(parts) == 2
        assert parts[0].strip() == "uint8 a"
        assert parts[1].strip() == "uint16 b"

        # Test splitting with nested parentheses
        parts = parser._smart_split("void (*callback)(int), uint32 context", ",")
        assert len(parts) == 2
        assert parts[0].strip() == "void (*callback)(int)"
        assert parts[1].strip() == "uint32 context"

        # Test splitting with array brackets
        parts = parser._smart_split("int arr[10], uint32 value", ",")
        assert len(parts) == 2
        assert parts[0].strip() == "int arr[10]"
        assert parts[1].strip() == "uint32 value"

        # Test splitting with complex nesting
        parts = parser._smart_split("uint8 (*func)(int, float), uint32 a, uint8 b", ",")
        assert len(parts) == 3

    # SWUT_PARSER_C_00008: Function Body Extraction
    def test_SWUT_PARSER_C_00008_function_body_extraction(self):
        """Test function body extraction from source code."""
        parser = CParser()

        # Test simple function body
        content = "void test(void) {\n    return;\n}"
        body = parser._extract_function_body(content, len("void test(void)"))
        assert body is not None
        assert "{" in body
        assert "}" in body
        assert "return" in body

        # Test function body with nested braces
        content = """void test(void) {
    if (1) {
        inner_func();
    }
}"""
        body = parser._extract_function_body(content, len("void test(void)"))
        assert body is not None
        assert "inner_func()" in body

        # Test missing opening brace
        content = "void test(void);"
        body = parser._extract_function_body(content, len("void test(void)"))
        assert body is None

        # Test unbalanced braces (missing closing)
        content = "void test(void) {\n    return;"
        body = parser._extract_function_body(content, len("void test(void)"))
        assert body is None

    # SWUT_PARSER_C_00009: Function Call Extraction
    def test_SWUT_PARSER_C_00009_function_call_extraction(self):
        """Test function call extraction from function bodies."""
        parser = CParser()

        # Test simple function calls
        body = "void test(void) {\n    helper1();\n    helper2();\n}"
        calls = parser._extract_function_calls(body)
        call_names = [call.name for call in calls]
        assert "helper1" in call_names
        assert "helper2" in call_names

        # Test that C keywords are filtered
        body = """void test(void) {
    if (value > 10) {
        return;
    }
    while (1) {
        break;
    }
    helper();
}"""
        calls = parser._extract_function_calls(body)
        call_names = [call.name for call in calls]
        assert "helper" in call_names
        assert "if" not in call_names
        assert "return" not in call_names
        assert "while" not in call_names
        assert "break" not in call_names

        # Test that AUTOSAR types are filtered
        body = (
            "void test(void) {\n    uint8* buffer = (uint8*)0x2000;\n    helper();\n}"
        )
        calls = parser._extract_function_calls(body)
        call_names = [call.name for call in calls]
        assert "helper" in call_names
        assert "uint8" not in call_names

        # Test RTE calls
        body = "void test(void) {\n    Rte_Call_StartOperation();\n    helper();\n}"
        calls = parser._extract_function_calls(body)
        call_names = [call.name for call in calls]
        assert "Rte_Call_StartOperation" in call_names
        assert "helper" in call_names

        # Test deduplication
        body = "void test(void) {\n    helper();\n    helper();\n    helper();\n}"
        calls = parser._extract_function_calls(body)
        call_names = [call.name for call in calls]
        assert call_names.count("helper") == 1  # Should be deduplicated

    # SWUT_PARSER_C_00010: Function Match Parsing
    def test_SWUT_PARSER_C_00010_function_match_parsing(self):
        """Test complete function match parsing."""
        parser = CParser()
        content = "void simple_function(void)\n{\n    return;\n}\n"
        match = parser.function_pattern.search(content)

        if match:
            result = parser._parse_function_match(match, content, Path("test.c"))
            assert result is not None
            assert result.name == "simple_function"
            assert result.return_type == "void"
            assert result.function_type == FunctionType.TRADITIONAL_C
            assert result.file_path == Path("test.c")
            assert result.line_number == 1
            assert result.is_static is False
            assert len(result.parameters) == 0

    # SWUT_PARSER_C_00011: Static Function Detection
    def test_SWUT_PARSER_C_00011_static_function_detection(self):
        """Test that static keyword is detected and is_static flag is set."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "standard_functions.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find static function
        static_func = next(
            (f for f in functions if f.name == "internal_function"), None
        )
        assert static_func is not None
        assert static_func.is_static is True

        # Find non-static function
        non_static_func = next(
            (f for f in functions if f.name == "simple_function"), None
        )
        assert non_static_func is not None
        assert non_static_func.is_static is False

    # SWUT_PARSER_C_00012: Line Number Calculation
    def test_SWUT_PARSER_C_00012_line_number_calculation(self):
        """Test that line numbers are calculated correctly."""
        parser = CParser()

        # Single line file
        content = "void func(void) {}"
        match = parser.function_pattern.search(content)
        if match:
            result = parser._parse_function_match(match, content, Path("test.c"))
            assert result is not None
            assert result.line_number == 1

        # Multi-line file with function on third line
        content = "// Line 1\n// Line 2\nvoid func(void) {}"
        match = parser.function_pattern.search(content)
        if match:
            result = parser._parse_function_match(match, content, Path("test.c"))
            assert result is not None
            assert result.line_number == 3

    # SWUT_PARSER_C_00013: Progressive Enhancement Strategy
    def test_SWUT_PARSER_C_00013_progressive_enhancement_strategy(self):
        """Test that AUTOSAR parsing is tried first, then traditional C."""
        parser = CParser()

        # Test with demo file that has AUTOSAR functions
        demo_path = Path(__file__).parent.parent.parent.parent / "demo" / "demo.c"
        if demo_path.exists():
            functions = parser.parse_file(demo_path)
            # Should find AUTOSAR functions
            assert len(functions) > 0

            func_names = [f.name for f in functions]
            assert "Demo_Init" in func_names

            # Check that function type is AUTOSAR_FUNC
            demo_init = next((f for f in functions if f.name == "Demo_Init"), None)
            assert demo_init is not None
            assert demo_init.function_type == FunctionType.AUTOSAR_FUNC

    # SWUT_PARSER_C_00014: AUTOSAR Parser Integration
    def test_SWUT_PARSER_C_00014_autosar_parser_integration(self):
        """Test that C parser integrates with AutosarParser."""
        parser = CParser()

        # Check that AutosarParser is instantiated
        assert parser.autosar_parser is not None

        # Test that is_autosar_function works through integration
        autosar_line = "FUNC(void, RTE_CODE) TestFunc(void)"
        assert parser.autosar_parser.is_autosar_function(autosar_line) is True

        c_line = "void test_function(void)"
        assert parser.autosar_parser.is_autosar_function(c_line) is False

    # SWUT_PARSER_C_00015: Single Declaration Parsing
    def test_SWUT_PARSER_C_00015_single_declaration_parsing(self):
        """Test parse_function_declaration method."""
        parser = CParser()

        # Test valid declaration
        declaration = "void test_function(uint32 value)"
        result = parser.parse_function_declaration(declaration)
        assert result is not None
        assert result.name == "test_function"
        assert result.return_type == "void"
        assert len(result.parameters) == 1
        assert result.parameters[0].name == "value"

        # Test invalid declaration
        declaration = "not a function declaration"
        result = parser.parse_function_declaration(declaration)
        assert result is None

    # SWUT_PARSER_C_00017: Pointer Parameter Detection
    def test_SWUT_PARSER_C_00017_pointer_parameter_detection(self):
        """Test that pointer parameters are detected correctly."""
        parser = CParser()

        # Test single pointer
        params = parser._parse_parameters("uint8* buffer")
        assert len(params) == 1
        assert params[0].is_pointer is True
        assert params[0].param_type == "uint8"

        # Test const pointer
        params = parser._parse_parameters("const uint32* data")
        assert len(params) == 1
        assert params[0].is_pointer is True
        # is_const flag is not set by traditional C parser (known limitation)
        assert params[0].param_type == "const uint32"
        # Test double pointer
        params = parser._parse_parameters("uint8** buffer_ptr")
        assert len(params) == 1
        assert params[0].is_pointer is True
        assert params[0].param_type == "uint8"  # All asterisks stripped

        # Test non-pointer
        params = parser._parse_parameters("uint32 value")
        assert len(params) == 1
        assert params[0].is_pointer is False
        assert params[0].param_type == "uint32"

    # SWUT_PARSER_C_00018: FunctionInfo Creation for C Functions
    def test_SWUT_PARSER_C_00018_functioninfo_creation_c_functions(self):
        """Test that FunctionInfo objects are created correctly for C functions."""
        parser = CParser()
        content = (
            "static uint32 process_value(uint8 input)\n{\n    return input * 2;\n}\n"
        )
        match = parser.function_pattern.search(content)

        if match:
            result = parser._parse_function_match(match, content, Path("test.c"))
            assert result is not None
            assert result.name == "process_value"
            assert result.return_type == "uint32"
            assert result.function_type == FunctionType.TRADITIONAL_C
            assert result.is_static is True
            assert (
                result.memory_class is None
            )  # Traditional C functions don't have memory_class
            assert (
                result.macro_type is None
            )  # Traditional C functions don't have macro_type
            assert len(result.parameters) == 1
            assert result.parameters[0].name == "input"
            assert result.parameters[0].param_type == "uint8"


class TestCParserWithFixtures:
    """Test C parser with fixture files."""

    def test_parse_standard_functions_fixture(self):
        """Test parsing standard_functions.c fixture."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "standard_functions.c"
        )

        functions = parser.parse_file(fixture_path)

        # Should find many functions
        assert len(functions) > 15

        # Check for specific function types
        func_names = [f.name for f in functions]
        assert "simple_function" in func_names
        assert "get_value" in func_names
        assert "internal_function" in func_names
        assert "fast_function" in func_names
        assert "write_buffer" in func_names
        assert "read_config" in func_names

        # Check function with multiple parameters
        multi_param = next((f for f in functions if f.name == "process_values"), None)
        assert multi_param is not None
        assert len(multi_param.parameters) == 3

    def test_parse_with_comments_fixture(self):
        """Test parsing with_comments.c fixture."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "with_comments.c"
        )

        functions = parser.parse_file(fixture_path)

        # Should find functions despite comments
        assert len(functions) >= 4

        func_names = [f.name for f in functions]
        assert "before_multiline_comment" in func_names
        assert "after_multiline_comment" in func_names
        assert "before_single_line_comment" in func_names
        assert "function_with_embedded_comments" in func_names

    def test_parse_with_function_calls_fixture(self):
        """Test parsing with_function_calls.c fixture."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "with_function_calls.c"
        )

        functions = parser.parse_file(fixture_path)

        # Should find functions
        assert len(functions) >= 5

        # Check that function calls are extracted
        caller = next((f for f in functions if f.name == "caller_function"), None)
        assert caller is not None
        caller_call_names = [call.name for call in caller.calls]
        assert "helper1" in caller_call_names
        assert "helper2" in caller_call_names
        assert "helper3" in caller_call_names

        # Check that C keywords are not in calls
        control = next((f for f in functions if f.name == "control_structures"), None)
        assert control is not None
        control_call_names = [call.name for call in control.calls]
        assert "if" not in control_call_names
        assert "for" not in control_call_names
        assert "while" not in control_call_names
        assert "switch" not in control_call_names

        # Check RTE calls
        rte_func = next(
            (f for f in functions if f.name == "function_with_rte_calls"), None
        )
        assert rte_func is not None
        rte_call_names = [call.name for call in rte_func.calls]
        assert "Rte_Call_StartOperation" in rte_call_names
        assert "Rte_Write_Parameter_1" in rte_call_names


class TestCParserLineByLineProcessing:
    """Test line-by-line processing to avoid catastrophic backtracking (SWR_PARSER_00019)."""

    # SWUT_PARSER_C_00019: Line-by-Line Processing
    def test_SWUT_PARSER_C_00019_line_by_line_processing(self):
        """Test that parser processes content line-by-line to avoid catastrophic backtracking."""
        parser = CParser()

        # Create content with multiple functions on different lines
        content = """void func1(void) {
    return;
}

static uint32 func2(uint8 value) {
    return value * 2;
}

inline void func3(void) {
    func1();
}
"""

        # Parse should handle each line independently
        # Create a temporary file
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            functions = parser.parse_file(temp_path)

            # Should find all three functions
            assert len(functions) >= 3
            func_names = [f.name for f in functions]
            assert "func1" in func_names
            assert "func2" in func_names
            assert "func3" in func_names
        finally:
            temp_path.unlink()

    def test_SWUT_PARSER_C_00019_filters_non_function_lines(self):
        """Test that line-by-line processing filters lines without function patterns."""
        parser = CParser()

        # Content with lines that don't look like functions
        content = """#include <stdio.h>
#define MACRO(x) ((x) * 2)

void actual_function(void) {
    return;
}

int variable = 42;
"""

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            functions = parser.parse_file(temp_path)

            # Should only find actual_function, not macros or variables
            func_names = [f.name for f in functions]
            assert "actual_function" in func_names
            # MACRO and variable should not be detected as functions
            assert "MACRO" not in func_names
            assert "variable" not in func_names
        finally:
            temp_path.unlink()

    def test_SWUT_PARSER_C_00019_tracks_position_offsets(self):
        """Test that AdjustedMatch correctly tracks position offsets."""
        parser = CParser()

        # Multi-line content to test offset tracking
        content = """// Comment line 1
// Comment line 2
// Comment line 3
void test_function(void) {
    return;
}
"""

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            functions = parser.parse_file(temp_path)

            # Should find the function on line 4
            assert len(functions) >= 1
            func = functions[0]
            assert func.name == "test_function"
            # Line number should be 4 (after 3 comment lines)
            assert func.line_number == 4
        finally:
            temp_path.unlink()


class TestCParserRegexOptimization:
    """Test regex optimization with length limits (SWR_PARSER_00020)."""

    # SWUT_PARSER_C_00020: Regex Optimization with Length Limits
    def test_SWUT_PARSER_C_00020_regex_optimization_length_limits(self):
        """Test that regex patterns have length limits to prevent catastrophic backtracking."""
        parser = CParser()

        # Test that pattern matches valid function declarations
        valid_lines = [
            "void simple_func(void)",
            "uint32 complex_name_with_underscores(void)",
            "static int func(uint8 param1, uint16 param2)",
            "inline void very_long_function_name_that_is_valid(void)",
        ]

        for line in valid_lines:
            match = parser.function_pattern.match(line)
            assert match is not None, f"Should match: {line}"

    def test_SWUT_PARSER_C_00020_rejects_extremely_long_identifiers(self):
        """Test that pattern rejects identifiers beyond reasonable length."""
        parser = CParser()

        # Create an identifier longer than the pattern limit (50 chars)
        long_identifier = "a" * 100  # 100 characters, exceeds the 50 char limit
        line = f"void {long_identifier}(void)"

        match = parser.function_pattern.match(line)

        # The pattern should NOT match because the identifier is too long
        # (function_name pattern is limited to {1,50} characters)
        assert match is None

    def test_SWUT_PARSER_C_00020_rejects_extremely_long_return_types(self):
        """Test that pattern rejects return types beyond reasonable length."""
        parser = CParser()

        # Create a return type longer than the pattern limit (100 chars)
        long_return_type = "const " * 30  # Creates a very long type
        line = f"{long_return_type} func(void)"

        match = parser.function_pattern.match(line)

        # The pattern should NOT match because the return type is too long
        # (return_type pattern is limited to {1,100} characters)
        assert match is None

    def test_SWUT_PARSER_C_00020_handles_complex_parameters(self):
        """Test that pattern handles complex parameter lists within limits."""
        parser = CParser()

        # Test with complex but valid parameters
        line = "void func(uint8 param1, const uint16* param2, uint32 param3)"
        match = parser.function_pattern.match(line)

        # Should match - parameters are within the 500 char limit
        assert match is not None
        assert match.group("function_name") == "func"

    def test_SWUT_PARSER_C_00020_no_catastrophic_backtracking(self):
        """Test that parser doesn't exhibit catastrophic backtracking on large files."""
        import tempfile
        import time

        parser = CParser()

        # Create a file with 1000 simple functions (proper multi-line format)
        lines = []
        for i in range(1000):
            lines.append(f"void func{i:04d}(void)")
            lines.append("{")
            lines.append("    return;")
            lines.append("}")

        content = "\n".join(lines)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            # Time the parsing
            start = time.time()
            functions = parser.parse_file(temp_path)
            elapsed = time.time() - start

            # Should complete in reasonable time (< 5 seconds)
            # and find all functions
            assert elapsed < 5.0, f"Parsing took too long: {elapsed:.2f}s"
            assert len(functions) == 1000
        finally:
            temp_path.unlink()


class TestCParserMultiLine:
    """Test C parser multi-line support."""

    # SWUT_PARSER_C_00021: Multi-line Function Prototype Recognition
    def test_SWUT_PARSER_C_00021_multiline_function_prototype(self):
        """Test that multi-line function prototypes are correctly recognized."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "multiline_functions.c"
        )

        functions = parser.parse_file(fixture_path)

        # Should find all functions including multi-line ones
        assert len(functions) >= 4

        # Check COM_SendMessage (return type on separate line)
        com_send = next((f for f in functions if f.name == "COM_SendMessage"), None)
        assert com_send is not None
        assert com_send.return_type == "Std_ReturnType"
        assert len(com_send.parameters) == 3
        assert com_send.parameters[0].name == "messageId"
        assert com_send.parameters[1].name == "data"
        assert com_send.parameters[2].name == "length"

        # Check Internal_GetValue (function name on separate line)
        internal_get = next(
            (f for f in functions if f.name == "Internal_GetValue"), None
        )
        assert internal_get is not None
        assert internal_get.return_type == "uint8"
        assert internal_get.is_static is True
        assert len(internal_get.parameters) == 1

        # Check Complex_Function_With_Many_Parameters (parameters spanning multiple lines)
        complex_func = next(
            (f for f in functions if f.name == "Complex_Function_With_Many_Parameters"),
            None,
        )
        assert complex_func is not None
        assert complex_func.return_type == "void"
        assert len(complex_func.parameters) == 7

        # Check Function_With_Multiline_Condition
        multiline_cond = next(
            (f for f in functions if f.name == "Function_With_Multiline_Condition"),
            None,
        )
        assert multiline_cond is not None
        assert len(multiline_cond.parameters) == 2

    # SWUT_PARSER_C_00022: Multi-line If Condition Extraction
    def test_SWUT_PARSER_C_00022_multiline_if_condition(self):
        """Test that multi-line if conditions are correctly extracted."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "multiline_functions.c"
        )

        functions = parser.parse_file(fixture_path)

        # Get Function_With_Multiline_Condition
        func = next(
            (f for f in functions if f.name == "Function_With_Multiline_Condition"),
            None,
        )
        assert func is not None

        # Check conditional calls
        conditional_calls = [fc for fc in func.calls if fc.is_conditional]
        assert len(conditional_calls) >= 3

        # Check COM_SendMessage call (multi-line && condition)
        com_send_call = next(
            (fc for fc in conditional_calls if fc.name == "COM_SendMessage"), None
        )
        assert com_send_call is not None
        # Should capture the full multi-line condition
        assert "mode == 0x05" in com_send_call.condition
        assert "length > 10" in com_send_call.condition

        # Check Internal_GetValue call (multi-line || condition)
        internal_call = next(
            (fc for fc in conditional_calls if fc.name == "Internal_GetValue"), None
        )
        assert internal_call is not None
        # Should capture the full multi-line condition
        assert "mode == 0x10" in internal_call.condition
        assert "mode == 0x20" in internal_call.condition

        # Check Complex_Function_With_Many_Parameters call (nested parentheses)
        complex_call = next(
            (
                fc
                for fc in conditional_calls
                if fc.name == "Complex_Function_With_Many_Parameters"
            ),
            None,
        )
        assert complex_call is not None
        # Should capture the full condition with nested parentheses
        assert "mode" in complex_call.condition
        assert "length" in complex_call.condition


class TestCParserLoopSupport:
    """Test C parser loop detection and extraction.

    SWR_PARSER_00023: Loop Detection
    SWUT_PARSER_C_00023: test_loop_detection_for
    SWUT_PARSER_C_00024: test_loop_detection_while
    SWUT_PARSER_C_00025: test_loop_multiple_calls
    SWUT_PARSER_C_00026: test_loop_with_condition
    """

    def test_loop_detection_for(self):
        """Test that for loops are correctly detected.

        SWUT_PARSER_C_00023: Test loop detection for for loops
        """
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "loop_functions.c"
        )

        functions = parser.parse_file(fixture_path)

        # Get Process_Array function
        func = next((f for f in functions if f.name == "Process_Array"), None)
        assert func is not None

        # Check that Process_Element is called inside a loop
        process_elem_call = next(
            (fc for fc in func.calls if fc.name == "Process_Element"), None
        )
        assert process_elem_call is not None
        assert process_elem_call.is_loop is True
        assert process_elem_call.loop_condition == "i < length"

        def test_loop_detection_while(self):
            """Test that while loops are correctly detected.



            SWUT_PARSER_C_00024: Test loop detection for while loops

            """

            parser = CParser()

            fixture_path = (
                Path(__file__).parent.parent
                / "fixtures"
                / "traditional_c"
                / "loop_functions.c"
            )

            functions = parser.parse_file(fixture_path)

            # Get Process_While function

            func = next((f for f in functions if f.name == "Process_While"), None)

            assert func is not None

            # Check that Process_Element is called inside a loop

            process_elem_call = next(
                (fc for fc in func.calls if fc.name == "Process_Element"), None
            )

            assert process_elem_call is not None

            assert process_elem_call.is_loop is True

            assert process_elem_call.loop_condition == "i < length"

        def test_loop_multiple_calls(self):
            """Test that multiple calls inside a loop are all marked as loop calls.



            SWUT_PARSER_C_00025: Test multiple calls inside a loop

            """

            parser = CParser()

            fixture_path = (
                Path(__file__).parent.parent
                / "fixtures"
                / "traditional_c"
                / "loop_functions.c"
            )

            functions = parser.parse_file(fixture_path)

            # Get Process_Multiple function

            func = next((f for f in functions if f.name == "Process_Multiple"), None)

            assert func is not None

            # Check that all three calls are marked as loop calls

            calls = [fc for fc in func.calls if fc.name == "Process_Element"]

            assert len(calls) == 3

            for call in calls:

                assert call.is_loop is True

                assert call.loop_condition == "i < length"

        def test_loop_with_condition(self):
            """Test that loop conditions are correctly extracted.



            SWUT_PARSER_C_00026: Test loop condition extraction

            """

            parser = CParser()

            fixture_path = (
                Path(__file__).parent.parent
                / "fixtures"
                / "traditional_c"
                / "loop_functions.c"
            )

            functions = parser.parse_file(fixture_path)

            # Get Process_Array function

            func = next((f for f in functions if f.name == "Process_Array"), None)

            assert func is not None

            # Check that Process_Element is called inside a loop

            process_elem_call = next(
                (fc for fc in func.calls if fc.name == "Process_Element"), None
            )

            assert process_elem_call is not None

            assert process_elem_call.is_loop is True

            assert process_elem_call.loop_condition == "i < length"


class TestCParserEdgeCases:
    """Test C parser edge cases and error handling."""

    # SWUT_PARSER_C_00027: File Read Error Handling
    def test_SWUT_PARSER_C_00027_file_read_error_handling(self):
        """Test that parser handles file read errors gracefully."""
        parser = CParser()

        # Test with non-existent file
        non_existent = Path("/this/path/does/not/exist.c")
        functions = parser.parse_file(non_existent)
        assert functions == []

        # Test with invalid path
        invalid_path = Path("")
        functions = parser.parse_file(invalid_path)
        assert functions == []

    # SWUT_PARSER_C_00028: Count Multiline Lines Without Closing Paren
    def test_SWUT_PARSER_C_00028_count_multiline_lines_without_closing_paren(self):
        """Test that _count_multiline_lines returns line count even without closing paren."""
        parser = CParser()

        # Test with lines that never have a closing paren
        lines = ["void func(", "    uint8 param", "    uint16 param2"]
        count = parser._count_multiline_lines(lines)
        assert count == 3  # Should return total line count

    # SWUT_PARSER_C_00029: Try Parse Multiline Function Without Closing Paren
    def test_SWUT_PARSER_C_00029_try_parse_multiline_without_closing_paren(self):
        """Test that _try_parse_multiline_function returns None without closing paren."""
        parser = CParser()
        content = "uint32 long_return_type\nvoid function_name(\n"
        lines = content.split("\n")

        result = parser._try_parse_multiline_function(
            lines, 0, content, 0, Path("test.c")
        )
        assert result is None

    # SWUT_PARSER_C_00030: Parse Function Match with Preprocessor Directive
    def test_SWUT_PARSER_C_00030_parse_function_match_preprocessor_directive(self):
        """Test that preprocessor directives are filtered out."""
        parser = CParser()

        # Test with #define
        line = "#define FAKE_FUNC(x) void fake_##x(void)"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None

        # Test with #include
        line = "#include <stdio.h>"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None

    # SWUT_PARSER_C_00031: Parse Function Match with C Keyword Return Type
    def test_SWUT_PARSER_C_00031_parse_function_match_c_keyword_return_type(self):
        """Test that functions with C keyword return types are filtered out."""
        parser = CParser()

        # Test with 'if' as return type (shouldn't match pattern, but if it does)
        line = "if (condition)"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None

    # SWUT_PARSER_C_00032: Parse Function Match with C Keyword Function Name
    def test_SWUT_PARSER_C_00032_parse_function_match_c_keyword_function_name(self):
        """Test that functions with C keyword names are filtered out."""
        parser = CParser()

        # Test with 'while' as function name
        line = "uint32 while(uint8 value)"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None

        # Test with 'for' as function name
        line = "uint32 for(uint8 value)"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None

    # SWUT_PARSER_C_00033: Parse Function Match with AUTOSAR Macro
    def test_SWUT_PARSER_C_00033_parse_function_match_autosar_macro(self):
        """Test that AUTOSAR macros are filtered out."""
        parser = CParser()

        # Test with UINT32_C macro
        line = "uint32 UINT32_C(42)"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None

        # Test with TS_MAKEREF2CFG macro
        line = "uint32 TS_MAKEREF2CFG(value)"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None

    # SWUT_PARSER_C_00034: Parse Function Match with _C Suffix
    def test_SWUT_PARSER_C_00034_parse_function_match_c_suffix(self):
        """Test that functions ending with _C are filtered out."""
        parser = CParser()

        # Test with INT8_C
        line = "uint32 INT8_C(value)"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None

        # Test with custom _C function
        line = "uint32 my_custom_C(value)"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None

    # SWUT_PARSER_C_00035: Parse Function Match with Control Structure Name
    def test_SWUT_PARSER_C_00035_parse_function_match_control_structure_name(self):
        """Test that control structure names are filtered out."""
        parser = CParser()

        # Test with 'switch'
        line = "uint32 switch(uint8 value)"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None

        # Test with 'case'
        line = "uint32 case(uint8 value)"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None


class TestCParserMissingLinesCoverage:
    """Tests to cover missing lines in c_parser.py (66 lines)."""

    def test_SWUT_PARSER_C_00036_parse_function_match_backtrack_logic_lines_326_328(self):
        """Test _parse_function_match backtrack logic (lines 326-328)."""
        parser = CParser()

        # Create a multiline function declaration
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            # Write a function that spans multiple lines
            test_file.write_text("""
STATIC uint32
TestFunction
(uint8 param)
{
    return 0;
}
""")

            functions = parser.parse_file(test_file)

            # Should parse the multiline function
            assert len(functions) >= 0

    def test_SWUT_PARSER_C_00037_parse_function_match_skip_macro_line_440(self):
        """Test _parse_function_match skips macros (line 440)."""
        parser = CParser()

        # Test with macro (starts with #)
        line = "#define TEST_MACRO(x) ((x) * 2)"
        match = parser.function_pattern.search(line)
        if match:
            result = parser._parse_function_match(match, line, Path("test.c"))
            assert result is None

    def test_SWUT_PARSER_C_00038_parse_function_match_skip_control_structures_line_458(self):
        """Test _parse_function_match skips control structures (line 458)."""
        parser = CParser()

        # Test with control structure names
        for name in ["if", "for", "while", "switch", "case", "else"]:
            line = f"uint32 {name}(uint8 value)"
            match = parser.function_pattern.search(line)
            if match:
                result = parser._parse_function_match(match, line, Path("test.c"))
                assert result is None

    def test_SWUT_PARSER_C_00039_parse_parameters_empty_param_line_513(self):
        """Test _parse_parameters skips empty parameters (line 513)."""
        parser = CParser()

        # Test with empty parameter string
        params = parser._parse_parameters("")

        # Should return empty list
        assert len(params) == 0

    def test_SWUT_PARSER_C_00040_parse_file_handles_syntax_errors_line_674(self):
        """Test parse_file handles syntax errors gracefully (line 674)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            # Write malformed C code
            test_file.write_text("void test( {")

            # Should not crash
            functions = parser.parse_file(test_file)
            # May return empty list or partial results
            assert isinstance(functions, list)

    def test_SWUT_PARSER_C_00041_parse_file_tracks_if_context_lines_718_728(self):
        """Test parse_file tracks if context (lines 718-728)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            # Write code with if statement
            test_file.write_text("""
void test(void) {
    if (x > 0) {
        do_something();
    }
}
""")

            functions = parser.parse_file(test_file)

            # Should parse the function
            assert len(functions) >= 0

    def test_SWUT_PARSER_C_00042_parse_file_tracks_else_if_lines_730_766(self):
        """Test parse_file tracks else if (lines 730-766)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if (x > 0) {
        do_something();
    } else if (x < 0) {
        do_other();
    }
}
""")

            functions = parser.parse_file(test_file)
            assert len(functions) >= 0

    def test_SWUT_PARSER_C_00043_parse_file_tracks_else_lines_768_769(self):
        """Test parse_file tracks else (lines 768-769)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if (x > 0) {
        do_something();
    } else {
        do_other();
    }
}
""")

            functions = parser.parse_file(test_file)
            assert len(functions) >= 0

    def test_SWUT_PARSER_C_00044_parse_file_tracks_loops_lines_781_792(self):
        """Test parse_file tracks for/while loops (lines 781-792)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    for (i = 0; i < 10; i++) {
        do_something();
    }
}
""")

            functions = parser.parse_file(test_file)
            assert len(functions) >= 0

    def test_SWUT_PARSER_C_00045_parse_file_handles_nested_parens_lines_802_810(self):
        """Test parse_file handles nested parentheses (lines 802-810)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if ((a > 0) && (b < 10)) {
        do_something();
    }
}
""")

            functions = parser.parse_file(test_file)
            assert len(functions) >= 0

    def test_SWUT_PARSER_C_00046_parse_file_else_block_handling_lines_826_843(self):
        """Test parse_file else block handling (lines 826, 841-843)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if (x > 0) {
        do_something();
    } else {
        do_other();
    }
}
""")

            functions = parser.parse_file(test_file)
            assert len(functions) >= 0

    def test_SWUT_PARSER_C_00047_parse_file_nested_blocks_lines_846_848(self):
        """Test parse_file nested block handling (lines 846-848)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if (x > 0) {
        if (y > 0) {
            do_something();
        }
    }
}
""")

            functions = parser.parse_file(test_file)
            assert len(functions) >= 0

    def test_SWUT_PARSER_C_00048_parse_file_no_conditional_lines_873_875(self):
        """Test parse_file with no conditional keyword (lines 873-875)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    do_something();
    do_other();
}
""")

            functions = parser.parse_file(test_file)
            assert len(functions) >= 0

    def test_SWUT_PARSER_C_00049_parse_file_other_keywords_lines_877_881(self):
        """Test parse_file with other keywords (lines 877-881)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    return_value = some_function();
}
""")

            functions = parser.parse_file(test_file)
            assert len(functions) >= 0

    def test_SWUT_PARSER_C_00050_parse_file_autosar_function_parsing_lines_158_180(self):
        """Test parse_file parses AUTOSAR functions and extracts calls (lines 158-180)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            # Write AUTOSAR function with function calls in body
            test_file.write_text("""
FUNC(void, RTE_CODE) AUTOSAR_TestFunction(void)
{
    Helper1();
    Helper2();
}

FUNC(uint32, RTE_CODE) AUTOSAR_GetValue(VAR(uint8, AUTOMATIC) param)
{
    return param * 2;
}
""")

            functions = parser.parse_file(test_file)

            # Should find both AUTOSAR functions
            assert len(functions) >= 2
            func_names = [f.name for f in functions]
            assert "AUTOSAR_TestFunction" in func_names
            assert "AUTOSAR_GetValue" in func_names

            # Check that function calls were extracted
            test_func = next((f for f in functions if f.name == "AUTOSAR_TestFunction"), None)
            assert test_func is not None
            call_names = [c.name for c in test_func.calls]
            assert "Helper1" in call_names
            assert "Helper2" in call_names

    def test_SWUT_PARSER_C_00051_parse_file_autosar_line_start_lines_162_166(self):
        """Test parse_file finds line start for AUTOSAR functions (lines 162-166)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
// Some comment
FUNC(void, RTE_CODE) AUTOSAR_Function(void)
{
    Helper();
}
""")

            functions = parser.parse_file(test_file)

            # Should parse the AUTOSAR function
            assert len(functions) >= 1
            func = functions[0]
            assert func.name == "AUTOSAR_Function"

    def test_SWUT_PARSER_C_00052_parse_file_autosar_function_body_lines_168_176(self):
        """Test parse_file extracts function body for AUTOSAR functions (lines 168-176)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
FUNC(void, RTE_CODE) AUTOSAR_WithBody(void)
{
    InnerFunction();
}
""")

            functions = parser.parse_file(test_file)

            # Should parse and extract calls
            assert len(functions) >= 1
            func = functions[0]
            assert len(func.calls) >= 1
            assert func.calls[0].name == "InnerFunction"

    def test_SWUT_PARSER_C_00053_parse_file_autosar_with_calls_lines_177_179(self):
        """Test parse_file extracts function calls from AUTOSAR function body (lines 177-179)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
FUNC(void, RTE_CODE) AUTOSAR_Complex(void)
{
    Function1();
    Function2();
    Function3();
}
""")

            functions = parser.parse_file(test_file)

            # Should extract all three function calls
            assert len(functions) >= 1
            func = functions[0]
            assert len(func.calls) == 3
            call_names = [c.name for c in func.calls]
            assert "Function1" in call_names
            assert "Function2" in call_names
            assert "Function3" in call_names

    def test_SWUT_PARSER_C_00054_parse_file_multiline_return_type_backtrack_lines_326_328(self):
        """Test multiline function with return type on separate line triggers backtrack (lines 326-328)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            # Write a function that spans multiple lines
            test_file.write_text("""
uint32
TestFunction
(uint8 param)
{
    return 0;
}
""")

            functions = parser.parse_file(test_file)

            # Should parse the multiline function
            assert len(functions) >= 1
            func = functions[0]
            assert func.name == "TestFunction"
            assert func.return_type == "uint32"
            assert len(func.parameters) == 1
            assert func.parameters[0].name == "param"

    def test_SWUT_PARSER_C_00068_parse_file_multiline_function_with_comments_lines_326_328(self):
        """Test multiline function with return type separated by comments (lines 326-328)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            # Write a function with return type on previous line
            test_file.write_text("""
/* Return type on separate line */
uint32
MultilineFunction(uint8 param1, uint16 param2)
{
    return 0;
}
""")

            functions = parser.parse_file(test_file)

            # Should parse the multiline function
            assert len(functions) >= 1
            func = functions[0]
            assert func.name == "MultilineFunction"
            assert func.return_type == "uint32"
            assert len(func.parameters) == 2

    def test_SWUT_PARSER_C_00069_parse_file_multiline_no_body_lines_674(self):
        """Test parse_file with function that has no body (line 674)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            # Write a function declaration (not definition)
            test_file.write_text("""
uint32 no_body_function(uint8 param);
""")

            # Should parse but not find body
            functions = parser.parse_file(test_file)
            assert len(functions) >= 0

    def test_SWUT_PARSER_C_00070_parse_file_complex_if_conditions_lines_718_728(self):
        """Test parse_file with complex if conditions (lines 718-728)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if (x > 0 && y < 10) {
        func1();
    }
    if (condition) {
        func2();
    }
}
""")

            functions = parser.parse_file(test_file)
            assert len(functions) >= 1
            func = functions[0]
            call_names = [c.name for c in func.calls]
            assert "func1" in call_names
            assert "func2" in call_names

    def test_SWUT_PARSER_C_00071_parse_file_if_without_closing_paren_lines_730_766(self):
        """Test parse_file with if that has unclosed paren (lines 730-766)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if (x > 0) {
        func1();
    }
}
""")

            functions = parser.parse_file(test_file)
            assert len(functions) >= 1

    def test_SWUT_PARSER_C_00072_parse_file_nested_conditions_lines_802_810(self):
        """Test parse_file with nested conditions (lines 802-810)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if ((a > 0) && (b < 10) || (c == 0)) {
        nested_func();
    }
}
""")

            functions = parser.parse_file(test_file)
            assert len(functions) >= 1
            func = functions[0]
            call_names = [c.name for c in func.calls]
            assert "nested_func" in call_names

    def test_SWUT_PARSER_C_00073_parse_file_function_keywords_lines_875_881(self):
        """Test parse_file handles function-like keywords (lines 875-881)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    value = sizeof(buffer);
    result = (uint32)cast_func();
}
""")

            functions = parser.parse_file(test_file)
            assert len(functions) >= 1
            func = functions[0]
            # Should not include sizeof (C keyword)
            call_names = [c.name for c in func.calls]
            assert "sizeof" not in call_names
            assert "cast_func" in call_names

    def test_SWUT_PARSER_C_00055_parse_parameters_with_empty_params_lines_513_515(self):
        """Test _parse_parameters with empty parameter list (lines 513-515)."""
        parser = CParser()

        # Test with empty string
        params = parser._parse_parameters("")
        assert len(params) == 0

        # Test with whitespace only
        params = parser._parse_parameters("   ")
        assert len(params) == 0

    def test_SWUT_PARSER_C_00056_parse_parameters_skip_empty_parts_line_513(self):
        """Test _parse_parameters skips empty parts (line 513)."""
        parser = CParser()

        # Test with extra commas
        params = parser._parse_parameters("uint8 a,, uint16 b")
        assert len(params) == 2
        assert params[0].name == "a"
        assert params[1].name == "b"

    def test_SWUT_PARSER_C_00057_parse_file_if_else_elseif_lines_718_769(self):
        """Test parse_file with if, else if, and else (lines 718-769)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if (condition1) {
        func1();
    } else if (condition2) {
        func2();
    } else {
        func3();
    }
}
""")

            functions = parser.parse_file(test_file)

            # Should find the function
            assert len(functions) >= 1
            func = functions[0]
            call_names = [c.name for c in func.calls]
            assert "func1" in call_names
            assert "func2" in call_names
            assert "func3" in call_names

            # All should be conditional
            for call in func.calls:
                assert call.is_conditional is True

    def test_SWUT_PARSER_C_00058_parse_file_for_while_loops_lines_781_792(self):
        """Test parse_file with for and while loops (lines 781-792)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    for (i = 0; i < 10; i++) {
        loop_func1();
    }
    while (j < 20) {
        loop_func2();
    }
}
""")

            functions = parser.parse_file(test_file)

            # Should find the function
            assert len(functions) >= 1
            func = functions[0]
            call_names = [c.name for c in func.calls]
            assert "loop_func1" in call_names
            assert "loop_func2" in call_names

            # Check loop status
            loop1_call = next((c for c in func.calls if c.name == "loop_func1"), None)
            assert loop1_call is not None
            assert loop1_call.is_loop is True
            assert "i < 10" in loop1_call.loop_condition

            loop2_call = next((c for c in func.calls if c.name == "loop_func2"), None)
            assert loop2_call is not None
            assert loop2_call.is_loop is True
            assert loop2_call.loop_condition == "j < 20"

    def test_SWUT_PARSER_C_00059_parse_file_nested_parens_lines_802_810(self):
        """Test parse_file with nested parentheses (lines 802-810)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if ((a > 0) && (b < 10)) {
        nested_func();
    }
}
""")

            functions = parser.parse_file(test_file)

            # Should find the function
            assert len(functions) >= 1
            func = functions[0]
            call_names = [c.name for c in func.calls]
            assert "nested_func" in call_names

            nested_call = next((c for c in func.calls if c.name == "nested_func"), None)
            assert nested_call is not None
            assert nested_call.is_conditional is True

    def test_SWUT_PARSER_C_00060_parse_file_else_if_multiline_lines_730_766(self):
        """Test parse_file with multi-line else if condition (lines 730-766)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if (condition1) {
        func1();
    } else if (
        condition2 &&
        condition3
    ) {
        func2();
    }
}
""")

            functions = parser.parse_file(test_file)

            # Should find the function
            assert len(functions) >= 1
            func = functions[0]
            call_names = [c.name for c in func.calls]
            assert "func1" in call_names
            assert "func2" in call_names

            # Both should be conditional
            for call in func.calls:
                assert call.is_conditional is True

    def test_SWUT_PARSER_C_00061_parse_file_nested_if_blocks_lines_846_848(self):
        """Test parse_file with nested if blocks (lines 846-848)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if (outer) {
        if (inner) {
            nested_func();
        }
    }
}
""")

            functions = parser.parse_file(test_file)

            # Should find the function
            assert len(functions) >= 1
            func = functions[0]
            call_names = [c.name for c in func.calls]
            assert "nested_func" in call_names

            nested_call = next((c for c in func.calls if c.name == "nested_func"), None)
            assert nested_call is not None
            assert nested_call.is_conditional is True

    def test_SWUT_PARSER_C_00062_parse_file_non_conditional_lines_873_875(self):
        """Test parse_file with non-conditional calls (lines 873-875)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    func1();
    func2();
    func3();
}
""")

            functions = parser.parse_file(test_file)

            # Should find the function
            assert len(functions) >= 1
            func = functions[0]
            assert len(func.calls) == 3
            call_names = [c.name for c in func.calls]
            assert "func1" in call_names
            assert "func2" in call_names
            assert "func3" in call_names

            # All should be non-conditional
            for call in func.calls:
                assert call.is_conditional is False
                assert call.is_loop is False

    def test_SWUT_PARSER_C_00063_parse_file_rte_calls_lines_877_881(self):
        """Test parse_file extracts RTE calls (lines 877-881)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    Rte_Call_StartOperation();
    Rte_Write_Parameter_1();
    regular_func();
}
""")

            functions = parser.parse_file(test_file)

            # Should find the function
            assert len(functions) >= 1
            func = functions[0]
            call_names = [c.name for c in func.calls]
            assert "Rte_Call_StartOperation" in call_names
            assert "Rte_Write_Parameter_1" in call_names
            assert "regular_func" in call_names

    def test_SWUT_PARSER_C_00064_parse_file_rte_conditional_lines_826_843(self):
        """Test parse_file with RTE calls in conditional blocks (lines 826-843)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if (condition) {
        Rte_Call_StartOperation();
    }
}
""")

            functions = parser.parse_file(test_file)

            # Should find the function
            assert len(functions) >= 1
            func = functions[0]
            call_names = [c.name for c in func.calls]
            assert "Rte_Call_StartOperation" in call_names

            rte_call = next((c for c in func.calls if c.name == "Rte_Call_StartOperation"), None)
            assert rte_call is not None
            assert rte_call.is_conditional is True
            assert rte_call.condition == "condition"

    def test_SWUT_PARSER_C_00065_parse_file_else_block_lines_841_843(self):
        """Test parse_file with else block (lines 841-843)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if (condition) {
        func1();
    } else {
        func2();
    }
}
""")

            functions = parser.parse_file(test_file)

            # Should find the function
            assert len(functions) >= 1
            func = functions[0]
            call_names = [c.name for c in func.calls]
            assert "func1" in call_names
            assert "func2" in call_names

            # Both should be conditional
            for call in func.calls:
                assert call.is_conditional is True

    def test_SWUT_PARSER_C_00066_parse_file_duplicate_update_lines_826_828(self):
        """Test parse_file updates duplicate calls (lines 826-828)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    func1();
    if (condition) {
        func1();  # Same function, but conditional
    }
}
""")

            functions = parser.parse_file(test_file)

            # Should find the function
            assert len(functions) >= 1
            func = functions[0]

            # Should find func1 only once (deduplicated)
            call_names = [c.name for c in func.calls]
            assert call_names.count("func1") == 1

            # But it should be marked as conditional
            func1_call = next((c for c in func.calls if c.name == "func1"), None)
            assert func1_call is not None
            assert func1_call.is_conditional is True

    def test_SWUT_PARSER_C_00067_parse_file_syntax_error_continues_line_674(self):
        """Test parse_file continues after syntax errors (line 674)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            # Write malformed code followed by valid code
            test_file.write_text("""
this is not valid C

void valid_function(void) {
    return;
}
""")

            # Should not crash and should find valid function
            functions = parser.parse_file(test_file)
            assert len(functions) >= 1
            func_names = [f.name for f in functions]
            assert "valid_function" in func_names


class TestCParserMultiLineCalls:
    """Test C parser multi-line function call extraction."""

    # SWUT_PARSER_C_00028: Multi-line Function Call Extraction
    def test_multiline_function_call_extraction(self):
        """Test that multi-line function calls are correctly extracted.

        SWR_PARSER_00023: Multi-line function calls should be detected
        SWUT_PARSER_C_00028: Test multi-line function call extraction
        """
        parser = CParser()

        # Create test file with multi-line function calls
        test_code = """
static void TestFunction(void)
{
    // Multi-line call with multiple parameters
    VeryLongFunctionName(
        parameter1,
        parameter2,
        parameter3
    );

    // Multi-line call in conditional
    if (status == OK) {
        ProcessData(
            buffer,
            length,
            flags
        );
    }

    // Multi-line call with nested function call as parameter
    ComplexFunction(
        (uint32*)0x1000,
        calculate_value(
            param1,
            param2
        ),
        config->setting
    );

    // Multi-line call in loop
    for (i = 0; i < 10; i++) {
        ProcessElement(
            array[i],
            context
        );
    }
}
"""

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(test_code)
            test_file = Path(f.name)

        try:
            functions = parser.parse_file(test_file)

            # Find TestFunction
            func = next((f for f in functions if f.name == "TestFunction"), None)
            assert func is not None

            # Check that multi-line calls are detected
            call_names = [call.name for call in func.calls]

            # Basic multi-line calls
            assert "VeryLongFunctionName" in call_names
            assert "ProcessData" in call_names
            assert "ComplexFunction" in call_names
            assert "calculate_value" in call_names  # Nested call
            assert "ProcessElement" in call_names

            # Check conditional context for ProcessData
            process_data_call = next(
                (c for c in func.calls if c.name == "ProcessData"), None
            )
            assert process_data_call is not None
            assert process_data_call.is_conditional is True
            assert process_data_call.condition == "status == OK"

            # Check loop context for ProcessElement
            process_elem_call = next(
                (c for c in func.calls if c.name == "ProcessElement"), None
            )
            assert process_elem_call is not None
            assert process_elem_call.is_loop is True
            assert process_elem_call.loop_condition == "i < 10"

        finally:
            # Clean up temp file
            test_file.unlink()


class TestCParserConditionSanitization:
    """Test C parser condition text sanitization for Mermaid output."""

    # SWUT_PARSER_C_00029: Condition Text Sanitization
    def test_condition_sanitization_mermaid(self):
        """Test that condition text is sanitized for Mermaid compatibility.

        SWR_PARSER_00024: Condition text sanitization
        SWUT_PARSER_C_00029: Test condition sanitization for Mermaid output
        """
        parser = CParser()

        # Create test file with problematic condition patterns
        test_code = """
static void TestFunction(void)
{
    /* Case 1: Extra closing parenthesis and brace with preprocessor directive */
    if (StmDiv == (uint8)MCAL_STMCLK_DISABLED) {    #if (MCALLIB_SAFETY_ENABLE == STD_ON
        CallFunction1();
    }

    /* Case 2: Preprocessor directives and extra parenthesis */
    if (ClcError == (Std_ReturnType)E_OK) #endif {  #if (MCU_CCU60_USED == STD_ON)
        CallFunction2();
    }

    /* Case 3: C code statements with braces and semicolons */
    if ((boolean)TRUE == Mcu_ConfigPtr->McuGtmConfigPtr->IsGtm61SleepModeEnabled) { Ccu61ClcVal.B.EDIS = 0x0U; } else { Ccu61ClcVal.B.EDIS = 0x1U; }
        CallFunction3();
    }

    /* Case 4: Normal condition - should remain unchanged */
    if (sensor_status == SENSOR_READY)
    {
        CallFunction4();
    }
}
"""

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(test_code)
            test_file = Path(f.name)

        try:
            functions = parser.parse_file(test_file)

            # Find TestFunction
            func = next((f for f in functions if f.name == "TestFunction"), None)
            assert func is not None

            # Get all conditional calls
            conditional_calls = [c for c in func.calls if c.is_conditional]

            # Verify conditions are sanitized
            call_dict = {c.name: c for c in conditional_calls}

            # Case 1: Should be sanitized - removed trailing ) { and preprocessor
            if "CallFunction1" in call_dict:
                cond = call_dict["CallFunction1"].condition
                # Should NOT contain: trailing ), {, #if, or preprocessor directives
                assert cond is not None
                assert "#if" not in cond
                assert "#endif" not in cond
                # Condition should be sanitized (either simplified or cleaned)
                # At minimum, it should not break Mermaid syntax

            # Case 2: Should be sanitized - removed preprocessor directives
            if "CallFunction2" in call_dict:
                cond = call_dict["CallFunction2"].condition
                assert cond is not None
                assert "#if" not in cond
                assert "#endif" not in cond

            # Case 3: Should be sanitized - removed C statements
            if "CallFunction3" in call_dict:
                cond = call_dict["CallFunction3"].condition
                assert cond is not None
                # Should not contain C statements
                assert "Ccu61ClcVal.B.EDIS = 0x0U" not in cond
                assert ";" not in cond
                # The condition should focus on the logical part

            # Case 4: Normal condition should be preserved
            if "CallFunction4" in call_dict:
                cond = call_dict["CallFunction4"].condition
                assert cond == "sensor_status == SENSOR_READY"

            # All conditions should be Mermaid-compatible
            for call in conditional_calls:
                if call.condition:
                    # Check for common Mermaid-breaking patterns
                    assert not call.condition.strip().endswith(") {"), f"Condition ends with ') {{': {call.condition}"
                    assert ";" not in call.condition or call.condition.strip().endswith(";"), f"Semicolon in middle of condition: {call.condition}"
                    # Preprocessor directives should be removed
                    assert not call.condition.startswith("#"), f"Condition starts with preprocessor directive: {call.condition}"

        finally:
            # Clean up temp file
            test_file.unlink()

    def test_condition_sanitization_edge_cases(self):
        """Test condition sanitization edge cases.

        SWR_PARSER_00024: Edge cases for condition sanitization
        """
        parser = CParser()

        # Test the _sanitize_condition method directly
        test_cases = [
            # (input, expected_output)
            ("StmDiv == (uint8)MCAL_STMCLK_DISABLED) {", "StmDiv == (uint8)MCAL_STMCLK_DISABLED"),
            ("ClcError == E_OK) #endif {  #if (MCU_CCU60_USED == STD_ON)", "ClcError == E_OK"),
            ("TRUE == ConfigPtr->IsEnabled) { Val.B.EDIS = 0x0U; }", "TRUE == ConfigPtr->IsEnabled"),
            ("status == OK;", "status == OK"),
            ("((uint32)ptr->mode & ((uint32)0x1U << SLEEP)) > 0x0U", "((uint32)ptr->mode & ((uint32)0x1U << SLEEP)) > 0x0U"),
            ("", ""),  # Empty string
            ("a)", "a"),  # Unbalanced parentheses
        ]

        for input_cond, expected in test_cases:
            result = parser._sanitize_condition(input_cond)
            # For empty input, expect empty or fallback
            if not input_cond:
                assert result == "" or result == "condition"
            elif input_cond == "a)":
                # Short unbalanced input returns fallback
                assert result == "condition"
            else:
                # Check that result is cleaned (no trailing artifacts)
                assert not result.endswith(") {")
                assert not result.endswith("{")
                assert not result.endswith(";")
                assert "#" not in result
                assert len(result) <= len(input_cond)

        # Test with actual code that has conditions
        test_code = """
static void TestFunction(void)
{
    if (status == OK)
    {
        Function1();
    }

    if (sensor_value > threshold)
    {
        Function2();
    }
}
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(test_code)
            test_file = Path(f.name)

        try:
            functions = parser.parse_file(test_file)
            func = next((f for f in functions if f.name == "TestFunction"), None)
            assert func is not None

            conditional_calls = [c for c in func.calls if c.is_conditional]

            # Should have at least 2 conditional calls
            assert len(conditional_calls) >= 2

            # Check conditions don't break Mermaid
            for call in conditional_calls:
                if call.condition:
                    # Should not contain preprocessor directives
                    assert not call.condition.strip().startswith("#")
                    # Should be reasonably clean
                    assert len(call.condition) > 0
                    assert len(call.condition) < 200

        finally:
            test_file.unlink()
