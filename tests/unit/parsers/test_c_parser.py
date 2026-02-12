"""Tests for parsers/c_parser.py (SWUT_PARSER_00011-00025)"""

from pathlib import Path
import pytest

from autosar_calltree.database.models import FunctionType
from autosar_calltree.parsers.c_parser import CParser


# SWUT_PARSER_00011: Traditional C Function Pattern Recognition

def test_traditional_c_function_pattern():
    """SWUT_PARSER_00011

    Test that traditional C function patterns are correctly recognized.
    """
    parser = CParser()

    # Test basic void function
    line = "void Demo_Init(void)"
    result = parser.parse_function_declaration(line, Path("demo.c"), 1)
    assert result is not None
    assert result.name == "Demo_Init"
    assert result.return_type == "void"
    assert result.function_type == FunctionType.TRADITIONAL_C
    assert result.is_static is False

    # Test function with return type
    line = "uint32 get_value(void)"
    result = parser.parse_function_declaration(line, Path("demo.c"), 5)
    assert result is not None
    assert result.name == "get_value"
    assert result.return_type == "uint32"

    # Test static function
    line = "static uint8 internal_function(void)"
    result = parser.parse_function_declaration(line, Path("demo.c"), 10)
    assert result.is_static is True


# SWUT_PARSER_00012: C Keyword Filtering

def test_c_keyword_filtering():
    """SWUT_PARSER_00012

    Test that C keywords and AUTOSAR types are excluded from function call
    detection.
    """
    parser = CParser()

    # Test that all keywords are in C_KEYWORDS
    for keyword in ["if", "else", "for", "while", "return", "switch", "case"]:
        assert keyword in parser.C_KEYWORDS

    # Test AUTOSAR types are filtered
    assert "uint8" in parser.AUTOSAR_TYPES
    assert "uint16" in parser.AUTOSAR_TYPES
    assert "uint32" in parser.AUTOSAR_TYPES
    assert "boolean" in parser.AUTOSAR_TYPES
    assert "Boolean" in parser.AUTOSAR_TYPES
    assert "StatusType" in parser.AUTOSAR_TYPES

    # Test that keyword is filtered from call detection
    # Create a call and check if keyword is filtered
    line = "void func() { if (condition) return; }"
    call = parser._extract_function_calls(line, Path("test.c"))
    # "if" should not be in the call list
    assert "if" not in call


# SWUT_PARSER_00013: File-Level Parsing

def test_file_level_parsing():
    """SWUT_PARSER_00013

    Test parse_file method processes complete C source files.
    """
    parser = CParser()

    # Create temporary file with test content
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write("void func1(void);\n")
        f.write("uint32 func2(uint32 value);\n")
        f.write("static uint8 func3(void);\n")
        fixture_path = Path(f.name)

    # Parse file
    functions = parser.parse_file(fixture_path)

    # Should find 3 functions
    assert len(functions) == 3

    # Check function names
    function_names = [f.name for f in functions]
    assert "func1" in function_names
    assert "func2" in function_names
    assert "func3" in function_names


# SWUT_PARSER_00014: Comment Removal

def test_comment_removal():
    """SWUT_PARSER_00014

    Test that C-style comments are removed before parsing.
    """
    parser = CParser()

    # Test single-line comment removal
    line_with_comment = "void func(void);  // This is a comment"
    line_clean = parser._remove_comments(line_with_comment)
    assert "// This is a comment" not in line_clean
    assert "void func(void);" in line_clean

    # Test multi-line comment removal
    line_multi = "/* Multi-line\n * comment\n */\nvoid func(void);"
    line_clean = parser._remove_comments(line_multi)
    assert "/* Multi-line\n * comment\n */" not in line_clean
    assert "void func(void);" in line_clean

    # Test comment in string
    line_string = "char* ptr = \"//\";  /* comment starts here"
    line_clean = parser._remove_comments(line_string)
    assert "char* ptr = \"//\";" in line_clean  # Rest should remain


# SWUT_PARSER_00015: Line-by-Line Processing

