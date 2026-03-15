"""Tests for tree formatter utility."""

from pathlib import Path

import pytest

from autosar_calltree.database.models import (
    CallTreeNode,
    FunctionInfo,
    FunctionType,
)
from autosar_calltree.utils.tree_formatter import TreeFormatter


@pytest.fixture
def sample_function_info():
    """Create a sample FunctionInfo for testing."""
    return FunctionInfo(
        name="main",
        return_type="void",
        file_path=Path("src/main.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )


@pytest.fixture
def sample_child_function_info():
    """Create a sample child FunctionInfo for testing."""
    return FunctionInfo(
        name="helper",
        return_type="int",
        file_path=Path("src/helper.c"),
        line_number=20,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )


class TestTreeFormatter:
    """Tests for TreeFormatter."""

    def test_format_single_node(self, sample_function_info):
        """Should format a single node without children."""
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[],
        )
        result = TreeFormatter.format_tree(node)
        assert "main (main.c:10)" in result

    def test_format_with_child(self, sample_function_info, sample_child_function_info):
        """Should format node with child."""
        child = CallTreeNode(
            function_info=sample_child_function_info,
            depth=1,
            children=[],
        )
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[child],
        )
        result = TreeFormatter.format_tree(node)
        assert "main (main.c:10)" in result
        assert "helper (helper.c:20)" in result
        assert "└──" in result

    def test_format_multiple_children(self, sample_function_info):
        """Should format multiple children with correct connectors."""
        child1 = CallTreeNode(
            function_info=FunctionInfo(
                name="child1",
                return_type="void",
                file_path=Path("src/a.c"),
                line_number=1,
                is_static=False,
                function_type=FunctionType.TRADITIONAL_C,
            ),
            depth=1,
            children=[],
        )
        child2 = CallTreeNode(
            function_info=FunctionInfo(
                name="child2",
                return_type="void",
                file_path=Path("src/b.c"),
                line_number=2,
                is_static=False,
                function_type=FunctionType.TRADITIONAL_C,
            ),
            depth=1,
            children=[],
        )
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[child1, child2],
        )
        result = TreeFormatter.format_tree(node)
        assert "├── child1" in result
        assert "└── child2" in result

    def test_format_recursive_node(self, sample_function_info):
        """Should mark recursive nodes."""
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[],
            is_recursive=True,
        )
        result = TreeFormatter.format_tree(node)
        assert "[RECURSIVE]" in result

    def test_format_without_file(self, sample_function_info):
        """Should hide file when show_file=False."""
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[],
        )
        result = TreeFormatter.format_tree(node, show_file=False)
        assert "main.c" not in result
        assert "main" in result

    def test_format_without_line(self, sample_function_info):
        """Should hide line number when show_line=False."""
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[],
        )
        result = TreeFormatter.format_tree(node, show_line=False)
        assert ":10" not in result
        assert "main.c" in result

    def test_format_nested_children(self, sample_function_info):
        """Should format nested children with correct indentation."""
        grandchild = CallTreeNode(
            function_info=FunctionInfo(
                name="grandchild",
                return_type="void",
                file_path=Path("src/gc.c"),
                line_number=5,
                is_static=False,
                function_type=FunctionType.TRADITIONAL_C,
            ),
            depth=2,
            children=[],
        )
        child = CallTreeNode(
            function_info=FunctionInfo(
                name="child",
                return_type="void",
                file_path=Path("src/c.c"),
                line_number=3,
                is_static=False,
                function_type=FunctionType.TRADITIONAL_C,
            ),
            depth=1,
            children=[grandchild],
        )
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[child],
        )
        result = TreeFormatter.format_tree(node)
        assert "main" in result
        assert "child" in result
        assert "grandchild" in result
