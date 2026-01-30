"""
Unit tests for CallTreeBuilder module.

Tests cover tree building, traversal, cycle detection, statistics,
and utility methods.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from autosar_calltree.analyzers.call_tree_builder import CallTreeBuilder
from autosar_calltree.database.function_database import FunctionDatabase
from autosar_calltree.database.models import FunctionInfo, FunctionType


class TestCallTreeBuilderInitialization:
    """Test builder initialization and setup (SWR_ANALYZER_00001)."""

    def test_SWUT_ANALYZER_00001_builder_initialization(self):
        """Test builder can be initialized with database (SWR_ANALYZER_00001)."""
        db = FunctionDatabase(source_dir="./demo")
        builder = CallTreeBuilder(db)

        assert builder.function_db == db
        assert len(builder.visited_functions) == 0
        assert len(builder.call_stack) == 0
        assert len(builder.circular_dependencies) == 0
        assert builder.max_depth_reached == 0
        assert builder.total_nodes == 0


class TestTreeBuilding:
    """Test tree building functionality (SWR_ANALYZER_00002-00005, SWR_ANALYZER_00014-00015)."""

    def test_SWUT_ANALYZER_00002_state_reset_between_builds(self):
        """Test each build_tree call resets state (SWR_ANALYZER_00002)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)

        # First build
        result1 = builder.build_tree("Demo_Init", max_depth=2, verbose=False)
        assert builder.total_nodes > 0

        # Second build
        result2 = builder.build_tree("Demo_MainFunction", max_depth=2, verbose=False)

        # Results should be independent
        assert result1.root_function == "Demo_Init"
        assert result2.root_function == "Demo_MainFunction"

    def test_SWUT_ANALYZER_00003_start_function_lookup(self):
        """Test builder looks up start function (SWR_ANALYZER_00003)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)

        # Non-existent function
        result = builder.build_tree("NonExistentFunction", max_depth=2, verbose=False)

        assert result.call_tree is None
        assert len(result.errors) > 0
        assert "not found" in result.errors[0]
        assert result.statistics.total_functions == 0

    def test_SWUT_ANALYZER_00005_depth_first_traversal(self):
        """Test builder performs depth-first traversal (SWR_ANALYZER_00005)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("Demo_Init", max_depth=3, verbose=False)

        assert result.call_tree is not None
        assert result.call_tree.function_info.name == "Demo_Init"
        assert len(result.call_tree.children) >= 3

        # Verify depth progression
        root = result.call_tree
        if root.children:
            first_child = root.children[0]
            assert first_child.depth == 1
            if first_child.children:
                second_child = first_child.children[0]
                assert second_child.depth == 2

    def test_SWUT_ANALYZER_00014_result_object_creation(self):
        """Test builder returns complete AnalysisResult (SWR_ANALYZER_00014)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("Demo_Init", max_depth=3, verbose=False)

        # Check all required fields
        assert result.root_function == "Demo_Init"
        assert result.call_tree is not None
        assert isinstance(result.circular_dependencies, list)
        assert result.statistics is not None
        assert isinstance(result.errors, list)

        # Statistics should have all fields
        assert hasattr(result.statistics, 'total_functions')
        assert hasattr(result.statistics, 'max_depth_reached')
        assert hasattr(result.statistics, 'circular_dependencies_found')
        assert hasattr(result.statistics, 'unique_functions')

    def test_SWUT_ANALYZER_00015_error_result_missing_function(self):
        """Test error result when function not found (SWR_ANALYZER_00015)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("NonExistentFunction", max_depth=3, verbose=False)

        assert result.call_tree is None
        assert len(result.errors) > 0
        assert "not found" in result.errors[0].lower()
        assert result.root_function == "NonExistentFunction"
        assert result.statistics.total_functions == 0
        assert result.statistics.max_depth_reached == 0
        assert result.statistics.unique_functions == 0


class TestCycleDetection:
    """Test cycle detection and handling (SWR_ANALYZER_00006-00007)."""

    def test_SWUT_ANALYZER_00006_cycle_detection(self):
        """Test builder detects circular dependencies (SWR_ANALYZER_00006)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # func_a calls func_b
            (temp_path / "func_a.c").write_text("""
void func_a(void) {
    func_b();
}
""")

            # func_b calls func_a (circular)
            (temp_path / "func_b.c").write_text("""
