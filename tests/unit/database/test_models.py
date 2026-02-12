"""Tests for database/models.py (SWUT_DB_*)"""

from datetime import datetime
from pathlib import Path

from autosar_calltree.database.models import (
    AnalysisResult,
    AnalysisStatistics,
    CallTreeNode,
    CircularDependency,
    FunctionCall,
    FunctionInfo,
    FunctionType,
    Parameter,
)

# SWUT_DB_00001: FunctionType Enum Values


def test_function_type_enum_values():
    """SWUT_DB_00001

    Test that FunctionType enum has all required classification values for different function
    declaration types encountered in AUTOSAR and traditional C code.
    """
    # Verify all enum values exist and have correct string representations
    assert FunctionType.AUTOSAR_FUNC.value == "autosar_func"
    assert FunctionType.AUTOSAR_FUNC_P2VAR.value == "autosar_func_p2var"
    assert FunctionType.AUTOSAR_FUNC_P2CONST.value == "autosar_func_p2const"
    assert FunctionType.TRADITIONAL_C.value == "traditional_c"
    assert FunctionType.RTE_CALL.value == "rte_call"
    assert FunctionType.UNKNOWN.value == "unknown"

    # Verify enum has exactly 6 values
    assert len(FunctionType) == 6


# SWUT_DB_00002: Parameter Dataclass Core Fields


def test_parameter_core_fields():
    """SWUT_DB_00002

    Test that Parameter dataclass has all required fields with correct types and default
    values.
    """
    # Create parameter with all fields
    param = Parameter(
        name="timerId",
        param_type="uint32",
        is_pointer=False,
        is_const=False,
        memory_class="AUTOMATIC",
    )

    # Verify field values
    assert param.name == "timerId"
    assert param.param_type == "uint32"
    assert param.is_pointer is False
    assert param.is_const is False
    assert param.memory_class == "AUTOMATIC"

    # Verify default values
    param_default = Parameter(name="test", param_type="int")
    assert param_default.is_pointer is False
    assert param_default.is_const is False
    assert param_default.memory_class is None


# SWUT_DB_00003: Parameter String Representation


def test_parameter_str_representation():
    """SWUT_DB_00003

    Test that Parameter.__str__ method formats parameters correctly with const, pointer, and
    memory class.
    """
    # Test const parameter
    param_const = Parameter(name="value", param_type="uint32", is_const=True)
    assert str(param_const) == "const uint32 value"

    # Test pointer parameter
    param_ptr = Parameter(name="buffer", param_type="uint8", is_pointer=True)
    assert str(param_ptr) == "uint8* buffer"

    # Test const pointer parameter
    param_const_ptr = Parameter(
        name="config", param_type="ConfigType", is_const=True, is_pointer=True
    )
    assert str(param_const_ptr) == "const ConfigType* config"

    # Test parameter with memory class
    param_memclass = Parameter(
        name="data", param_type="uint32", memory_class="AUTOMATIC"
    )
    assert str(param_memclass) == "uint32 data [AUTOMATIC]"

    # Test const pointer with memory class
    param_full = Parameter(
        name="buffer",
        param_type="uint8",
        is_const=True,
        is_pointer=True,
        memory_class="APPL_DATA",
    )
    assert str(param_full) == "const uint8* buffer [APPL_DATA]"


# SWUT_DB_00004: FunctionInfo Core Identity Fields


def test_function_info_identity_fields():
    """SWUT_DB_00004

    Test that FunctionInfo dataclass has all core identity fields for uniquely identifying
    functions.
    """
    # Create function with all identity fields
    func = FunctionInfo(
        name="Demo_Init",
        return_type="void",
        file_path=Path("/src/demo.c"),
        line_number=42,
        is_static=False,
    )

    # Verify field values
    assert func.name == "Demo_Init"
    assert func.return_type == "void"
    assert func.file_path == Path("/src/demo.c")
    assert func.line_number == 42
    assert func.is_static is False

    # Test static function
    func_static = FunctionInfo(
        name="Internal_Helper",
        return_type="uint8",
        file_path=Path("/src/demo.c"),
        line_number=100,
        is_static=True,
    )
    assert func_static.is_static is True


# SWUT_DB_00005: FunctionInfo Type Classification


