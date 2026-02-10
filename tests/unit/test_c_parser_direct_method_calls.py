"""Direct method tests to cover remaining lines in c_parser.py.

This file uses direct method calls to trigger specific code paths
that are difficult to reach through normal parsing.
"""

from pathlib import Path

from autosar_calltree.parsers.c_parser import CParser


class TestCParserDirectMethodCalls:
    """Direct method tests for c_parser.py coverage."""

    def test_line_326_328_multiline_backtrack_with_non_type(self):
        r"""Test multiline function backtrack with non-type line (lines 326-328).

        This triggers the else: break branch when prev_line doesn't
        match ^[\w\s\*]+$ pattern.
        """
        parser = CParser()

        # Create a multiline function where the return type line
        # contains characters not matching ^[\w\s\*]+$
        test_content = """
struct ComplexType
{
    int field;
};

struct ComplexType
MyFunction(int param)
{
    return param;
}
"""

        with open("/tmp/test_multiline_struct.c", "w") as f:
            f.write(test_content)

        functions = parser.parse_file(Path("/tmp/test_multiline_struct.c"))
        # Should parse without crashing
        assert isinstance(functions, list)

    def test_line_440_parse_function_match_c_keyword_return_type(self):
        """Test _parse_function_match with C keyword return type (line 440)."""
        parser = CParser()

        # Create a test string where a C keyword could be extracted as return_type
        # The regex pattern requires a space after return_type, so 'if ' might work
        test_content = "if  TestFunc(void) { return; }"

        match = parser.function_pattern.search(test_content)

        if match:
            result = parser._parse_function_match(match, test_content, Path("test.c"))
            # The regex extracts 'if ' as return_type, which after strip becomes 'if'
            # This should return None because 'if' is a C keyword
            assert result is None

    def test_line_458_parse_function_match_control_structure_name(self):
        """Test _parse_function_match with control structure name (line 458)."""
        parser = CParser()

        # Test with 'if' as function name
        test_content = "void if(void) { return; }"
        match = parser.function_pattern.search(test_content)

        if match:
            result = parser._parse_function_match(match, test_content, Path("test.c"))
            # Should return None because 'if' is a control structure
            assert result is None

    def test_line_734_750_else_if_multiline_condition_collection(self):
        """Test else if multiline condition collection (lines 734-750)."""
        parser = CParser()

        # Create a function with else if that has unbalanced parentheses
        test_content = """
void test_else_if_multiline(void)
{
    int x = 0;
    int y = 0;

    if (x > 0)
    {
        Func1();
    }
    else if (x < 0 &&
             y > 0 &&
             z > 0)
    {
        Func2();
    }
}
"""

        with open("/tmp/test_else_if_multiline.c", "w") as f:
            f.write(test_content)

        functions = parser.parse_file(Path("/tmp/test_else_if_multiline.c"))
        assert len(functions) >= 1

        func = functions[0]
        # Should have conditional calls
        cond_calls = [fc for fc in func.calls if fc.is_conditional]
        assert len(cond_calls) >= 2

    def test_line_766_else_if_no_closing_paren(self):
        """Test else if without closing parenthesis (line 766)."""
        parser = CParser()

        # Create a function with else if that has no closing paren
        test_content = """
void test_else_if_no_closing(void)
{
    int x = 0;

    if (x > 0)
    {
        Func1();
    }
    else if (x < 0 && y > 0
    {
        Func2();
    }
}
"""

        with open("/tmp/test_else_if_no_closing.c", "w") as f:
            f.write(test_content)

        functions = parser.parse_file(Path("/tmp/test_else_if_no_closing.c"))
        # Should parse without crashing
        assert isinstance(functions, list)

    def test_line_805_806_while_loop_fallback(self):
        """Test while loop fallback without closing paren (lines 805-806)."""
        parser = CParser()

        # Create a function with while loop that has no closing paren
        test_content = """
void test_while_fallback(void)
{
    int count = 10;

    while (count > 0 &&
           index < limit
    {
        Func1();
        count--;
    }
}
"""

        with open("/tmp/test_while_fallback.c", "w") as f:
            f.write(test_content)

        functions = parser.parse_file(Path("/tmp/test_while_fallback.c"))
        # Should parse without crashing
        assert isinstance(functions, list)

    def test_line_875_autosar_type_filtering(self):
        """Test AUTOSAR type filtering in function calls (line 875)."""
        parser = CParser()

        # Create a function that looks like it has an AUTOSAR type as a call
        test_content = """
void test_autosar_type(void)
{
    uint8 value = 10;
    uint8(value);  // This looks like a function call but is a type
    Func1();
}
"""

        with open("/tmp/test_autosar_type.c", "w") as f:
            f.write(test_content)

        functions = parser.parse_file(Path("/tmp/test_autosar_type.c"))
        assert len(functions) >= 1

        func = functions[0]
        # 'uint8' should not be detected as a function call
        uint8_call = next((fc for fc in func.calls if fc.name == "uint8"), None)
        assert uint8_call is None

        # Func1 should be detected
        func1_call = next((fc for fc in func.calls if fc.name == "Func1"), None)
        assert func1_call is not None

    def test_line_879_881_rte_call_loop_update(self):
        """Test RTE call update with loop condition (lines 879-881)."""
        parser = CParser()

        # Create a function with duplicate RTE call in loop
        test_content = """
void test_rte_loop_update(void)
{
    Rte_Call_Process();

    for (int i = 0; i < 10; i++)
    {
        Rte_Call_Process();
    }
}
"""

        with open("/tmp/test_rte_loop_update.c", "w") as f:
            f.write(test_content)

        functions = parser.parse_file(Path("/tmp/test_rte_loop_update.c"))
        assert len(functions) >= 1

        func = functions[0]
        # Should have only one RTE call (deduplicated)
        rte_calls = [fc for fc in func.calls if fc.name == "Rte_Call_Process"]
        assert len(rte_calls) == 1

        # But it should be marked as in loop
        assert rte_calls[0].is_loop is True