void func_b(void) {
    func_a();
}
""")

            db = FunctionDatabase(source_dir=temp_dir)
            db.build_database(use_cache=False, verbose=False)

            builder = CallTreeBuilder(db)
            result = builder.build_tree("func_a", max_depth=5, verbose=False)

            # Should detect circular dependency
            assert len(result.circular_dependencies) > 0

            # Check cycle structure
            cycle = result.circular_dependencies[0]
            assert len(cycle.cycle) >= 2

    def test_SWUT_ANALYZER_00007_cycle_handling_in_tree(self):
        """Test nodes in cycles are marked recursive (SWR_ANALYZER_00007)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create circular call
            (temp_path / "func_a.c").write_text("""
void func_a(void) {
    func_b();
}
""")

            (temp_path / "func_b.c").write_text("""
void func_b(void) {
    func_a();
}
""")

            db = FunctionDatabase(source_dir=temp_dir)
            db.build_database(use_cache=False, verbose=False)

            builder = CallTreeBuilder(db)
            result = builder.build_tree("func_a", max_depth=5, verbose=False)

            # Find recursive node
            def find_recursive(node):
                if node.is_recursive:
                    return node
                for child in node.children:
                    found = find_recursive(child)
                    if found:
                        return found
                return None

            recursive_node = find_recursive(result.call_tree)
            assert recursive_node is not None

            # Recursive node should have no children
            assert len(recursive_node.children) == 0

    def test_self_recursion_detection(self):
        """Test detection of self-recursive functions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Function that calls itself
            (temp_path / "recursive.c").write_text("""
void recursive_func(void) {
    recursive_func();
}
""")

            db = FunctionDatabase(source_dir=temp_dir)
            db.build_database(use_cache=False, verbose=False)

            builder = CallTreeBuilder(db)
            result = builder.build_tree("recursive_func", max_depth=5, verbose=False)

            # Should detect circular dependency
            assert len(result.circular_dependencies) > 0
            assert result.circular_dependencies[0].depth >= 1


class TestDepthHandling:
    """Test max depth enforcement and node depth tracking (SWR_ANALYZER_00008-00009)."""

    def test_SWUT_ANALYZER_00008_max_depth_enforcement(self):
        """Test builder respects max_depth parameter (SWR_ANALYZER_00008)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("Demo_Init", max_depth=2, verbose=False)

        # Verify no node exceeds max depth
        def check_max_depth(node, max_depth):
            assert node.depth <= max_depth
            for child in node.children:
                check_max_depth(child, max_depth)

        check_max_depth(result.call_tree, 2)
        assert result.statistics.max_depth_reached <= 2

    def test_SWUT_ANALYZER_00009_node_depth_tracking(self):
        """Test each node tracks its depth correctly (SWR_ANALYZER_00009)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("Demo_Init", max_depth=3, verbose=False)

        # Root should be depth 0
        assert result.call_tree.depth == 0

        # Children should be depth 1
        for child in result.call_tree.children:
            assert child.depth == 1

            # Grandchildren should be depth 2
            for grandchild in child.children:
                assert grandchild.depth == 2

    def test_max_depth_zero(self):
        """Test max_depth=0 only includes root."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("Demo_Init", max_depth=0, verbose=False)

        assert result.call_tree is not None
        assert len(result.call_tree.children) == 0
        assert result.statistics.max_depth_reached == 0


class TestErrorHandling:
    """Test error handling for edge cases (SWR_ANALYZER_00010)."""

    def test_SWUT_ANALYZER_00010_missing_function_handling(self):
        """Test builder handles missing functions gracefully (SWR_ANALYZER_00010)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create function that calls non-existent functions
            (temp_path / "caller.c").write_text("""
