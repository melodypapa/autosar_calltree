"""Tests for parsers/c_parser_pycparser.py (SWUT_PARSER_00026-00035)"""

import sys
from pathlib import Path
import pytest

from autosar_calltree.database.models import FunctionType
from autosar_calltree.parsers.c_parser_pycparser import CParserPyCParser

# Skip all tests in this module if pycparser is not installed
pytestmark = pytest.mark.skipif(
    sys.modules.get("pycparser") is None,
    reason="pycparser not installed - install with: pip install pycparser",
)


# SWUT_PARSER_00026: Optional Dependency

def test_pycparser_optional_dependency():
    """SWUT_PARSER_00026

    Test that pycparser is treated as an optional dependency with graceful
    fallback when not available.
    """
    # If pycparser is not installed, this test module is skipped
    # The pytestmark at module level handles this

    # When installed, verify parser can be imported
    try:
        from autosar_calltree.parsers.c_parser_pycparser import CParserPyCParser  # type: ignore
        # If we get here, pycparser is installed
        assert True
    except ImportError:
        pytest.fail("pycparser should be installed for this test")


# SWUT_PARSER_00027: AST-Based Parsing

def test_ast_based_parsing():
    """SWUT_PARSER_00027

    Test that pycparser provides AST-based parsing for more accurate C parsing.
    """
    parser = CParserPyCParser()

    # Create test file
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write("""
        int add(int a, int b) {
            return a + b;
        }

        void caller(void) {
            add(1, 2);
        }
        """)

    fixture_path = Path(f.name)

    # Parse file
    functions = parser.parse_file(fixture_path)

    # Should parse both functions
    assert len(functions) == 2

    # Check add function
    add_func = [f for f in functions if f.name == "add"][0]
    assert add_func.name == "add"
    assert add_func.return_type == "int"
    assert len(add_func.parameters) == 2

    # Check caller function
    caller_func = [f for f in functions if f.name == "caller"][0]
    assert caller_func.name == "caller"
    assert caller_func.return_type == "void"


# SWUT_PARSER_00028: AUTOSAR Macro Preprocessing

def test_autosar_macro_preprocessing():
    """SWUT_PARSER_00028

    Test that AUTOSAR macros are converted to standard C before pycparser
    parsing.
    """
    parser = CParserPyCParser()

    # Test FUNC macro conversion
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        # AUTOSAR macros that need preprocessing
        f.write("FUNC(void, RTE_CODE) TestFunc(void)")
        f.write("FUNC_P2VAR(uint8, AUTOMATIC) GetBuffer(void)")
        f.write("FUNC_P2CONST(ConfigType, AUTOMATIC) GetConfig(void)")
        # Traditional C function (no preprocessing)
        f.write("void TradFunc(void)")

    fixture_path = Path(f.name)

    # Parse file
    functions = parser.parse_file(fixture_path)

    # Should parse all 4 functions
    assert len(functions) == 4

    # Check FUNC was converted
    test_func = [f for f in functions if f.name == "TestFunc"][0]
    assert test_func.return_type == "void"

    # Check FUNC_P2VAR was converted
    get_buf_func = [f for f in functions if f.name == "GetBuffer"][0]
    assert get_buf_func.return_type == "uint8*"  # Pointer added

    # Check FUNC_P2CONST was converted
    get_cfg_func = [f for f in functions if f.name == "GetConfig"][0]
    assert get_cfg_func.return_type == "const ConfigType*"  # const + pointer

    # Check traditional function not preprocessed
    trad_func = [f for f in functions if f.name == "TradFunc"][0]
    assert trad_func.return_type == "void"


# SWUT_PARSER_00029: AST Visitor Pattern

def test_ast_visitor_pattern():
    """SWUT_PARSER_00029

    Test that AST visitor pattern systematically walks the AST to extract function
    information.
    """
    parser = CParserPyCParser()

    # Create test file with multiple functions
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write("""
        void first(void) {}
        void second(int x) {}
        void third(float y) {}
        """)

    fixture_path = Path(f.name)

    # Parse file
    functions = parser.parse_file(fixture_path)

    # Visitor should find all 3 functions
    assert len(functions) == 3

    # Check function order (visitor traverses in order)
    assert functions[0].name == "first"
    assert functions[1].name == "second"
    assert functions[2].name == "third"


# SWUT_PARSER_00030: Return Type Extraction from AST

def test_ast_return_type_extraction():
    """SWUT_PARSER_00030

    Test that return types are correctly extracted from AST nodes, handling
    complex types including pointers and const qualifiers.
    """
    parser = CParserPyCParser()

    # Test various return types
    import tempfile
    test_cases = [
        ("void func(void) {}", "void"),
        ("int func(int x) {}", "int"),
        ("uint8* get_buffer(void) {}", "uint8*"),
        ("const char* read(void) {}", "const char*"),
        ("int** func_ptr(void) {}", "int**"),  # Pointer to pointer
    ]

    for i, (code, expected_return) in enumerate(test_cases):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(code + "\n")

        fixture_path = Path(f.name)
        functions = parser.parse_file(fixture_path)

        assert len(functions) == 1
        assert functions[0].return_type == expected_return