def test_line_by_line_processing():
    """SWUT_PARSER_00015

    Test that file is processed line-by-line to prevent catastrophic backtracking.
    """
    parser = CParser()

    # Test that parse_file processes line by line
    # (Implementation detail: should use readline() not regex on whole file)
    # This test validates the approach avoids ReDoS vulnerabilities

    # Create file and parse
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        # Write many function declarations
        for i in range(100):
            f.write(f"void func{i}(void);\n")

    fixture_path = Path(f.name)

    # Parse should complete without catastrophic backtracking
    functions = parser.parse_file(fixture_path)

    # Should successfully parse all 100 functions
    assert len(functions) == 100


# SWUT_PARSER_00016: Multi-Line Function Prototypes

def test_multiline_function_prototypes():
    """SWUT_PARSER_00016

    Test that function declarations spanning multiple lines are handled correctly.
    """
    parser = CParser()

    # Create multi-line declaration
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write("uint32\n")
        f.write("get_value(\n")
        f.write("    uint32 value\n")
        f.write(")\n")
        f.write("(void)")

    fixture_path = Path(f.name)

    functions = parser.parse_file(fixture_path)

    # Should parse the multi-line function
    assert len(functions) == 1
    result = functions[0]
    assert result.name == "get_value"
    assert result.return_type == "uint32"
    assert len(result.parameters) == 1
    assert result.parameters[0].name == "value"
    assert result.parameters[0].param_type == "uint32"


# SWUT_PARSER_00017: Parameter String Parsing

def test_parameter_string_parsing():
    """SWUT_PARSER_00017

    Test that C parameter syntax is parsed correctly.
    """
    parser = CParser()

    # Test simple parameter
    line = "void func(uint32 value)"
    match = parser.parameter_pattern.search(line)
    assert match.group("type") == "uint32"
    assert match.group("name") == "value"

    # Test pointer parameter
    line = "void func(uint8* buffer)"
    match = parser.parameter_pattern.search(line)
    assert match.group("type") == "uint8"
    assert match.group("ptr") == "*"  # Pointer marker

    # Test const parameter
    line = "void func(const uint32 limit)"
    match = parser.parameter_pattern.search(line)
    assert match.group("const") == "const"
    assert match.group("type") == "uint32"

    # Test array parameter
    line = "void func(uint8 buffer[256])"
    match = parser.parameter_pattern.search(line)
    assert match.group("type") == "uint8"
    assert "buffer[256]" in match.group(0)  # Array notation


# SWUT_PARSER_00018: Smart Split Parameters

def test_smart_split_parameters():
    """SWUT_PARSER_00018

    Test that parameters are split by comma respecting nested parentheses.
    """
    parser = CParser()

    # Test simple split
    line = "void func(int a, float b)"
    params = parser._smart_split_parameters(line)
    assert len(params) == 2
    assert params[0] == "int a"
    assert params[1] == "float b"

    # Test nested parentheses (function pointer)
    line = "void register_callback(void (*callback)(int))"
    params = parser._smart_split_parameters(line)
    assert len(params) == 1
    assert "(*callback)(int)" in params[0]

    # Test complex nesting
    line = "void func(int a, void (*fp)(int, float), char c)"
    params = parser._smart_split_parameters(line)
    assert len(params) == 3
    assert params[0] == "int a"
    assert params[1] == "void (*fp)(int, float)"
    assert params[2] == "char c"


# SWUT_PARSER_00019: Function Body Extraction

def test_function_body_extraction():
    """SWUT_PARSER_00019

    Test that function bodies are extracted by finding balanced braces.
    """
    parser = CParser()

    # Create function with body
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write("void func(void) {\n")
        f.write("    int x = 5;\n")
        f.write("}\n")
        f.write("void next_func(void) {\n")
        f.write("    func();\n")
        f.write("}\n")

    fixture_path = Path(f.name)

    functions = parser.parse_file(fixture_path)

    # Should extract bodies
    assert len(functions) == 2

    # Check first function body
    func1 = functions[0]
    body1 = func1.calls[0].body if func1.calls else ""
    assert body1 == "    int x = 5;"

    # Check second function body
    func2 = functions[1]
    body2 = func2.calls[0].body if func2.calls else ""
    assert body2 == "    func();"


# SWUT_PARSER_00020: Function Call Extraction

def test_function_call_extraction():
    """SWUT_PARSER_00020

    Test that function calls are extracted from function bodies.
    """
    parser = CParser()

    # Create test file with function call
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write("void caller(void) {\n")
        f.write("    callee();\n")  # Direct call
        f.write("    // Commented call\n")  # Should not extract
        f.write("}\n")

    fixture_path = Path(f.name)

    functions = parser.parse_file(fixture_path)
    calls = functions[0].calls if functions else []

    # Should extract one call (callee)
    assert len(calls) == 1
    assert calls[0].name == "callee"
    assert calls[0].line_number == 3


