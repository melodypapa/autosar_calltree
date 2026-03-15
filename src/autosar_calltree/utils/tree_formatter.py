"""
Tree formatter utility for call tree visualization.

This module provides utilities for formatting call trees as
text-based tree diagrams.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..database.models import CallTreeNode


class TreeFormatter:
    """Format call trees as text-based tree diagrams."""

    @staticmethod
    def format_tree(
        root: "CallTreeNode",
        show_file: bool = True,
        show_line: bool = True
    ) -> str:
        """
        Generate text-based tree representation.

        Args:
            root: Root node of call tree
            show_file: Include file name in output
            show_line: Include line number in output

        Returns:
            Formatted tree string
        """
        lines = []

        def format_location(node: "CallTreeNode") -> str:
            """Format file:line location."""
            if not show_file:
                return ""
            file_name = Path(node.function_info.file_path).name
            if show_line:
                return f" ({file_name}:{node.function_info.line_number})"
            return f" ({file_name})"

        def traverse(node: "CallTreeNode", prefix: str = "", is_last: bool = True):
            connector = "└── " if is_last else "├── "

            func_name = node.function_info.name
            location = format_location(node)
            line = f"{prefix}{connector}{func_name}{location}"

            if node.is_recursive:
                line += " [RECURSIVE]"

            lines.append(line)

            if node.children:
                new_prefix = prefix + ("    " if is_last else "│   ")
                for idx, child in enumerate(node.children):
                    is_last_child = idx == len(node.children) - 1
                    traverse(child, new_prefix, is_last_child)

        # Root node (no prefix)
        func_name = root.function_info.name
        location = format_location(root)
        root_line = f"{func_name}{location}"
        if root.is_recursive:
            root_line += " [RECURSIVE]"
        lines.append(root_line)

        for idx, child in enumerate(root.children):
            is_last = idx == len(root.children) - 1
            traverse(child, "", is_last)

        return "\n".join(lines)