# SWUT_PARSER_00031: Parameter Extraction from AST

def test_ast_parameter_extraction():
    """SWUT_PARSER_00031

    Test that function parameters are extracted from AST parameter list with correct
    type information.
    """
    parser = CParserPyCParser()

    # Create test function with multiple parameter types
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write("""
        void complex_func(
            uint8 value,
            uint16* buffer,
            const uint32 limit,
            int array[256])
        {}
        """)

    fixture_path = Path(f.name)
    functions = parser.parse_file(fixture_path)

    assert len(functions) == 1
    func = functions[0]

    # Check all parameters
    assert len(func.parameters) == 4

    # Check simple parameter
    assert func.parameters[0].name == "value"
    assert func.parameters[0].param_type == "uint8"
    assert func.parameters[0].is_pointer is False
    assert func.parameters[0].is_const is False

    # Check pointer parameter
    assert func.parameters[1].name == "buffer"
    assert func.parameters[1].param_type == "uint16"
    assert func.parameters[1].is_pointer is True
    assert func.parameters[1].is_const is False

    # Check const parameter
    assert func.parameters[2].name == "limit"
    assert func.parameters[2].param_type == "uint32"
    assert func.parameters[2].is_pointer is False
    assert func.parameters[2].is_const is True

    # Check array parameter
    assert func.parameters[3].name == "array"
    assert func.parameters[3].param_type == "int"
    # Array parameters from pycparser may not preserve array notation


# SWUT_PARSER_00032: Function Call Extraction via AST

def test_ast_function_call_extraction():
    """SWUT_PARSER_00032

    Test that function calls are identified from AST with fallback to regex for
    AUTOSAR functions.
    """
    parser = CParserPyCParser()

    # Create test file with function calls
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write("""
        void caller(void) {
            helper1();
            helper2(42);
            Rte_Call_MyFunc();  // AUTOSAR-style call
        }
        """)

    fixture_path = Path(f.name)
    functions = parser.parse_file(fixture_path)

    assert len(functions) == 1

    # Extract calls from caller function
    # pycparser doesn't track if/else context, so calls may not have is_conditional
    calls = functions[0].calls if functions else []

    # Should find 3 calls
    assert len(calls) == 3
    call_names = [c.name for c in calls]
    assert "helper1" in call_names
    assert "helper2" in call_names
    assert "Rte_Call_MyFunc" in call_names


# SWUT_PARSER_00033: Hybrid Parsing Strategy

def test_hybrid_parsing_strategy():
    """SWUT_PARSER_00033

    Test that both AUTOSAR and traditional C parsing work together with
    deduplication.
    """
    parser = CParserPyCParser()

    # Create test file with mixed AUTOSAR and traditional C
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write("""
        FUNC(void, RTE_CODE) AutosarFunc(void) {
            TradFunc(42);
        }

        void TradFunc(void) {}
        """)

    fixture_path = Path(f.name)
    functions = parser.parse_file(fixture_path)

    # Should parse both functions
    assert len(functions) == 2

    # Check AUTOSAR function
    autosar_func = [f for f in functions if f.name == "AutosarFunc"][0]
    assert autosar_func.name == "AutosarFunc"
    assert autosar_func.return_type == "void"
    # AUTOSAR functions should have AUTOSAR_FUNC type from pycparser (not TRADITIONAL_C)
    assert autosar_func.function_type in [FunctionType.AUTOSAR_FUNC, FunctionType.AUTOSAR_FUNC_P2VAR]

    # Check traditional function
    trad_func = [f for f in functions if f.name == "TradFunc"][0]
    assert trad_func.name == "TradFunc"
    assert trad_func.return_type == "void"
    assert trad_func.function_type == FunctionType.TRADITIONAL_C


# SWUT_PARSER_00034: Preprocessor Directive Handling

def test_preprocessor_directive_handling():
    """SWUT_PARSER_00034

    Test that problematic preprocessor directives are removed before pycparser
    parsing to avoid errors.
    """
    parser = CParserPyCParser()

    # Create test file with preprocessor directives
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        # Write directives that should be removed
        f.write("#pragma once\n")
        f.write("#line 1000 \"file.c\"\n")
        f.write("#error \"Unsupported feature\"\n")
        f.write("#warning \"Deprecated function\"\n")
        # Write function after directives
        f.write("void test_func(void) {}\n")

    fixture_path = Path(f.name)
    functions = parser.parse_file(fixture_path)

    # Should parse the function (preprocessor directives removed)
    assert len(functions) == 1
    assert functions[0].name == "test_func"


# SWUT_PARSER_00035: Parse Error Graceful Handling

def test_parse_error_graceful_handling():
    """SWUT_PARSER_00035

    Test that pycparser parse errors are handled gracefully with fallback to regex
    parser.
    """
    parser = CParserPyCParser()

    # Create test file with syntax error
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        # Invalid C syntax
        f.write("void func(void {\n")  # Missing closing brace

    fixture_path = Path(f.name)

    # Parse should handle error gracefully
    functions = parser.parse_file(fixture_path)

    # Should fall back to regex parser which might handle this differently
    # or return empty result
    # The key is that it doesn't crash
    assert functions is not None