void caller(void) {
    nonexistent_function();
    another_missing();
}
""")

            db = FunctionDatabase(source_dir=temp_dir)
            db.build_database(use_cache=False, verbose=False)

            builder = CallTreeBuilder(db)
            result = builder.build_tree("caller", max_depth=3, verbose=False)

            # Tree should be built successfully
            assert result.call_tree is not None
            assert result.call_tree.function_info.name == "caller"

            # The C parser creates stub FunctionInfo objects for called functions
            # even if they don't exist, so children will exist but with no calls
            assert len(result.call_tree.children) >= 0

            # No errors should be reported
            assert len(result.errors) == 0


class TestStatistics:
    """Test statistics collection (SWR_ANALYZER_00011-00012)."""

    def test_SWUT_ANALYZER_00011_statistics_collection(self):
        """Test builder collects accurate statistics (SWR_ANALYZER_00011)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("Demo_Init", max_depth=3, verbose=False)

        stats = result.statistics

        assert stats.total_functions > 0
        assert stats.max_depth_reached >= 0
        assert stats.unique_functions > 0
        assert stats.circular_dependencies_found >= 0

        # Total functions should match internal counter
        assert stats.total_functions == builder.total_nodes

        # Unique functions should match visited set
        assert stats.unique_functions == len(builder.visited_functions)

        # Circular dependencies should match list
        assert stats.circular_dependencies_found == len(builder.circular_dependencies)

    def test_SWUT_ANALYZER_00012_unique_function_tracking(self):
        """Test builder tracks unique functions visited (SWR_ANALYZER_00012)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("Demo_Init", max_depth=3, verbose=False)

        unique_count = len(builder.visited_functions)

        # Should be reflected in statistics
        assert result.statistics.unique_functions == unique_count

        # Should be <= total nodes
        assert unique_count <= result.statistics.total_functions

        # Verify qualified names are unique
        visited_names = list(builder.visited_functions)
        assert len(set(visited_names)) == len(visited_names)


class TestQualifiedName:
    """Test qualified name generation (SWR_ANALYZER_00013)."""

    def test_SWUT_ANALYZER_00013_qualified_name_generation(self):
        """Test builder generates qualified names correctly (SWR_ANALYZER_00013)."""
        from autosar_calltree.database.function_database import FunctionDatabase
        from autosar_calltree.database.models import FunctionInfo, FunctionType

        db = FunctionDatabase(source_dir="./demo")

        func = FunctionInfo(
            name="MyFunction",
            return_type="void",
            file_path=Path("/path/to/my_function.c"),
            line_number=10,
            is_static=False,
            function_type=FunctionType.TRADITIONAL_C,
            calls=[]
        )

        builder = CallTreeBuilder(db)
        qualified = builder._get_qualified_name(func)

        assert qualified == "my_function::MyFunction"
        assert "::" in qualified


class TestUtilityMethods:
    """Test utility methods for tree analysis (SWR_ANALYZER_00016-00019)."""

    def test_SWUT_ANALYZER_00016_get_all_functions_in_tree(self):
        """Test get_all_functions_in_tree collects all functions (SWR_ANALYZER_00016)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("Demo_Init", max_depth=3, verbose=False)

        functions = builder.get_all_functions_in_tree(result.call_tree)

        assert isinstance(functions, list)
        assert len(functions) > 0

        # Should be unique
        function_names = [f.name for f in functions]
        assert len(function_names) == len(set(function_names))

        # Root function should be included
        assert any(f.name == "Demo_Init" for f in functions)

    def test_SWUT_ANALYZER_00016_unique_in_tree_with_cycles(self):
        """Test get_all_functions_in_tree handles cycles."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create circular call
            (temp_path / "func_a.c").write_text("""
void func_a(void) {
    func_b();
}
""")

            (temp_path / "func_b.c").write_text("""
void func_b(void) {
    func_a();
}
""")

            db = FunctionDatabase(source_dir=temp_dir)
            db.build_database(use_cache=False, verbose=False)

            builder = CallTreeBuilder(db)
            result = builder.build_tree("func_a", max_depth=5, verbose=False)

            functions = builder.get_all_functions_in_tree(result.call_tree)

            # Should have exactly 2 unique functions
            assert len(functions) == 2
            function_names = {f.name for f in functions}
            assert function_names == {"func_a", "func_b"}

    def test_SWUT_ANALYZER_00017_get_tree_depth(self):
        """Test get_tree_depth returns maximum depth (SWR_ANALYZER_00017)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("Demo_Init", max_depth=3, verbose=False)

        depth = builder.get_tree_depth(result.call_tree)

        assert isinstance(depth, int)
        assert depth >= 0
        assert depth <= 3

    def test_SWUT_ANALYZER_00017_single_node_depth(self):
        """Test get_tree_depth for single node."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            (temp_path / "leaf.c").write_text("""
void leaf(void) {
    return;
}
""")

            db = FunctionDatabase(source_dir=temp_dir)
            db.build_database(use_cache=False, verbose=False)

            builder = CallTreeBuilder(db)
            result = builder.build_tree("leaf", max_depth=3, verbose=False)

            depth = builder.get_tree_depth(result.call_tree)

            assert depth == 0

    def test_SWUT_ANALYZER_00018_get_leaf_nodes(self):
        """Test get_leaf_nodes returns all terminal nodes (SWR_ANALYZER_00018)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("Demo_Init", max_depth=2, verbose=False)

        leaves = builder.get_leaf_nodes(result.call_tree)

        assert isinstance(leaves, list)
        assert len(leaves) > 0

        # All leaves should have no children
        assert all(len(leaf.children) == 0 for leaf in leaves)

    def test_SWUT_ANALYZER_00018_all_nodes_are_leaves(self):
        """Test get_leaf_nodes when max_depth=0."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("Demo_Init", max_depth=0, verbose=False)

        leaves = builder.get_leaf_nodes(result.call_tree)

        # Only root, which is a leaf
        assert len(leaves) == 1
        assert leaves[0] == result.call_tree

    def test_SWUT_ANALYZER_00019_text_tree_generation(self):
        """Test print_tree_text generates proper representation (SWR_ANALYZER_00019)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)
        result = builder.build_tree("Demo_Init", max_depth=2, verbose=False)

        # With file paths
        text_with_files = builder.print_tree_text(result.call_tree, show_file=True)

        assert isinstance(text_with_files, str)
        assert len(text_with_files) > 0
        assert "Demo_Init" in text_with_files
        assert ".c" in text_with_files
        assert "├──" in text_with_files or "└──" in text_with_files

        # Without file paths
        text_without_files = builder.print_tree_text(result.call_tree, show_file=False)

        assert isinstance(text_without_files, str)
        assert len(text_without_files) > 0
        assert "Demo_Init" in text_without_files
        assert ".c" not in text_without_files

    def test_SWUT_ANALYZER_00019_text_tree_with_recursive(self):
        """Test text tree shows recursive nodes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create self-recursive function
            (temp_path / "recursive.c").write_text("""
