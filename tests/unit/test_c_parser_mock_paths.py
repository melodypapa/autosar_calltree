"""Tests using mock to force specific code paths in c_parser.py.

This file uses unittest.mock to trigger hard-to-reach code paths.
"""

from pathlib import Path
from unittest.mock import MagicMock

from autosar_calltree.parsers.c_parser import CParser


def test_line_440_with_mock():
    """Test line 440: return_type starts with '#' using mock."""
    parser = CParser()

    # Create a mock match that returns '#define' as the return_type
    mock_match = MagicMock()
    mock_match.group.side_effect = lambda x: {
        "static": None,
        "inline": None,
        "return_type": "#define",
        "function_name": "test_func",
        "params": "int x"
    }.get(x)

    result = parser._parse_function_match(mock_match, "#define test_func(int x)", Path("test.c"))
    # Should return None because return_type starts with '#'
    assert result is None


def test_line_458_with_mock():
    """Test line 458: function_name in control structures using mock."""
    parser = CParser()

    # Create a mock match that returns 'if' as the function_name
    mock_match = MagicMock()
    mock_match.group.side_effect = lambda x: {
        "static": None,
        "inline": None,
        "return_type": "void",
        "function_name": "if",
        "params": "int x"
    }.get(x)

    result = parser._parse_function_match(mock_match, "void if(int x)", Path("test.c"))
    # Should return None because 'if' is a control structure
    assert result is None


def test_line_442_return_type_is_c_keyword():
    """Test line 442: return_type in C_KEYWORDS using mock."""
    parser = CParser()

    # Create a mock match that returns 'return' as the return_type
    mock_match = MagicMock()
    mock_match.group.side_effect = lambda x: {
        "static": None,
        "inline": None,
        "return_type": "return",
        "function_name": "test_func",
        "params": "int x"
    }.get(x)

    result = parser._parse_function_match(mock_match, "return test_func(int x)", Path("test.c"))
    # Should return None because 'return' is a C keyword
    assert result is None


def test_line_734_750_else_if_multiline_with_mock():
    """Test lines 734-750: else if multiline condition using mock."""
    parser = CParser()

    # Create a file with else if
    with open("/tmp/test_line_734.c", "w") as f:
        f.write("""
void test(void)
{
    if (x > 0) {
        func1();
    } else if (x < 0 && (y > 0
        && z < 0)) {
        func2();
    }
}
""")

    functions = parser.parse_file(Path("/tmp/test_line_734.c"))
    # Should parse without crashing
    assert len(functions) >= 1


def test_line_766_else_if_fallback_with_mock():
    """Test line 766: else if fallback using mock."""
    parser = CParser()

    # Create a file with malformed else if
    with open("/tmp/test_line_766.c", "w") as f:
        f.write("""
void test(void)
{
    if (x > 0) {
        func1();
    } else if x < 0 {
        func2();
    }
}
""")

    functions = parser.parse_file(Path("/tmp/test_line_766.c"))
    # Should parse without crashing
    assert len(functions) >= 1


def test_line_805_806_while_fallback_with_mock():
    """Test lines 805-806: while loop fallback using mock."""
    parser = CParser()

    # Create a file with malformed while
    with open("/tmp/test_line_805.c", "w") as f:
        f.write("""
void test(void)
{
    while x < 10 {
        func();
    }
}
""")

    functions = parser.parse_file(Path("/tmp/test_line_805.c"))
    # Should parse without crashing
    assert len(functions) >= 1


def test_line_875_rte_condition_with_mock():
    """Test line 875: RTE call condition update using mock."""
    parser = CParser()

    # Create a file with RTE call in different contexts
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


def test_line_879_881_rte_loop_with_mock():
    """Test lines 879-881: RTE call loop condition using mock."""
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