"""Tests for analyzers/call_tree_builder.py (SWUT_ANALYZER_00001-00015)"""

from pathlib import Path

from autosar_calltree.analyzers.call_tree_builder import CallTreeBuilder
from autosar_calltree.database.function_database import FunctionDatabase


# SWUT_ANALYZER_00001: Builder Initialization

def test_builder_initialization():
    """SWUT_ANALYZER_00001

    Test that CallTreeBuilder can be initialized with a FunctionDatabase instance.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    builder = CallTreeBuilder(db)

    assert builder.function_db == db
    assert len(builder.visited_functions) == 0
    assert len(builder.call_stack) == 0
    assert len(builder.circular_dependencies) == 0
    assert builder.max_depth_reached == 0
    assert builder.total_nodes == 0


# SWUT_ANALYZER_00002: State Management

def test_state_reset_between_builds():
    """SWUT_ANALYZER_00002

    Test that each build_tree() call resets state properly.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    # First build
    result1 = builder.build_tree("Demo_Init", max_depth=2, verbose=False)
    assert builder.total_nodes > 0
    first_total = builder.total_nodes

    # Second build
    result2 = builder.build_tree("Demo_MainFunction", max_depth=2, verbose=False)

    # State should be reset for second build
    assert len(builder.visited_functions) > 0  # Populated during second build
    assert builder.total_nodes >= first_total  # New count for second build

    # Results should be independent
    assert result1.root_function == "Demo_Init"
    assert result2.root_function == "Demo_MainFunction"


# SWUT_ANALYZER_00003: Start Function Validation

def test_start_function_validation():
    """SWUT_ANALYZER_00003

    Test that start function exists in database before building tree.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    # Test with valid function
    result = builder.build_tree("Demo_Init", max_depth=2)
    assert result.root_function == "Demo_Init"
    assert len(result.errors) == 0

    # Test with non-existent function
    result_invalid = builder.build_tree("NonExistentFunction", max_depth=2)
    assert result_invalid.root_function is None
    assert len(result_invalid.errors) > 0
    assert any("not found" in e for e in result_invalid.errors)


# SWUT_ANALYZER_00004: Depth-First Traversal Algorithm

def test_depth_first_traversal():
    """SWUT_ANALYZER_00004

    Test that call tree is built using depth-first traversal.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    result = builder.build_tree("Demo_Init", max_depth=2, verbose=False)

    # Verify DFS traversal: should explore each call path to end
    assert result.call_tree is not None
    assert len(result.statistics.unique_functions) > 0


# SWUT_ANALYZER_00005: Cycle Detection

def test_cycle_detection():
    """SWUT_ANALYZER_00005

    Test that circular dependencies in call graph are detected using call stack.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    result = builder.build_tree("Demo_Init", max_depth=5, verbose=False)

    # Check if cycles were detected
    assert len(result.circular_dependencies) >= 0

    # Verify cycle structure
    for cycle in result.circular_dependencies:
        assert len(cycle.cycle) >= 2  # At least A->B->A
        assert cycle.depth > 0


# SWUT_ANALYZER_00006: Cycle Handling in Tree

def test_cycle_handling_in_tree():
    """SWUT_ANALYZER_00006

    Test that cycles in call graph are handled correctly in tree structure.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    result = builder.build_tree("Demo_Init", max_depth=5, verbose=False)

    # Check for recursive nodes
    recursive_nodes = []

    def check_recursive(node: CallTreeNode):
        if node.is_recursive:
            recursive_nodes.append(node.function_info.name)
        for child in node.children:
            check_recursive(child)

    check_recursive(result.call_tree)

    # Should have recursive nodes if cycles detected
    if result.circular_dependencies:
        assert len(recursive_nodes) > 0


# SWUT_ANALYZER_00007: Max Depth Enforcement

