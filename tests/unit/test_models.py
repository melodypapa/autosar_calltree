"""Tests for models module (SWUT_MODEL_*)"""

from datetime import datetime
from pathlib import Path

from autosar_calltree.database.models import (
    AnalysisResult,
    AnalysisStatistics,
    CallTreeNode,
    CircularDependency,
    FunctionCall,
    FunctionDict,
    FunctionInfo,
    FunctionType,
    Parameter,
)


# SWUT_MODEL_00001: FunctionType Enum Values
def test_function_type_enum_values():
    """SWUT_MODEL_00001
    
    Test that FunctionType enum has all required classification values."""
    # Verify all enum values exist and have correct string representations
    assert FunctionType.AUTOSAR_FUNC.value == "autosar_func"
    assert FunctionType.AUTOSAR_FUNC_P2VAR.value == "autosar_func_p2var"
    assert FunctionType.AUTOSAR_FUNC_P2CONST.value == "autosar_func_p2const"
    assert FunctionType.TRADITIONAL_C.value == "traditional_c"
    assert FunctionType.RTE_CALL.value == "rte_call"
    assert FunctionType.UNKNOWN.value == "unknown"

    # Verify enum has exactly 6 values
    assert len(FunctionType) == 6


# SWUT_MODEL_00002: Parameter Dataclass Core Fields
def test_parameter_core_fields():
    """SWUT_MODEL_00002
    
    Test Parameter dataclass core fields."""
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


# SWUT_MODEL_00003: Parameter String Representation
def test_parameter_str_representation():
    """SWUT_MODEL_00003
    
    Test that Parameter.__str__ method formats parameters correctly."""
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


# SWUT_MODEL_00004: FunctionInfo Core Identity Fields
def test_function_info_identity_fields():
    """SWUT_MODEL_00004
    
    Test that FunctionInfo dataclass has all core identity fields."""
    # Create function with all identity fields
    func = FunctionInfo(
        name="Demo_Init",
        return_type="void",
        file_path=Path("/src/demo.c"),
        line_number=42,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
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
        function_type=FunctionType.TRADITIONAL_C,
    )
    assert func_static.is_static is True


# SWUT_MODEL_00005: FunctionInfo Type Classification
def test_function_info_type_classification():
    """SWUT_MODEL_00005
    
    Test that FunctionInfo includes function type classification and AUTOSAR-specific metadata."""
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


