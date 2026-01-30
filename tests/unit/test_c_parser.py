"""Tests for C parser module (SWUT_PARSER_C_*)"""

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
        assert "helper1" in calls
        assert "helper2" in calls

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
        assert "helper" in calls
        assert "if" not in calls
        assert "return" not in calls
        assert "while" not in calls
        assert "break" not in calls

        # Test that AUTOSAR types are filtered
        body = (
            "void test(void) {\n    uint8* buffer = (uint8*)0x2000;\n    helper();\n}"
        )
        calls = parser._extract_function_calls(body)
        assert "helper" in calls
        assert "uint8" not in calls

        # Test RTE calls
        body = "void test(void) {\n    Rte_Call_StartOperation();\n    helper();\n}"
        calls = parser._extract_function_calls(body)
        assert "Rte_Call_StartOperation" in calls
        assert "helper" in calls

        # Test deduplication
        body = "void test(void) {\n    helper();\n    helper();\n    helper();\n}"
        calls = parser._extract_function_calls(body)
        assert calls.count("helper") == 1  # Should be deduplicated

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
        assert "helper1" in caller.calls
        assert "helper2" in caller.calls
        assert "helper3" in caller.calls

        # Check that C keywords are not in calls
        control = next((f for f in functions if f.name == "control_structures"), None)
        assert control is not None
        assert "if" not in control.calls
        assert "for" not in control.calls
        assert "while" not in control.calls
        assert "switch" not in control.calls

        # Check RTE calls
        rte_func = next(
            (f for f in functions if f.name == "function_with_rte_calls"), None
        )
        assert rte_func is not None
        assert "Rte_Call_StartOperation" in rte_func.calls
        assert "Rte_Write_Parameter_1" in rte_func.calls


class TestCParserLineByLineProcessing:
    """Test line-by-line processing to avoid catastrophic backtracking (SWR_PARSER_C_00019)."""

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
    """Test regex optimization with length limits (SWR_PARSER_C_00020)."""

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