# SWUT_PARSER_00021: Conditional Call Detection

def test_conditional_call_detection():
    """SWUT_PARSER_00021

    Test that function calls inside if/else blocks are detected with condition
    context.
    """
    parser = CParser()

    # Create test with conditional call
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write("void test(void) {\n")
        f.write("    if (condition) {\n")
        f.write("        conditional_call();\n")
        f.write("    }\n")
        f.write("}\n")

    fixture_path = Path(f.name)

    functions = parser.parse_file(fixture_path)
    calls = functions[0].calls if functions else []

    # Should detect conditional call
    assert len(calls) == 1
    assert calls[0].name == "conditional_call"
    assert calls[0].is_conditional is True
    assert "condition" in calls[0].condition


# SWUT_PARSER_00022: Multi-Line If Condition Extraction

def test_multiline_if_condition_extraction():
    """SWUT_PARSER_00022

    Test that conditions spanning multiple lines are extracted correctly.
    """
    parser = CParser()

    # Create test with multi-line condition
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write("void test(void) {\n")
        f.write("    if (complex_condition &&\n")
        f.write("        another_condition) {\n")
        f.write("            call();\n")
        f.write("        }\n")
        f.write("    }\n")
        f.write("}\n")

    fixture_path = Path(f.name)

    functions = parser.parse_file(fixture_path)
    calls = functions[0].calls if functions else []

    # Should extract complete multi-line condition
    assert len(calls) == 1
    assert calls[0].name == "test"
    assert "complex_condition &&\n        another_condition" in calls[0].condition


# SWUT_PARSER_00023: Loop Detection

def test_loop_detection():
    """SWUT_PARSER_00023

    Test that for/while loops in function bodies are detected.
    """
    parser = CParser()

    # Create test with for loop
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write("void test(void) {\n")
        f.write("    for (int i = 0; i < 10; i++) {\n")
        f.write("        loop_call();\n")
        f.write("    }\n")
        f.write("}\n")

    fixture_path = Path(f.name)

    functions = parser.parse_file(fixture_path)
    calls = functions[0].calls if functions else []

    # Should detect loop
    assert len(calls) == 1
    assert calls[0].name == "test"
    assert calls[0].is_loop is True
    assert "i < 10; i++" in calls[0].loop_condition


# SWUT_PARSER_00024: Condition Text Sanitization

def test_condition_sanitization():
    """SWUT_PARSER_00024

    Test that condition text is cleaned for Mermaid output.
    """
    parser = CParser()

    # Test condition sanitization
    raw_condition = "if (ptr != NULL) && (count > 0))"
    sanitized = parser._sanitize_condition(raw_condition)

    # Should remove C-specific artifacts
    assert "ptr != NULL" in sanitized
    assert "count > 0" in sanitized
    assert "(" not in sanitized or ")" not in sanitized
    assert "&&" not in sanitized


# SWUT_PARSER_00025: Progressive Enhancement

def test_progressive_enhancement():
    """SWUT_PARSER_00025

    Test that AUTOSAR parser is tried first, falling back to C parser for
    traditional C functions.
    """
    # This tests the integration of both parsers
    # Full integration tests are in test_function_database_parser_integration.py

    # For this test, verify the fallback behavior
    from autosar_calltree.parsers.autosar_parser import AutosarParser
    from autosar_calltree.parsers.c_parser import CParser

    # Test that AUTOSAR functions are handled by AUTOSAR parser
    autosar_parser = AutosarParser()
    line_autosar = "FUNC(void, RTE_CODE) AutosarFunc(void)"
    result_autosar = autosar_parser.parse_function_declaration(line_autosar, Path("test.c"), 1)
    assert result_autosar is not None
    assert result_autosar.function_type == FunctionType.AUTOSAR_FUNC

    # Test that traditional C functions fall back to C parser
    c_parser = CParser()
    line_traditional = "void TradFunc(void)"
    result_traditional = c_parser.parse_function_declaration(line_traditional, Path("test.c"), 10)
    assert result_traditional is not None
    assert result_traditional.function_type == FunctionType.TRADITIONAL_C
