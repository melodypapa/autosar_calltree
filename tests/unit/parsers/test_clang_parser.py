"""Tests for parsers/clang_parser.py"""

import tempfile
from pathlib import Path
from autosar_calltree.parsers.clang_parser import ClangParser
from autosar_calltree.database.models import FunctionInfo


def test_clang_parser_initialization():
    """Test that ClangParser initializes correctly."""
    parser = ClangParser()
    assert parser is not None
    assert parser.index is not None


def test_clang_parser_extract_simple_function():
    """Test that ClangParser extracts a simple function."""
    parser = ClangParser()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write("""
void simple_function(void) {
}
""")
        fixture_path = Path(f.name)
    
    functions = parser.parse_file(fixture_path)
    
    assert len(functions) == 1
    assert isinstance(functions[0], FunctionInfo)
    assert functions[0].name == 'simple_function'
    assert functions[0].return_type == 'void'


def test_clang_parser_extract_parameters():
    """Test that ClangParser extracts function parameters."""
    parser = ClangParser()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write("""
int add(int a, int b) {
    return a + b;
}
""")
        fixture_path = Path(f.name)
    
    functions = parser.parse_file(fixture_path)
    
    assert len(functions) == 1
    assert functions[0].name == 'add'
    assert len(functions[0].parameters) == 2
    assert functions[0].parameters[0].name == 'a'
    assert functions[0].parameters[0].param_type == 'int'
    assert functions[0].parameters[1].name == 'b'
    assert functions[0].parameters[1].param_type == 'int'


def test_clang_parser_extract_function_calls():
    """Test that ClangParser extracts function calls."""
    parser = ClangParser()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write("""
void helper1(void) {}
void helper2(void) {}

void caller(void) {
    helper1();
    helper2();
}
""")
        fixture_path = Path(f.name)
    
    functions = parser.parse_file(fixture_path)
    
    caller_func = [f for f in functions if f.name == 'caller'][0]
    assert len(caller_func.calls) == 2
    call_names = [c.name for c in caller_func.calls]
    assert 'helper1' in call_names
    assert 'helper2' in call_names