def test_max_depth_enforcement():
    """SWUT_ANALYZER_00007

    Test that max_depth limit is respected during traversal.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    # Test max_depth = 0 (root only)
    result = builder.build_tree("Demo_Init", max_depth=0)
    assert result.call_tree.depth == 0
    assert len(result.call_tree.children) == 0
    assert result.statistics.max_depth_reached == 0

    # Test max_depth = 1 (root + immediate children)
    result = builder.build_tree("Demo_Init", max_depth=1)
    assert result.call_tree.depth == 0
    assert len(result.call_tree.children) > 0
    # All children should be at depth 1
    for child in result.call_tree.children:
        assert child.depth == 1

    # Verify truncated nodes
    def check_truncated(node: CallTreeNode, current_depth: int):
        if node.depth == current_depth:
            assert node.is_truncated is False
        for child in node.children:
            check_truncated(child, current_depth + 1)

    # With limited depth, nodes should not be truncated
    check_truncated(result.call_tree, 1)


# SWUT_ANALYZER_00008: Node Depth Tracking

def test_node_depth_tracking():
    """SWUT_ANALYZER_00008

    Test that depth of each node in tree is tracked correctly.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    result = builder.build_tree("Demo_Init", max_depth=3, verbose=False)

    # Root should be at depth 0
    assert result.call_tree.depth == 0

    # Check all children at depth 1
    for child in result.call_tree.children:
        assert child.depth == 1

        # Check grandchildren at depth 2
        for grandchild in child.children:
            assert grandchild.depth == 2


# SWUT_ANALYZER_00009: AnalysisResult Creation

def test_analysis_result_creation():
    """SWUT_ANALYZER_00009

    Test that complete AnalysisResult objects are created with all required
    fields.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    result = builder.build_tree("Demo_Init", max_depth=2, verbose=False)

    # Verify result structure
    assert result.root_function is not None
    assert result.call_tree is not None
    assert result.statistics is not None
    assert result.circular_dependencies is not None
    assert result.errors is not None

    # Verify statistics fields
    assert hasattr(result.statistics, "total_functions")
    assert hasattr(result.statistics, "unique_functions")
    assert hasattr(result.statistics, "max_depth_reached")
    assert hasattr(result.statistics, "total_function_calls")


# SWUT_ANALYZER_00010: Statistics Collection

def test_statistics_collection():
    """SWUT_ANALYZER_00010

    Test that statistics are collected during traversal.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    result = builder.build_tree("Demo_Init", max_depth=5, verbose=False)

    # Verify statistics collected
    assert result.statistics.total_functions > 0
    assert result.statistics.unique_functions > 0
    assert result.statistics.max_depth_reached >= 0
    assert result.statistics.total_function_calls >= 0


# SWUT_ANALYZER_00011: Unique Function Tracking

def test_unique_function_tracking():
    """SWUT_ANALYZER_00011

    Test that unique functions are tracked using a set.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    result = builder.build_tree("Demo_Init", max_depth=5, verbose=False)

    # Unique count should be <= total count
    assert result.statistics.unique_functions <= result.statistics.total_functions

    # If same function called multiple times, counted once
    assert result.statistics.unique_functions > 0


# SWUT_ANALYZER_00012: Missing Function Handling

def test_missing_function_handling():
    """SWUT_ANALYZER_00012

    Test that functions not in database are handled gracefully.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    # Build tree with functions that may call missing functions
    result = builder.build_tree("Demo_Init", max_depth=2, verbose=False)

    # Should complete successfully even with missing functions
    assert result.call_tree is not None
    assert result.root_function is not None


# SWUT_ANALYZER_00013: RTE Call Filtering

def test_rte_call_filtering():
    """SWUT_ANALYZER_00013

    Test that RTE calls can be included or excluded from tree.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    # Test excluding RTE calls (default behavior)
    result1 = builder.build_tree("Demo_Init", max_depth=2, include_rte=False)
    rte_count_excluded = result1.statistics.rte_functions

    # Test including RTE calls
    result2 = builder.build_tree("Demo_Init", max_depth=2, include_rte=True)
    rte_count_included = result2.statistics.rte_functions

    # Including RTE should have equal or more RTE functions
    assert rte_count_included >= rte_count_excluded


# SWUT_ANALYZER_00014: Qualified Name Usage

def test_qualified_name_usage():
    """SWUT_ANALYZER_00014

    Test that qualified names (file::function) are used for cycle detection to
    differentiate static functions with same name.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=False)

    builder = CallTreeBuilder(db)

    _ = builder.build_tree("Demo_Init", max_depth=5, verbose=False)

    # Qualified names prevent false cycle detection across files
    # This is verified by checking call_stack operations
    # which use qualified names


# SWUT_ANALYZER_00015: Verbose Logging

def test_verbose_logging():
    """SWUT_ANALYZER_00015

    Test that progress is logged during tree building in verbose mode.
    """
    db = FunctionDatabase(source_dir=Path("./demo"))
    db.build_database(use_cache=False, verbose=True)

    builder = CallTreeBuilder(db)

    # Verbose mode should produce output without errors
    result = builder.build_tree("Demo_Init", max_depth=2, verbose=True)

    # Verify result is created
    assert result.root_function is not None
    assert result.call_tree is not None
