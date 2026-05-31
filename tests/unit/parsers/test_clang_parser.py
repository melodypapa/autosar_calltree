"""Tests for parsers/clang_parser.py"""

from pathlib import Path
from autosar_calltree.parsers.clang_parser import ClangParser


def test_clang_parser_initialization():
    """Test that ClangParser initializes correctly."""
    parser = ClangParser()
    assert parser is not None
    assert parser.index is not None
