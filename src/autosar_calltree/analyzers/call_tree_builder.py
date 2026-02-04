"""
Call tree analyzer module.

This module builds call trees by performing depth-first traversal
of function calls, detecting cycles, and collecting statistics.
"""

from pathlib import Path
from typing import List, Set

from ..database.function_database import FunctionDatabase
from ..database.models import (
    AnalysisResult,
    AnalysisStatistics,
    CallTreeNode,
    CircularDependency,
    FunctionInfo,
)


class CallTreeBuilder:
    """
    Builds call trees by traversing function calls.

    This class performs depth-first search through function calls,
    respects maximum depth limits, detects circular dependencies,
    and builds a hierarchical tree structure.
    """

    def __init__(self, function_db: FunctionDatabase):
        """
        Initialize the call tree builder.

        Args:
            function_db: Function database to use for lookups
        """
        self.function_db = function_db
        self.visited_functions: Set[str] = set()
        self.call_stack: List[str] = []
        self.circular_dependencies: List[CircularDependency] = []
        self.max_depth_reached = 0
        self.total_nodes = 0

    def build_tree(
        self, start_function: str, max_depth: int = 3, verbose: bool = False
    ) -> AnalysisResult:
        """
        Build a call tree starting from a function.

        Args:
            start_function: Name of the function to start from
            max_depth: Maximum depth to traverse
            verbose: Print progress information

        Returns:
            AnalysisResult containing the call tree and metadata
        """
        # Reset state
        self.visited_functions.clear()
        self.call_stack.clear()
        self.circular_dependencies.clear()
        self.max_depth_reached = 0
        self.total_nodes = 0

        if verbose:
            print(f"Building call tree for: {start_function}")
            print(f"Max depth: {max_depth}")

        # Lookup start function
        start_functions = self.function_db.lookup_function(start_function)

        if not start_functions:
            # Function not found
            if verbose:
                print(f"Error: Function '{start_function}' not found in database")

            return AnalysisResult(
                root_function=start_function,
                call_tree=None,
                circular_dependencies=[],
                statistics=AnalysisStatistics(
                    total_functions=0,
                    max_depth_reached=0,
                    circular_dependencies_found=0,
                    unique_functions=0,
                ),
                errors=[f"Function '{start_function}' not found"],
            )

        # Use first match (or disambiguate if multiple found)
        start_func_info = start_functions[0]

        if len(start_functions) > 1 and verbose:
            print(
                f"Warning: Multiple definitions found for '{start_function}', using first match"
            )
            for func in start_functions:
                print(f"  - {func.file_path}:{func.line_number}")

        # Build the tree
        call_tree = self._build_tree_recursive(
            func_info=start_func_info,
            current_depth=0,
            max_depth=max_depth,
            verbose=verbose,
        )

        # Compute statistics
        unique_functions = len(self.visited_functions)

        statistics = AnalysisStatistics(
            total_functions=self.total_nodes,
            max_depth_reached=self.max_depth_reached,
            circular_dependencies_found=len(self.circular_dependencies),
            unique_functions=unique_functions,
        )

        if verbose:
            print("\nAnalysis complete:")
            print(f"  - Total nodes: {self.total_nodes}")
            print(f"  - Unique functions: {unique_functions}")
            print(f"  - Max depth reached: {self.max_depth_reached}")
            print(f"  - Circular dependencies: {len(self.circular_dependencies)}")

        return AnalysisResult(
            root_function=start_function,
            call_tree=call_tree,
            circular_dependencies=self.circular_dependencies,
            statistics=statistics,
            errors=[],
        )

    def _build_tree_recursive(
        self,
        func_info: FunctionInfo,
        current_depth: int,
        max_depth: int,
        verbose: bool = False,
    ) -> CallTreeNode:
        """
        Recursively build call tree using depth-first search.

        Args:
            func_info: Current function information
            current_depth: Current depth in the tree
            max_depth: Maximum depth to traverse
            verbose: Print progress information

        Returns:
            CallTreeNode for current function
        """
        self.total_nodes += 1

        # Track maximum depth
        if current_depth > self.max_depth_reached:
            self.max_depth_reached = current_depth

        # Create qualified name for cycle detection
        qualified_name = self._get_qualified_name(func_info)

        # Check for circular dependency
        if qualified_name in self.call_stack:
            cycle_start_idx = self.call_stack.index(qualified_name)
            cycle = self.call_stack[cycle_start_idx:] + [qualified_name]

            circular_dep = CircularDependency(cycle=cycle, depth=current_depth)
            self.circular_dependencies.append(circular_dep)

            if verbose:
                print(f"  {'  ' * current_depth}Cycle detected: {' -> '.join(cycle)}")

            # Return node without children
            return CallTreeNode(
                function_info=func_info,
                depth=current_depth,
                children=[],
                is_recursive=True,
            )

        # Add to visited set and call stack
        self.visited_functions.add(qualified_name)
        self.call_stack.append(qualified_name)

        # Check depth limit
        if current_depth >= max_depth:
            if verbose:
                print(f"  {'  ' * current_depth}{func_info.name} (max depth reached)")

            self.call_stack.pop()
            return CallTreeNode(
                function_info=func_info,
                depth=current_depth,
                children=[],
                is_recursive=False,
            )

        if verbose:
            indent = "  " * current_depth
            print(
                f"{indent}{func_info.name} ({func_info.file_path}:{func_info.line_number})"
            )

        # Build children nodes
        children = []

        for func_call in func_info.calls:
            called_func_name = func_call.name
            is_conditional = func_call.is_conditional

            # Lookup called function
            called_funcs = self.function_db.lookup_function(
                called_func_name, context_file=str(func_info.file_path)
            )

            if not called_funcs:
                # Function not found - might be external or library function
                if verbose:
                    print(
                        f"  {'  ' * (current_depth + 1)}{called_func_name} (not found)"
                    )
                continue

            # Use first match (prefer function from same file for static functions)
            called_func_info = called_funcs[0]

            # Recursively build child node
            child_node = self._build_tree_recursive(
                func_info=called_func_info,
                current_depth=current_depth + 1,
                max_depth=max_depth,
                verbose=verbose,
            )

            # Mark as optional if it's conditional
            if is_conditional:
                child_node.is_optional = True
                child_node.condition = func_call.condition

            children.append(child_node)

        # Remove from call stack
        self.call_stack.pop()

        return CallTreeNode(
            function_info=func_info,
            depth=current_depth,
            children=children,
            is_recursive=False,
        )

    def _get_qualified_name(self, func_info: FunctionInfo) -> str:
        """
        Get qualified name for a function (file::function).

        Args:
            func_info: Function information

        Returns:
            Qualified name string
        """
        file_stem = Path(func_info.file_path).stem
        return f"{file_stem}::{func_info.name}"

    def get_all_functions_in_tree(self, root: CallTreeNode) -> List[FunctionInfo]:
        """
        Get all unique functions in a call tree.

        Args:
            root: Root node of call tree

        Returns:
            List of all FunctionInfo objects in tree
        """
        functions = []
        seen = set()

        def traverse(node: CallTreeNode):
            qualified_name = self._get_qualified_name(node.function_info)
            if qualified_name not in seen:
                seen.add(qualified_name)
                functions.append(node.function_info)

            for child in node.children:
                traverse(child)

        traverse(root)
        return functions

    def get_tree_depth(self, root: CallTreeNode) -> int:
        """
        Get the maximum depth of a call tree.

        Args:
            root: Root node of call tree

        Returns:
            Maximum depth
        """
        if not root.children:
            return root.depth

        max_child_depth = max(self.get_tree_depth(child) for child in root.children)

        return max_child_depth

    def get_leaf_nodes(self, root: CallTreeNode) -> List[CallTreeNode]:
        """
        Get all leaf nodes (functions that don't call anything) in tree.

        Args:
            root: Root node of call tree

        Returns:
            List of leaf CallTreeNode objects
        """
        leaves = []

        def traverse(node: CallTreeNode):
            if not node.children:
                leaves.append(node)
            else:
                for child in node.children:
                    traverse(child)

        traverse(root)
        return leaves

    def print_tree_text(self, root: CallTreeNode, show_file: bool = True) -> str:
        """
        Generate a text representation of the call tree.

        Args:
            root: Root node of call tree
            show_file: Whether to show file paths

        Returns:
            Text representation as string
        """
        lines = []

        def traverse(node: CallTreeNode, prefix: str = "", is_last: bool = True):
            # Build line for current node
            connector = "└── " if is_last else "├── "

            func_name = node.function_info.name
            if show_file:
                file_name = Path(node.function_info.file_path).name
                line = f"{prefix}{connector}{func_name} ({file_name}:{node.function_info.line_number})"
            else:
                line = f"{prefix}{connector}{func_name}"

            if node.is_recursive:
                line += " [RECURSIVE]"

            lines.append(line)

            # Build lines for children
            if node.children:
                new_prefix = prefix + ("    " if is_last else "│   ")
                for idx, child in enumerate(node.children):
                    is_last_child = idx == len(node.children) - 1
                    traverse(child, new_prefix, is_last_child)

        # Start with root (no prefix)
        func_name = root.function_info.name
        if show_file:
            file_name = Path(root.function_info.file_path).name
            lines.append(f"{func_name} ({file_name}:{root.function_info.line_number})")
        else:
            lines.append(func_name)

        # Add children
        for idx, child in enumerate(root.children):
            is_last = idx == len(root.children) - 1
            traverse(child, "", is_last)

        return "\n".join(lines)