def test_function_info_type_classification():
    """SWUT_DB_00005

    Test that FunctionInfo includes function type classification and AUTOSAR-specific metadata
    fields.
    """
    # Test AUTOSAR FUNC
    func_autosar = FunctionInfo(
        name="COM_Init",
        return_type="void",
        file_path=Path("/src/com.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.AUTOSAR_FUNC,
        memory_class="RTE_CODE",
        macro_type="FUNC",
    )
    assert func_autosar.function_type == FunctionType.AUTOSAR_FUNC
    assert func_autosar.memory_class == "RTE_CODE"
    assert func_autosar.macro_type == "FUNC"

    # Test FUNC_P2VAR
    func_p2var = FunctionInfo(
        name="GetBuffer",
        return_type="uint8*",
        file_path=Path("/src/buffer.c"),
        line_number=20,
        is_static=False,
        function_type=FunctionType.AUTOSAR_FUNC_P2VAR,
        memory_class="AUTOMATIC",
        macro_type="FUNC_P2VAR",
    )
    assert func_p2var.function_type == FunctionType.AUTOSAR_FUNC_P2VAR

    # Test traditional C function
    func_c = FunctionInfo(
        name="standard_function",
        return_type="int",
        file_path=Path("/src/main.c"),
        line_number=50,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    assert func_c.function_type == FunctionType.TRADITIONAL_C
    assert func_c.memory_class is None
    assert func_c.macro_type is None


# SWUT_DB_00006: FunctionInfo Equality and Hashing


def test_function_info_equality():
    """SWUT_DB_00004

    Test that FunctionInfo objects can be compared and hashed correctly based on identity
    fields.
    """
    # Create two identical functions
    func1 = FunctionInfo(
        name="TestFunc",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=False,
    )

    func2 = FunctionInfo(
        name="TestFunc",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=False,
    )

    # Hash should be based on identity fields
    assert hash(func1) == hash(func2)

    # Can be used in set
    function_set = {func1, func2}
    assert len(function_set) == 1  # Duplicates removed

    # Can be used as dictionary key
    func_dict = {func1: "value1"}
    assert func1 in func_dict
    assert func_dict[func1] == "value1"
    assert func_dict[func2] == "value1"  # func2 is same key

    # Different function should have different hash
    func3 = FunctionInfo(
        name="TestFunc",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=20,  # Different line
        is_static=False,
    )
    assert hash(func1) != hash(func3)

    function_set2 = {func1, func3}
    assert len(function_set2) == 2


# SWUT_DB_00007: FunctionInfo RTE Detection


def test_function_info_rte_detection():
    """SWUT_DB_00004

    Test that FunctionInfo.is_rte_function method correctly identifies RTE functions.
    """
    # Test RTE function by naming convention
    func_rte_call = FunctionInfo(
        name="Rte_Call_StartTrigger",
        return_type="void",
        file_path=Path("/src/rte.c"),
        line_number=10,
        is_static=False,
    )
    assert func_rte_call.is_rte_function() is True

    # Test RTE function by function type
    func_rte_type = FunctionInfo(
        name="SomeFunction",
        return_type="void",
        file_path=Path("/src/rte.c"),
        line_number=20,
        is_static=False,
        function_type=FunctionType.RTE_CALL,
    )
    assert func_rte_type.is_rte_function() is True

    # Test both conditions
    func_rte_both = FunctionInfo(
        name="Rte_Read_Data",
        return_type="Std_ReturnType",
        file_path=Path("/src/rte.c"),
        line_number=30,
        is_static=False,
        function_type=FunctionType.RTE_CALL,
    )
    assert func_rte_both.is_rte_function() is True

    # Test non-RTE function
    func_regular = FunctionInfo(
        name="RegularFunction",
        return_type="void",
        file_path=Path("/src/regular.c"),
        line_number=40,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    assert func_regular.is_rte_function() is False

    # Test function with Rte_ prefix but traditional type
    func_mixed = FunctionInfo(
        name="Rte_InternalHelper",  # Has Rte_ prefix
        return_type="void",
        file_path=Path("/src/rte.c"),
        line_number=50,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    assert func_mixed.is_rte_function() is True  # Due to Rte_ prefix


# SWUT_DB_00008: FunctionCall Conditional Fields


def test_function_call_conditional_fields():
    """SWUT_DB_00006

    Test that FunctionCall model tracks conditional execution context (if/else blocks) for proper
    opt block generation.
    """
    # Test conditional call
    call_cond = FunctionCall(
        name="COM_Send", is_conditional=True, condition="update_mode == 0x05"
    )
    assert call_cond.is_conditional is True
    assert call_cond.condition == "update_mode == 0x05"

    # Test non-conditional call
    call_normal = FunctionCall(name="COM_Init")
    assert call_normal.is_conditional is False
    assert call_normal.condition is None

    # Test defaults
    call_default = FunctionCall(name="SomeFunction")
    assert call_default.is_conditional is False
    assert call_default.condition is None


# SWUT_DB_00009: FunctionCall Loop Fields


def test_function_call_loop_fields():
    """SWUT_DB_00006

    Test that FunctionCall model tracks loop execution context (for/while loops) for proper
    loop block generation.
    """
    # Test loop call
    call_loop = FunctionCall(
        name="ProcessData", is_loop=True, loop_condition="i < count"
    )
    assert call_loop.is_loop is True
    assert call_loop.loop_condition == "i < count"

    # Test non-loop call
    call_normal = FunctionCall(name="COM_Init")
    assert call_normal.is_loop is False
    assert call_normal.loop_condition is None

    # Test defaults
    call_default = FunctionCall(name="SomeFunction")
    assert call_default.is_loop is False
    assert call_default.loop_condition is None


# SWUT_DB_00010: CallTreeNode Structure


def test_call_tree_node_structure():
    """SWUT_DB_00007

    Test that CallTreeNode dataclass has core fields for hierarchical tree structure.
    """
    # Create function info for node
    func_info = FunctionInfo(
        name="ParentFunc",
        return_type="void",
        file_path=Path("/src/parent.c"),
        line_number=10,
        is_static=False,
    )

    # Create node with all core fields
    node = CallTreeNode(function_info=func_info, depth=0, children=[], parent=None)

    # Verify field values
    assert node.function_info == func_info
    assert node.depth == 0
    assert len(node.children) == 0
    assert node.parent is None

    # Create child node
    child_func = FunctionInfo(
        name="ChildFunc",
        return_type="void",
        file_path=Path("/src/child.c"),
        line_number=20,
        is_static=False,
    )
    child_node = CallTreeNode(
        function_info=child_func, depth=1, children=[], parent=node
    )

    assert child_node.depth == 1
    assert child_node.parent == node


# SWUT_DB_00011: CallTreeNode State Flags


def test_call_tree_node_state_flags():
    """SWUT_DB_00007

    Test that CallTreeNode includes state flags for recursive calls, truncation, and call
    frequency.
    """
    func = FunctionInfo(
        name="TestFunc",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=False,
    )

    # Test default values
    node = CallTreeNode(function_info=func, depth=0)
    assert node.is_recursive is False
    assert node.is_truncated is False
    assert node.call_count == 1

    # Test recursive flag
    node_recursive = CallTreeNode(function_info=func, depth=2, is_recursive=True)
    assert node_recursive.is_recursive is True

    # Test truncated flag
    node_truncated = CallTreeNode(function_info=func, depth=5, is_truncated=True)
    assert node_truncated.is_truncated is True

    # Test call count
    node_called = CallTreeNode(function_info=func, depth=1, call_count=3)
    assert node_called.call_count == 3


# SWUT_DB_00012: CallTreeNode Recursive Detection


def test_call_tree_node_recursive_detection():
    """SWUT_DB_00007

    Test that CallTreeNode correctly identifies recursive function calls for circular dependency
    tracking.
    """
    func = FunctionInfo(
        name="RecursiveFunc",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=False,
    )

    # Create recursive node
    node_recursive = CallTreeNode(function_info=func, depth=2, is_recursive=True)
    assert node_recursive.is_recursive is True


# SWUT_DB_00013: CallTreeNode Tree Manipulation


def test_call_tree_node_add_child():
    """SWUT_DB_00007

    Test that CallTreeNode.add_child method correctly builds parent-child relationships.
    """
    # Create parent and child nodes
    parent_func = FunctionInfo(
        name="Parent",
        return_type="void",
        file_path=Path("/src/parent.c"),
        line_number=10,
        is_static=False,
    )
    parent = CallTreeNode(function_info=parent_func, depth=0)

    child1_func = FunctionInfo(
        name="Child1",
        return_type="void",
        file_path=Path("/src/child1.c"),
        line_number=20,
        is_static=False,
    )
    child1 = CallTreeNode(function_info=child1_func, depth=1)

    child2_func = FunctionInfo(
        name="Child2",
        return_type="void",
        file_path=Path("/src/child2.c"),
        line_number=30,
        is_static=False,
    )
    child2 = CallTreeNode(function_info=child2_func, depth=1)

    # Add children
    parent.add_child(child1)
    parent.add_child(child2)

    # Verify children list
    assert len(parent.children) == 2
    assert parent.children[0] == child1
    assert parent.children[1] == child2

    # Verify parent references
    assert child1.parent == parent
    assert child2.parent == parent

    # Verify child depth is preserved
    assert child1.depth == 1
    assert child2.depth == 1


# SWUT_DB_00014: CallTreeNode Function Collection


def test_call_tree_node_get_all_functions():
    """SWUT_DB_00007

    Test that CallTreeNode.get_all_functions method collects all unique functions in subtree.
    """
    # Create function infos
    func1 = FunctionInfo(
        name="Func1",
        return_type="void",
        file_path=Path("/src/f1.c"),
        line_number=10,
        is_static=False,
    )
    func2 = FunctionInfo(
        name="Func2",
        return_type="void",
        file_path=Path("/src/f2.c"),
        line_number=20,
        is_static=False,
    )
    func3 = FunctionInfo(
        name="Func3",
        return_type="void",
        file_path=Path("/src/f3.c"),
        line_number=30,
        is_static=False,
    )

    # Build tree: root -> child1 -> grandchild
    #                -> child2
    root = CallTreeNode(function_info=func1, depth=0)
    child1 = CallTreeNode(function_info=func2, depth=1)
    child2 = CallTreeNode(function_info=func3, depth=1)
    grandchild = CallTreeNode(function_info=func1, depth=2)  # Duplicate func1

    root.add_child(child1)
    root.add_child(child2)
    child1.add_child(grandchild)

    # Collect all functions
    all_funcs = root.get_all_functions()

    # Should have unique functions (func1 appears twice in tree but once in set)
    assert len(all_funcs) == 3
    assert func1 in all_funcs
    assert func2 in all_funcs
    assert func3 in all_funcs

    # Test leaf node (no children)
    leaf_funcs = child2.get_all_functions()
    assert len(leaf_funcs) == 1
    assert func3 in leaf_funcs


# SWUT_DB_00015: CallTreeNode Depth Calculation


def test_call_tree_node_get_max_depth():
    """SWUT_DB_00007

    Test that CallTreeNode.get_max_depth method calculates maximum depth of subtree.
    """
    func = FunctionInfo(
        name="Func",
        return_type="void",
        file_path=Path("/src/f.c"),
        line_number=10,
        is_static=False,
    )

    # Test leaf node
    leaf = CallTreeNode(function_info=func, depth=5)
    assert leaf.get_max_depth() == 5

    # Test tree with varying depths
    # Structure:
    #   root (depth 0)
    #     ├── child1 (depth 1)
    #     │     └── grandchild (depth 2)
    #     └── child2 (depth 1)
    #           └── grandchild2 (depth 2)
    #                 └── greatgrandchild (depth 3)

    root = CallTreeNode(function_info=func, depth=0)
    child1 = CallTreeNode(function_info=func, depth=1)
    child2 = CallTreeNode(function_info=func, depth=1)
    grandchild1 = CallTreeNode(function_info=func, depth=2)
    grandchild2 = CallTreeNode(function_info=func, depth=2)
    greatgrandchild = CallTreeNode(function_info=func, depth=3)

    root.add_child(child1)
    root.add_child(child2)
    child1.add_child(grandchild1)
    child2.add_child(grandchild2)
    grandchild2.add_child(greatgrandchild)

    assert root.get_max_depth() == 3

    # Test from intermediate node
    assert child2.get_max_depth() == 3  # Finds greatgrandchild at depth 3
    assert child1.get_max_depth() == 2  # Finds grandchild1 at depth 2


# SWUT_DB_00016: CircularDependency Core Structure


def test_circular_dependency_structure():
    """SWUT_DB_00008

    Test that CircularDependency dataclass has core fields for representing detected cycles.
    """
    # Create circular dependency
    cycle = CircularDependency(cycle=["FuncA", "FuncB", "FuncC", "FuncA"], depth=3)

    # Verify fields
    assert cycle.cycle == ["FuncA", "FuncB", "FuncC", "FuncA"]
    assert cycle.depth == 3

    # Test different cycle
    cycle2 = CircularDependency(cycle=["Init", "Process", "Validate", "Init"], depth=5)
    assert len(cycle2.cycle) == 4
    assert cycle2.depth == 5

    # Test simple 2-function cycle
    cycle3 = CircularDependency(cycle=["A", "B", "A"], depth=1)
    assert len(cycle3.cycle) == 3
    assert cycle3.depth == 1


# SWUT_DB_00017: CircularDependency String Representation


def test_circular_dependency_str():
    """SWUT_DB_00008

    Test that CircularDependency.__str__ method formats cycles in readable arrow notation.
    """
    # Test 3-function cycle
    cycle1 = CircularDependency(cycle=["FuncA", "FuncB", "FuncC", "FuncA"], depth=3)
    assert str(cycle1) == "FuncA -> FuncB -> FuncC -> FuncA"

    # Test 2-function cycle
    cycle2 = CircularDependency(cycle=["Init", "Process", "Init"], depth=2)
    assert str(cycle2) == "Init -> Process -> Init"

    # Test 4-function cycle
    cycle3 = CircularDependency(cycle=["A", "B", "C", "D", "A"], depth=5)
    assert str(cycle3) == "A -> B -> C -> D -> A"

    # Test single function (self-call)
    cycle4 = CircularDependency(cycle=["RecursiveFunc", "RecursiveFunc"], depth=1)
    assert str(cycle4) == "RecursiveFunc -> RecursiveFunc"


# SWUT_DB_00018: AnalysisStatistics Counters


def test_analysis_statistics_counters():
    """SWUT_DB_00009

    Test that AnalysisStatistics dataclass has all counter fields with correct defaults.
    """
    # Test default values
    stats = AnalysisStatistics()
    assert stats.total_functions == 0
    assert stats.unique_functions == 0
    assert stats.max_depth_reached == 0
    assert stats.total_function_calls == 0
    assert stats.static_functions == 0
    assert stats.rte_functions == 0
    assert stats.autosar_functions == 0
    assert stats.circular_dependencies_found == 0

    # Test with values
    stats2 = AnalysisStatistics(
        total_functions=100,
        unique_functions=50,
        max_depth_reached=5,
        total_function_calls=200,
        static_functions=30,
        rte_functions=10,
        autosar_functions=40,
        circular_dependencies_found=2,
    )
    assert stats2.total_functions == 100
    assert stats2.unique_functions == 50
    assert stats2.max_depth_reached == 5
    assert stats2.total_function_calls == 200
    assert stats2.static_functions == 30
    assert stats2.rte_functions == 10
    assert stats2.autosar_functions == 40
    assert stats2.circular_dependencies_found == 2


# SWUT_DB_00019: AnalysisStatistics Dictionary Conversion


def test_analysis_statistics_to_dict():
    """SWUT_DB_00009

    Test that AnalysisStatistics.to_dict method converts statistics to dictionary format.
    """
    # Test with values
    stats = AnalysisStatistics(
        total_functions=100,
        unique_functions=50,
        max_depth_reached=5,
        total_function_calls=200,
        static_functions=30,
        rte_functions=10,
        autosar_functions=40,
        circular_dependencies_found=2,
    )

    result = stats.to_dict()

    # Verify dictionary structure
    assert isinstance(result, dict)
    assert result["total_functions"] == 100
    assert result["unique_functions"] == 50
    assert result["max_depth_reached"] == 5
    assert result["total_function_calls"] == 200
    assert result["static_functions"] == 30
    assert result["rte_functions"] == 10
    assert result["autosar_functions"] == 40
    assert result["circular_dependencies_found"] == 2

    # Verify all keys present
    expected_keys = {
        "total_functions",
        "unique_functions",
        "max_depth_reached",
        "total_function_calls",
        "static_functions",
        "rte_functions",
        "autosar_functions",
        "circular_dependencies_found",
    }
    assert set(result.keys()) == expected_keys


# SWUT_DB_00020: AnalysisResult Result Container


def test_analysis_result_container():
    """SWUT_DB_00010

    Test that AnalysisResult dataclass encapsulates complete analysis results.
    """
    # Create components
    func = FunctionInfo(
        name="Root",
        return_type="void",
        file_path=Path("/src/root.c"),
        line_number=10,
        is_static=False,
    )
    tree = CallTreeNode(function_info=func, depth=0)
    stats = AnalysisStatistics(total_functions=10, unique_functions=8)
    cycle = CircularDependency(cycle=["A", "B", "A"], depth=2)

    # Create analysis result
    result = AnalysisResult(
        root_function="Root",
        call_tree=tree,
        statistics=stats,
        circular_dependencies=[cycle],
        errors=["Warning: unresolved function"],
    )

    # Verify fields
    assert result.root_function == "Root"
    assert result.call_tree == tree
    assert result.statistics == stats
    assert len(result.circular_dependencies) == 1
    assert result.circular_dependencies[0] == cycle
    assert len(result.errors) == 1
    assert result.errors[0] == "Warning: unresolved function"

    # Test with defaults
    result_default = AnalysisResult(
        root_function="Test", call_tree=tree, statistics=stats
    )
    assert len(result_default.circular_dependencies) == 0
    assert len(result_default.errors) == 0


# SWUT_DB_00021: AnalysisResult Metadata


def test_analysis_result_metadata():
    """SWUT_DB_00010

    Test that AnalysisResult includes metadata fields for analysis context and reproducibility.
    """
    # Create basic result
    func = FunctionInfo(
        name="Test",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=False,
    )
    tree = CallTreeNode(function_info=func, depth=0)
    stats = AnalysisStatistics()

    # Test with explicit metadata
    timestamp = datetime(2026, 1, 30, 12, 0, 0)
    result = AnalysisResult(
        root_function="Test",
        call_tree=tree,
        statistics=stats,
        timestamp=timestamp,
        source_directory=Path("/src"),
        max_depth_limit=5,
    )

    assert result.timestamp == timestamp
    assert result.source_directory == Path("/src")
    assert result.max_depth_limit == 5

    # Test defaults (timestamp should be near current time)
    result_default = AnalysisResult(
        root_function="Test", call_tree=tree, statistics=stats
    )

    # Verify timestamp is recent (within 1 second)
    now = datetime.now()
    time_diff = abs((now - result_default.timestamp).total_seconds())
    assert time_diff < 1.0

    # Verify other defaults
    assert result_default.source_directory is None
    assert result_default.max_depth_limit == 3


# SWUT_DB_00022: AnalysisResult Function Collection


def test_analysis_result_get_all_functions():
    """SWUT_DB_00010

    Test that AnalysisResult.get_all_functions method collects functions from call tree.
    """
    # Create tree with multiple functions
    func1 = FunctionInfo(
        name="Root",
        return_type="void",
        file_path=Path("/src/root.c"),
        line_number=10,
        is_static=False,
    )
    func2 = FunctionInfo(
        name="Child",
        return_type="void",
        file_path=Path("/src/child.c"),
        line_number=20,
        is_static=False,
    )

    root = CallTreeNode(function_info=func1, depth=0)
    child = CallTreeNode(function_info=func2, depth=1)
    root.add_child(child)

    stats = AnalysisStatistics()
    result = AnalysisResult(root_function="Root", call_tree=root, statistics=stats)

    # Collect functions
    all_funcs = result.get_all_functions()

    # Verify results
    assert len(all_funcs) == 2
    assert func1 in all_funcs
    assert func2 in all_funcs


# SWUT_DB_00023: AnalysisResult Circular Dependency Check


def test_analysis_result_has_circular_dependencies():
    """SWUT_DB_00010

    Test that AnalysisResult.has_circular_dependencies method correctly detects cycles.
    """
    # Create basic components
    func = FunctionInfo(
        name="Test",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=False,
    )
    tree = CallTreeNode(function_info=func, depth=0)
    stats = AnalysisStatistics()

    # Test with no circular dependencies
    result_no_cycles = AnalysisResult(
        root_function="Test", call_tree=tree, statistics=stats, circular_dependencies=[]
    )
    assert result_no_cycles.has_circular_dependencies() is False

    # Test with default (empty list)
    result_default = AnalysisResult(
        root_function="Test", call_tree=tree, statistics=stats
    )
    assert result_default.has_circular_dependencies() is False

    # Test with one circular dependency
    cycle = CircularDependency(cycle=["A", "B", "A"], depth=2)
    result_with_cycle = AnalysisResult(
        root_function="Test",
        call_tree=tree,
        statistics=stats,
        circular_dependencies=[cycle],
    )
    assert result_with_cycle.has_circular_dependencies() is True

    # Test with multiple circular dependencies
    cycle2 = CircularDependency(cycle=["C", "D", "C"], depth=3)
    result_multiple = AnalysisResult(
        root_function="Test",
        call_tree=tree,
        statistics=stats,
        circular_dependencies=[cycle, cycle2],
    )
    assert result_multiple.has_circular_dependencies() is True
