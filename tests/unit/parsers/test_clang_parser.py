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