# SWUT_MODEL_00006: FunctionInfo Call Relationships
def test_function_info_call_relationships():
    """SWUT_MODEL_00006
    
    Test that FunctionInfo tracks bidirectional call relationships."""
    # Create function with parameters and calls
    func = FunctionInfo(
        name="Demo_Main",
        return_type="void",
        file_path=Path("/src/demo.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
        parameters=[
            Parameter(name="param1", param_type="uint32"),
            Parameter(name="param2", param_type="uint8"),
        ],
        calls=[
            FunctionCall("Helper_Function1", False),
            FunctionCall("Helper_Function2", False),
        ],
    )

    # Verify parameters list
    assert len(func.parameters) == 2
    assert func.parameters[0].name == "param1"
    assert func.parameters[1].name == "param2"

    # Verify calls list
    assert len(func.calls) == 2
    call_names = [call.name for call in func.calls]
    assert "Helper_Function1" in call_names
    assert "Helper_Function2" in call_names

    # Verify called_by set (empty initially)
    assert len(func.called_by) == 0

    # Add callers
    func.called_by.add("Caller1")
    func.called_by.add("Caller2")
    assert len(func.called_by) == 2
    assert "Caller1" in func.called_by
    assert "Caller2" in func.called_by

    # Verify set prevents duplicates
    func.called_by.add("Caller1")
    assert len(func.called_by) == 2


# SWUT_MODEL_00007: FunctionInfo Disambiguation and Module Assignment
def test_function_info_disambiguation_module():
    """SWUT_MODEL_00007
    
    Test that FunctionInfo supports qualified names and SW module assignment."""
    # Create function with qualified name and module
    func1 = FunctionInfo(
        name="Helper",
        return_type="void",
        file_path=Path("/src/module1/helper.c"),
        line_number=10,
        is_static=True,
        function_type=FunctionType.TRADITIONAL_C,
        qualified_name="module1/helper.c::Helper",
        sw_module="Module1",
    )
    assert func1.qualified_name == "module1/helper.c::Helper"
    assert func1.sw_module == "Module1"

    # Create another function with same name but different file
    func2 = FunctionInfo(
        name="Helper",
        return_type="void",
        file_path=Path("/src/module2/helper.c"),
        line_number=15,
        is_static=True,
        function_type=FunctionType.TRADITIONAL_C,
        qualified_name="module2/helper.c::Helper",
        sw_module="Module2",
    )
    assert func2.qualified_name == "module2/helper.c::Helper"
    assert func2.sw_module == "Module2"

    # Functions should be distinguishable by qualified_name
    assert func1.qualified_name != func2.qualified_name

    # Test function without module assignment
    func_no_module = FunctionInfo(
        name="Orphan",
        return_type="void",
        file_path=Path("/src/orphan.c"),
        line_number=5,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    assert func_no_module.qualified_name is None
    assert func_no_module.sw_module is None


# SWUT_MODEL_00008: FunctionInfo Hash Implementation
def test_function_info_hash():
    """SWUT_MODEL_00008
    
    Test that FunctionInfo.__hash__ enables use in sets and as dictionary keys."""
    # Create two identical functions
    func1 = FunctionInfo(
        name="TestFunc",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )

    func2 = FunctionInfo(
        name="TestFunc",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )

    # Hash should be based on (name, file_path, line_number)
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
        function_type=FunctionType.TRADITIONAL_C,
    )
    assert hash(func1) != hash(func3)

    function_set2 = {func1, func3}
    assert len(function_set2) == 2


# SWUT_MODEL_00009: FunctionInfo Equality Implementation
def test_function_info_equality():
    """SWUT_MODEL_00009
    
    Test that FunctionInfo.__eq__ compares identity fields only."""
    # Create functions with same identity but different other fields
    func1 = FunctionInfo(
        name="TestFunc",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
        parameters=[Parameter(name="p1", param_type="int")],
        calls=["Helper1"],
    )

    func2 = FunctionInfo(
        name="TestFunc",
        return_type="int",  # Different return type
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=True,  # Different static flag
        function_type=FunctionType.AUTOSAR_FUNC,  # Different type
        parameters=[Parameter(name="p2", param_type="float")],  # Different params
        calls=["Helper2"],  # Different calls
    )

    # Should be equal based on identity fields (name, file_path, line_number)
    assert func1 == func2

    # Comparison with non-FunctionInfo object
    assert func1 != "TestFunc"
    assert func1 is not None
    assert func1 != 42

    # Different identity should not be equal
    func3 = FunctionInfo(
        name="TestFunc",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=20,  # Different line
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    assert func1 != func3

    # Different file path
    func4 = FunctionInfo(
        name="TestFunc",
        return_type="void",
        file_path=Path("/src/other.c"),  # Different file
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    assert func1 != func4


# SWUT_MODEL_00010: FunctionInfo Signature Generation
def test_function_info_signature():
    """SWUT_MODEL_00010
    
    Test that FunctionInfo.get_signature generates correctly formatted signatures."""
    # Test function with no parameters
    func_no_params = FunctionInfo(
        name="Init",
        return_type="void",
        file_path=Path("/src/init.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    assert func_no_params.get_signature() == "void Init()"

    # Test function with one parameter
    func_one_param = FunctionInfo(
        name="Process",
        return_type="uint8",
        file_path=Path("/src/process.c"),
        line_number=20,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
        parameters=[Parameter(name="value", param_type="uint32")],
    )
    assert func_one_param.get_signature() == "uint8 Process(uint32 value)"

    # Test function with multiple parameters
    func_multi_params = FunctionInfo(
        name="ComplexFunc",
        return_type="Std_ReturnType",
        file_path=Path("/src/complex.c"),
        line_number=30,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
        parameters=[
            Parameter(name="id", param_type="uint32"),
            Parameter(name="data", param_type="uint8", is_pointer=True),
            Parameter(name="length", param_type="uint16"),
        ],
    )
    signature = func_multi_params.get_signature()
    assert (
        signature == "Std_ReturnType ComplexFunc(uint32 id, uint8* data, uint16 length)"
    )

    # Test function with complex parameters
    func_complex_params = FunctionInfo(
        name="AdvancedFunc",
        return_type="void",
        file_path=Path("/src/advanced.c"),
        line_number=40,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
        parameters=[
            Parameter(
                name="config",
                param_type="ConfigType",
                is_const=True,
                is_pointer=True,
                memory_class="APPL_DATA",
            )
        ],
    )
    assert (
        func_complex_params.get_signature()
        == "void AdvancedFunc(const ConfigType* config [APPL_DATA])"
    )


# SWUT_MODEL_00011: FunctionInfo RTE Function Detection
def test_function_info_rte_detection():
    """SWUT_MODEL_00011
    
    Test that FunctionInfo.is_rte_function correctly detects RTE functions."""
    # Test RTE function by naming convention
    func_rte_call = FunctionInfo(
        name="Rte_Call_StartTrigger",
        return_type="void",
        file_path=Path("/src/rte.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
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


# SWUT_MODEL_00012: CallTreeNode Core Structure
def test_call_tree_node_structure():
    """SWUT_MODEL_00012
    
    Test that CallTreeNode dataclass has core fields for hierarchical tree structure."""
    # Create function info for node
    func_info = FunctionInfo(
        name="ParentFunc",
        return_type="void",
        file_path=Path("/src/parent.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
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
        function_type=FunctionType.TRADITIONAL_C,
    )
    child_node = CallTreeNode(
        function_info=child_func, depth=1, children=[], parent=node
    )

    assert child_node.depth == 1
    assert child_node.parent == node


# SWUT_MODEL_00013: CallTreeNode State Flags
def test_call_tree_node_state_flags():
    """SWUT_MODEL_00013
    
    Test that CallTreeNode includes state flags for recursive calls, truncation, and call frequency."""
    func = FunctionInfo(
        name="TestFunc",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
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

    # Test all flags
    node_all = CallTreeNode(
        function_info=func, depth=3, is_recursive=True, is_truncated=False, call_count=5
    )
    assert node_all.is_recursive is True
    assert node_all.is_truncated is False
    assert node_all.call_count == 5


# SWUT_MODEL_00014: CallTreeNode Tree Manipulation
def test_call_tree_node_add_child():
    """SWUT_MODEL_00014
    
    Test that CallTreeNode.add_child correctly builds parent-child relationships."""
    # Create parent and child nodes
    parent_func = FunctionInfo(
        name="Parent",
        return_type="void",
        file_path=Path("/src/parent.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    parent = CallTreeNode(function_info=parent_func, depth=0)

    child1_func = FunctionInfo(
        name="Child1",
        return_type="void",
        file_path=Path("/src/child1.c"),
        line_number=20,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    child1 = CallTreeNode(function_info=child1_func, depth=1)

    child2_func = FunctionInfo(
        name="Child2",
        return_type="void",
        file_path=Path("/src/child2.c"),
        line_number=30,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
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


# SWUT_MODEL_00015: CallTreeNode Function Collection
def test_call_tree_node_get_all_functions():
    """SWUT_MODEL_00015
    
    Test that CallTreeNode.get_all_functions collects all unique functions in subtree."""
    # Create function infos
    func1 = FunctionInfo(
        name="Func1",
        return_type="void",
        file_path=Path("/src/f1.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    func2 = FunctionInfo(
        name="Func2",
        return_type="void",
        file_path=Path("/src/f2.c"),
        line_number=20,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    func3 = FunctionInfo(
        name="Func3",
        return_type="void",
        file_path=Path("/src/f3.c"),
        line_number=30,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
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


# SWUT_MODEL_00016: CallTreeNode Depth Calculation
def test_call_tree_node_get_max_depth():
    """SWUT_MODEL_00016
    
    Test that CallTreeNode.get_max_depth calculates maximum depth of subtree."""
    func = FunctionInfo(
        name="Func",
        return_type="void",
        file_path=Path("/src/f.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
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


# SWUT_MODEL_00017: CircularDependency Core Structure
def test_circular_dependency_structure():
    """SWUT_MODEL_00017
    
    Test that CircularDependency dataclass has core fields for representing detected cycles."""
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


# SWUT_MODEL_00018: CircularDependency String Representation
def test_circular_dependency_str():
    """SWUT_MODEL_00018
    
    Test that CircularDependency.__str__ formats cycles in readable arrow notation."""
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


# SWUT_MODEL_00019: AnalysisStatistics Counters
def test_analysis_statistics_counters():
    """SWUT_MODEL_00019
    
    Test that AnalysisStatistics dataclass has all counter fields with correct defaults."""
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

    # Test partial values (others default)
    stats3 = AnalysisStatistics(total_functions=25, unique_functions=20)
    assert stats3.total_functions == 25
    assert stats3.unique_functions == 20
    assert stats3.max_depth_reached == 0  # Default
    assert stats3.circular_dependencies_found == 0  # Default


# SWUT_MODEL_00020: AnalysisStatistics Dictionary Conversion
def test_analysis_statistics_to_dict():
    """SWUT_MODEL_00020
    
    Test that AnalysisStatistics.to_dict converts statistics to dictionary format."""
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

    # Test with default values
    stats_default = AnalysisStatistics()
    result_default = stats_default.to_dict()
    for key in expected_keys:
        assert result_default[key] == 0


# SWUT_MODEL_00021: AnalysisResult Result Container
def test_analysis_result_container():
    """SWUT_MODEL_00021
    
    Test that AnalysisResult dataclass encapsulates complete analysis results."""
    # Create components
    func = FunctionInfo(
        name="Root",
        return_type="void",
        file_path=Path("/src/root.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
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


# SWUT_MODEL_00022: AnalysisResult Metadata
def test_analysis_result_metadata():
    """SWUT_MODEL_00022
    
    Test that AnalysisResult includes metadata fields for analysis context."""
    # Create basic result
    func = FunctionInfo(
        name="Test",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
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
    assert result_default.max_depth_limit == 3  # Default


# SWUT_MODEL_00023: AnalysisResult Function Collection
def test_analysis_result_get_all_functions():
    """SWUT_MODEL_00023
    
    Test that AnalysisResult.get_all_functions collects functions from call tree."""
    # Create tree with multiple functions
    func1 = FunctionInfo(
        name="Root",
        return_type="void",
        file_path=Path("/src/root.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    func2 = FunctionInfo(
        name="Child",
        return_type="void",
        file_path=Path("/src/child.c"),
        line_number=20,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
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

    # Test with None call_tree (should raise error)
    result_no_tree = AnalysisResult(
        root_function="Missing", call_tree=None, statistics=stats
    )

    # get_all_functions() returns an empty set when call_tree is None
    # (doesn't raise an error, just returns empty)
    all_funcs_none = result_no_tree.get_all_functions()
    assert len(all_funcs_none) == 0 or all_funcs_none is None or all_funcs_none == set()


# SWUT_MODEL_00024: AnalysisResult Circular Dependency Check
def test_analysis_result_has_circular_deps():
    """SWUT_MODEL_00024
    
    Test that AnalysisResult.has_circular_dependencies correctly detects cycles."""
    # Create basic components
    func = FunctionInfo(
        name="Test",
        return_type="void",
        file_path=Path("/src/test.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
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


# SWUT_MODEL_00025: FunctionDict Type Alias
def test_function_dict_type_alias():
    """SWUT_MODEL_00025
    
    Test that FunctionDict type alias correctly represents mapping."""
    # Create FunctionDict instance
    func1 = FunctionInfo(
        name="COM_Init",
        return_type="void",
        file_path=Path("/src/com.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    func2 = FunctionInfo(
        name="COM_Init",  # Same name, different file
        return_type="void",
        file_path=Path("/src/com_decl.c"),
        line_number=5,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )
    func3 = FunctionInfo(
        name="Demo_Init",
        return_type="void",
        file_path=Path("/src/demo.c"),
        line_number=15,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )

    # Build function dict
    func_dict: FunctionDict = {
        "COM_Init": [func1, func2],  # Multiple definitions
        "Demo_Init": [func3],  # Single definition
    }

    # Verify structure
    assert isinstance(func_dict, dict)
    assert "COM_Init" in func_dict
    assert "Demo_Init" in func_dict
    assert len(func_dict["COM_Init"]) == 2
    assert len(func_dict["Demo_Init"]) == 1
    assert func_dict["COM_Init"][0] == func1
    assert func_dict["COM_Init"][1] == func2

    # Verify values are FunctionInfo objects
    assert all(
        isinstance(f, FunctionInfo) for funcs in func_dict.values() for f in funcs
    )


# Additional tests for FunctionCall.__str__ (covers lines 45-51)
def test_function_call_str_with_loop_condition():
    """Test FunctionCall.__str__ with loop condition (covers line 45-46)."""
    call = FunctionCall(
        name="ProcessItem",
        is_conditional=False,
        condition=None,
        is_loop=True,
        loop_condition="i < 10"
    )
    assert str(call) == "ProcessItem [loop: i < 10]"


def test_function_call_str_with_condition():
    """Test FunctionCall.__str__ with condition (covers line 47-48)."""
    call = FunctionCall(
        name="SendData",
        is_conditional=True,
        condition="mode == ACTIVE",
        is_loop=False,
        loop_condition=None
    )
    assert str(call) == "SendData [mode == ACTIVE]"


def test_function_call_str_conditional_only():
    """Test FunctionCall.__str__ with conditional flag only (covers line 49-51)."""
    call = FunctionCall(
        name="OptionalCall",
        is_conditional=True,
        condition=None,
        is_loop=False,
        loop_condition=None
    )
    assert str(call) == "OptionalCall [conditional]"


def test_function_call_str_loop_only():
    """Test FunctionCall.__str__ with loop flag only (covers line 49-51)."""
    call = FunctionCall(
        name="LoopCall",
        is_conditional=False,
        condition=None,
        is_loop=True,
        loop_condition=None
    )
    assert str(call) == "LoopCall [loop]"


def test_function_call_str_plain():
    """Test FunctionCall.__str__ with no flags (covers line 49-51)."""
    call = FunctionCall(
        name="SimpleCall",
        is_conditional=False,
        condition=None,
        is_loop=False,
        loop_condition=None
    )
    assert str(call) == "SimpleCall"


def test_function_call_str_conditional_and_loop():
    """Test FunctionCall.__str__ with both conditional and loop flags (covers line 49-51)."""
    call = FunctionCall(
        name="ComplexCall",
        is_conditional=True,
        condition=None,
        is_loop=True,
        loop_condition=None
    )
    assert str(call) == "ComplexCall [conditional] [loop]"