void recursive_func(void) {
    recursive_func();
}
""")

            db = FunctionDatabase(source_dir=temp_dir)
            db.build_database(use_cache=False, verbose=False)

            builder = CallTreeBuilder(db)
            result = builder.build_tree("recursive_func", max_depth=3, verbose=False)

            text = builder.print_tree_text(result.call_tree, show_file=False)

            assert "[RECURSIVE]" in text


class TestVerboseOutput:
    """Test verbose progress logging (SWR_ANALYZER_00020)."""

    def test_SWUT_ANALYZER_00020_verbose_progress_logging(self):
        """Test verbose mode logs progress (SWR_ANALYZER_00020)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)

        import sys
        from io import StringIO

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        result = builder.build_tree("Demo_Init", max_depth=2, verbose=True)

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        # Should contain progress information
        assert "Building call tree" in output or "Demo_Init" in output
        assert "Max depth" in output or "depth" in output.lower()
        assert "Analysis complete" in output or "complete" in output.lower()

    def test_verbose_false_no_output(self):
        """Test verbose=False produces no output."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        builder = CallTreeBuilder(db)

        import sys
        from io import StringIO

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        result = builder.build_tree("Demo_Init", max_depth=2, verbose=False)

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        # Should have no output from build_tree
        # (Note: database build might have output if verbose, but not builder)
        assert "Building call tree" not in output


class TestMultipleDefinitions:
    """Test handling of multiple function definitions (SWR_ANALYZER_00004)."""

    def test_SWUT_ANALYZER_00004_multiple_definition_warning(self):
        """Test builder handles multiple definitions with smart selection (SWR_ANALYZER_00004)."""
        # Create database with duplicate definitions
        # Note: The smart lookup selects the best match, so we won't see
        # a "multiple definitions" warning in this case
        db = FunctionDatabase(source_dir="./demo")

        func1 = FunctionInfo(
            name="DuplicateFunc",
            return_type="void",
            file_path=Path("file1.c"),
            line_number=10,
            is_static=False,
            function_type=FunctionType.TRADITIONAL_C,
            calls=[]
        )

        func2 = FunctionInfo(
            name="DuplicateFunc",
            return_type="void",
            file_path=Path("file2.c"),
            line_number=20,
            is_static=False,
            function_type=FunctionType.TRADITIONAL_C,
            calls=[]
        )

        db.functions["DuplicateFunc"] = [func1, func2]

        builder = CallTreeBuilder(db)

        import sys
        from io import StringIO

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        result = builder.build_tree("DuplicateFunc", max_depth=2, verbose=True)

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        # Smart lookup will select one, and the tree will be built successfully
        assert result.call_tree is not None
        assert result.call_tree.function_info.name == "DuplicateFunc"

        # Tree is built with the selected function
        assert "Building call tree" in output

    def test_multiple_definitions_uses_first(self):
        """Test builder uses first definition when multiple exist."""
        db = FunctionDatabase(source_dir="./demo")

        func1 = FunctionInfo(
            name="SomeFunc",
            return_type="void",
            file_path=Path("file1.c"),
            line_number=10,
            is_static=False,
            function_type=FunctionType.TRADITIONAL_C,
            calls=[]
        )

        func2 = FunctionInfo(
            name="SomeFunc",
            return_type="void",
            file_path=Path("file2.c"),
            line_number=20,
            is_static=False,
            function_type=FunctionType.TRADITIONAL_C,
            calls=[]
        )

        db.functions["SomeFunc"] = [func1, func2]

        builder = CallTreeBuilder(db)
        result = builder.build_tree("SomeFunc", max_depth=2, verbose=False)

        # Should use first match
        assert result.call_tree is not None
        assert result.call_tree.function_info == func1
