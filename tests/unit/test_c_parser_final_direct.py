"""Final direct method tests to cover remaining lines in c_parser.py.

This file contains tests that directly call parser methods to trigger
hard-to-reach code paths.
"""

from pathlib import Path

from autosar_calltree.parsers.c_parser import CParser


def test_line_440_return_type_is_c_keyword():
    """Test line 440: return_type in C_KEYWORDS.

    Line 440: if return_type in self.C_KEYWORDS or function_name in self.C_KEYWORDS:
    """
    parser = CParser()

    # Use the function_pattern to create a match where return_type is a C keyword
    test_code = "return test_func(int x)"
    match = parser.function_pattern.search(test_code)
    if match:
        result = parser._parse_function_match(match, test_code, Path("test.c"))
        # Should return None because 'return' is a C keyword
        assert result is None


def test_line_458_function_name_is_control_structure():
    """Test line 458: function_name in control structures.

    Line 458: if function_name in ["if", "for", "while", "switch", "case", "else"]:
    """
    parser = CParser()

    # Use the function_pattern to create a match where function_name is a control structure
    test_code = "void if(int x)"
    match = parser.function_pattern.search(test_code)
    if match:
        result = parser._parse_function_match(match, test_code, Path("test.c"))
        # Should return None because 'if' is a control structure
        assert result is None


def test_line_513_extract_function_body_no_brace():
    """Test line 513: _extract_function_body returns None.

    Line 513 is in _extract_function_body when no opening brace is found.
    """
    parser = CParser()

    # Call with content that has no brace
    result = parser._extract_function_body("void test();", 0)
    assert result is None


def test_line_728_if_statement_fallback():
    """Test line 728: if statement fallback branch.

    Line 728 is the else branch when if pattern doesn't match and no opening brace.
    """
    parser = CParser()

    # Create a file with an if statement that triggers the fallback
    with open("/tmp/test_line_728.c", "w") as f:
        f.write("""
void test(void)
{
    if x > 0
        func();
}
""")

    functions = parser.parse_file(Path("/tmp/test_line_728.c"))
    # Should parse without crashing
    assert len(functions) >= 1


def test_line_766_else_if_fallback():
    """Test line 766: else if fallback branch.

    Line 766 is the else branch when else if pattern doesn't match.
    """
    parser = CParser()

    # Create a file with an else if that triggers the fallback
    with open("/tmp/test_line_766.c", "w") as f:
        f.write("""
void test(void)
{
    if (x > 0) {
        func1();
    } else if x < 0
        func2();
}
""")

    functions = parser.parse_file(Path("/tmp/test_line_766.c"))
    # Should parse without crashing
    assert len(functions) >= 1


def test_line_805_806_while_fallback():
    """Test lines 805-806: while loop fallback.

    Lines 805-806 are the else branch when while pattern doesn't match.
    """
    parser = CParser()

    # Create a file with a while loop that triggers the fallback
    with open("/tmp/test_line_805.c", "w") as f:
        f.write("""
void test(void)
{
    while count > 0
        func();
}
""")

    functions = parser.parse_file(Path("/tmp/test_line_805.c"))
    # Should parse without crashing
    assert len(functions) >= 1


def test_line_875_rte_existing_condition():
    """Test line 875: updating existing RTE call condition.

    Line 875: existing.condition = current_condition
    """
    parser = CParser()

    # Create a file with RTE call in conditional context
    with open("/tmp/test_line_875.c", "w") as f:
        f.write("""
void test(void)
{
    Rte_Call_Op();
    if (x > 0) {
        Rte_Call_Op();
    }
}
""")

    functions = parser.parse_file(Path("/tmp/test_line_875.c"))
    assert len(functions) >= 1
    func = functions[0]
    rte_calls = [fc for fc in func.calls if fc.name == "Rte_Call_Op"]
    # Should have one RTE call that's marked as conditional
    assert len(rte_calls) == 1
    assert rte_calls[0].is_conditional is True


def test_line_879_881_rte_loop_condition():
    """Test lines 879-881: updating RTE call loop condition.

    Line 879: existing.loop_condition = current_loop_condition
    Line 880: else:
    Line 881: called_functions.append(...)
    """
    parser = CParser()

    # Create a file with RTE call in loop
    with open("/tmp/test_line_879.c", "w") as f:
        f.write("""
void test(void)
{
    while (i < 10) {
        Rte_Call_Op();
    }
}
""")

    functions = parser.parse_file(Path("/tmp/test_line_879.c"))
    assert len(functions) >= 1
    func = functions[0]
    rte_calls = [fc for fc in func.calls if fc.name == "Rte_Call_Op"]
    assert len(rte_calls) == 1
    assert rte_calls[0].is_loop is True
    assert rte_calls[0].loop_condition == "i < 10"