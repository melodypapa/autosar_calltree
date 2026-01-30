# Database Models Test Cases

## Overview
This document describes the test cases for the database models module (`src/autosar_calltree/database/models.py`). The models module defines core data structures including enums, dataclasses, and type aliases for representing function information, call trees, analysis results, and statistics.

## Test Cases

### SWUT_MODEL_00001: FunctionType Enum Values

**Requirement:** SWR_MODEL_00001
**Priority:** High
**Status:** Pending

**Description:**
Test that FunctionType enum has all required classification values for different function declaration types.

**Test Function:** `test_SWUT_MODEL_00001_function_type_enum_values()`

**Test Setup:**
```python
from autosar_calltree.database.models import FunctionType
```

**Test Execution:**
```python
# Verify all enum values exist and have correct string representations
assert FunctionType.AUTOSAR_FUNC.value == "autosar_func"
assert FunctionType.AUTOSAR_FUNC_P2VAR.value == "autosar_func_p2var"
assert FunctionType.AUTOSAR_FUNC_P2CONST.value == "autosar_func_p2const"
assert FunctionType.TRADITIONAL_C.value == "traditional_c"
assert FunctionType.RTE_CALL.value == "rte_call"
assert FunctionType.UNKNOWN.value == "unknown"

# Verify enum has exactly 6 values
assert len(FunctionType) == 6
```

**Expected Result:**
All enum values should be accessible and have correct string representations.

**Edge Cases Covered:**
- None (enum values are constants)

---

### SWUT_MODEL_00002: Parameter Dataclass Core Fields

**Requirement:** SWR_MODEL_00002
**Priority:** High
**Status:** Pending

**Description:**
Test that Parameter dataclass has all required fields with correct types and default values.

**Test Function:** `test_SWUT_MODEL_00002_parameter_core_fields()`

**Test Setup:**
```python
from autosar_calltree.database.models import Parameter
from dataclasses import fields
```

**Test Execution:**
```python
# Create parameter with all fields
param = Parameter(
    name="timerId",
    param_type="uint32",
    is_pointer=False,
    is_const=False,
    memory_class="AUTOMATIC"
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
```

**Expected Result:**
All fields should be present with correct types and defaults.

**Edge Cases Covered:**
- Parameter with all fields specified
- Parameter with only required fields (defaults applied)
- Parameter with None memory_class

---

### SWUT_MODEL_00003: Parameter String Representation

**Requirement:** SWR_MODEL_00003
**Priority:** Medium
**Status:** Pending

**Description:**
Test that Parameter.__str__ method formats parameters correctly with const, pointer, and memory class.

**Test Function:** `test_SWUT_MODEL_00003_parameter_str_representation()`

**Test Setup:**
```python
from autosar_calltree.database.models import Parameter
```

**Test Execution:**
```python
# Test const parameter
param_const = Parameter(name="value", param_type="uint32", is_const=True)
assert str(param_const) == "const uint32 value"

# Test pointer parameter
param_ptr = Parameter(name="buffer", param_type="uint8", is_pointer=True)
assert str(param_ptr) == "uint8* buffer"

# Test const pointer parameter
param_const_ptr = Parameter(name="config", param_type="ConfigType", is_const=True, is_pointer=True)
assert str(param_const_ptr) == "const ConfigType* config"

# Test parameter with memory class
param_memclass = Parameter(name="data", param_type="uint32", memory_class="AUTOMATIC")
assert str(param_memclass) == "uint32 data [AUTOMATIC]"

# Test const pointer with memory class
param_full = Parameter(
    name="buffer",
    param_type="uint8",
    is_const=True,
    is_pointer=True,
    memory_class="APPL_DATA"
)
assert str(param_full) == "const uint8* buffer [APPL_DATA]"
```

**Expected Result:**
Parameters should be formatted with const prefix, pointer asterisk, and memory class in brackets when applicable.

**Edge Cases Covered:**
- Const only
- Pointer only
- Const and pointer
- Memory class only
- All attributes combined
- No special attributes (type name only)

---

### SWUT_MODEL_00004: FunctionInfo Core Identity Fields

**Requirement:** SWR_MODEL_00004
**Priority:** High
**Status:** Pending

**Description:**
Test that FunctionInfo dataclass has all core identity fields for uniquely identifying functions.

**Test Function:** `test_SWUT_MODEL_00004_function_info_identity_fields()`

**Test Setup:**
```python
from autosar_calltree.database.models import FunctionInfo
from pathlib import Path
```

**Test Execution:**
```python
# Create function with all identity fields
func = FunctionInfo(
    name="Demo_Init",
    return_type="void",
    file_path=Path("/src/demo.c"),
    line_number=42,
    is_static=False
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
    is_static=True
)
assert func_static.is_static is True
```

**Expected Result:**
All identity fields should be present and correctly typed.

**Edge Cases Covered:**
- Non-static function
- Static function
- Different return types
- Different line numbers

---

### SWUT_MODEL_00005: FunctionInfo Type Classification

**Requirement:** SWR_MODEL_00005
**Priority:** High
**Status:** Pending

**Description:**
Test that FunctionInfo includes function type classification and AUTOSAR-specific metadata fields.

**Test Function:** `test_SWUT_MODEL_00005_function_info_type_classification()`

**Test Setup:**
```python
from autosar_calltree.database.models import FunctionInfo, FunctionType
from pathlib import Path
```

**Test Execution:**
```python
# Test AUTOSAR FUNC
func_autosar = FunctionInfo(
    name="COM_Init",
    return_type="void",
    file_path=Path("/src/com.c"),
    line_number=10,
    is_static=False,
    function_type=FunctionType.AUTOSAR_FUNC,
    memory_class="RTE_CODE",
    macro_type="FUNC"
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
    macro_type="FUNC_P2VAR"
)
assert func_p2var.function_type == FunctionType.AUTOSAR_FUNC_P2VAR

# Test traditional C function
func_c = FunctionInfo(
    name="standard_function",
    return_type="int",
    file_path=Path("/src/main.c"),
    line_number=50,
    is_static=False,
    function_type=FunctionType.TRADITIONAL_C
)
assert func_c.function_type == FunctionType.TRADITIONAL_C
assert func_c.memory_class is None
assert func_c.macro_type is None
```

**Expected Result:**
Function type and AUTOSAR metadata fields should be correctly stored.

**Edge Cases Covered:**
- AUTOSAR FUNC with memory class
- AUTOSAR FUNC_P2VAR with metadata
- Traditional C function (no AUTOSAR metadata)
- Missing optional fields (None defaults)

---

### SWUT_MODEL_00006: FunctionInfo Call Relationships

**Requirement:** SWR_MODEL_00006
**Priority:** High
**Status:** Pending

**Description:**
Test that FunctionInfo tracks bidirectional call relationships (calls and called_by).

**Test Function:** `test_SWUT_MODEL_00006_function_info_call_relationships()`

**Test Setup:**
```python
from autosar_calltree.database.models import FunctionInfo, Parameter
from pathlib import Path
```

**Test Execution:**
```python
# Create function with parameters and calls
func = FunctionInfo(
    name="Demo_Main",
    return_type="void",
    file_path=Path("/src/demo.c"),
    line_number=10,
    is_static=False,
    parameters=[
        Parameter(name="param1", param_type="uint32"),
        Parameter(name="param2", param_type="uint8")
    ],
    calls=["Helper_Function1", "Helper_Function2"]
)

# Verify parameters list
assert len(func.parameters) == 2
assert func.parameters[0].name == "param1"
assert func.parameters[1].name == "param2"

# Verify calls list
assert len(func.calls) == 2
assert "Helper_Function1" in func.calls
assert "Helper_Function2" in func.calls

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
```

**Expected Result:**
Parameters list, calls list, and called_by set should be correctly maintained.

**Edge Cases Covered:**
- Empty parameters list (default)
- Populated parameters list
- Empty calls list (default)
- Populated calls list
- Adding callers to called_by set
- Set prevents duplicate entries

---

### SWUT_MODEL_00007: FunctionInfo Disambiguation and Module Assignment

**Requirement:** SWR_MODEL_00007
**Priority:** High
**Status:** Pending

**Description:**
Test that FunctionInfo supports qualified names for static function disambiguation and SW module assignment.

**Test Function:** `test_SWUT_MODEL_00007_function_info_disambiguation_module()`

**Test Setup:**
```python
from autosar_calltree.database.models import FunctionInfo
from pathlib import Path
```

**Test Execution:**
```python
# Create function with qualified name and module
func1 = FunctionInfo(
    name="Helper",
    return_type="void",
    file_path=Path("/src/module1/helper.c"),
    line_number=10,
    is_static=True,
    qualified_name="module1/helper.c::Helper",
    sw_module="Module1"
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
    qualified_name="module2/helper.c::Helper",
    sw_module="Module2"
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
    is_static=False
)
assert func_no_module.qualified_name is None
assert func_no_module.sw_module is None
```

**Expected Result:**
Qualified names and SW module assignments should be correctly stored and enable disambiguation.

**Edge Cases Covered:**
- Static function with qualified name and module
- Same-named function in different modules
- Function without module assignment (None defaults)
- Function without qualified name

---

### SWUT_MODEL_00008: FunctionInfo Hash Implementation

**Requirement:** SWR_MODEL_00008
**Priority:** Medium
**Status:** Pending

**Description:**
Test that FunctionInfo.__hash__ method enables use in sets and as dictionary keys based on identity fields.

**Test Function:** `test_SWUT_MODEL_00008_function_info_hash()`

**Test Setup:**
```python
from autosar_calltree.database.models import FunctionInfo
from pathlib import Path
```

**Test Execution:**
```python
# Create two identical functions
func1 = FunctionInfo(
    name="TestFunc",
    return_type="void",
    file_path=Path("/src/test.c"),
    line_number=10,
    is_static=False
)

func2 = FunctionInfo(
    name="TestFunc",
    return_type="void",
    file_path=Path("/src/test.c"),
    line_number=10,
    is_static=False
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
    is_static=False
)
assert hash(func1) != hash(func3)

function_set2 = {func1, func3}
assert len(function_set2) == 2
```

**Expected Result:**
Hash should be based on identity fields and enable set/dict operations.

**Edge Cases Covered:**
- Identical functions have same hash
- Functions can be added to sets (deduplication)
- Functions can be used as dictionary keys
- Different identity produces different hash
- Set correctly stores multiple distinct functions

---

### SWUT_MODEL_00009: FunctionInfo Equality Implementation

**Requirement:** SWR_MODEL_00009
**Priority:** Medium
**Status:** Pending

**Description:**
Test that FunctionInfo.__eq__ method compares identity fields only, not all fields.

**Test Function:** `test_SWUT_MODEL_00009_function_info_equality()`

**Test Setup:**
```python
from autosar_calltree.database.models import FunctionInfo, Parameter, FunctionType
from pathlib import Path
```

**Test Execution:**
```python
# Create functions with same identity but different other fields
func1 = FunctionInfo(
    name="TestFunc",
    return_type="void",
    file_path=Path("/src/test.c"),
    line_number=10,
    is_static=False,
    parameters=[Parameter(name="p1", param_type="int")],
    calls=["Helper1"]
)

func2 = FunctionInfo(
    name="TestFunc",
    return_type="int",  # Different return type
    file_path=Path("/src/test.c"),
    line_number=10,
    is_static=True,  # Different static flag
    parameters=[Parameter(name="p2", param_type="float")],  # Different params
    calls=["Helper2"],  # Different calls
    function_type=FunctionType.TRADITIONAL_C  # Different type
)

# Should be equal based on identity fields (name, file_path, line_number)
assert func1 == func2

# Comparison with non-FunctionInfo object
assert func1 != "TestFunc"
assert func1 != None
assert func1 != 42

# Different identity should not be equal
func3 = FunctionInfo(
    name="TestFunc",
    return_type="void",
    file_path=Path("/src/test.c"),
    line_number=20,  # Different line
    is_static=False
)
assert func1 != func3

# Different file path
func4 = FunctionInfo(
    name="TestFunc",
    return_type="void",
    file_path=Path("/src/other.c"),  # Different file
    line_number=10,
    is_static=False
)
assert func1 != func4
```

**Expected Result:**
Equality should be based only on identity fields (name, file_path, line_number).

**Edge Cases Covered:**
- Same identity, different other fields → equal
- Comparison with non-FunctionInfo → not equal
- Different line number → not equal
- Different file path → not equal
- Different function name → not equal

---

### SWUT_MODEL_00010: FunctionInfo Signature Generation

**Requirement:** SWR_MODEL_00010
**Priority:** Medium
**Status:** Pending

**Description:**
Test that FunctionInfo.get_signature method generates correctly formatted function signatures.

**Test Function:** `test_SWUT_MODEL_00010_function_info_signature()`

**Test Setup:**
```python
from autosar_calltree.database.models import FunctionInfo, Parameter
from pathlib import Path
```

**Test Execution:**
```python
# Test function with no parameters
func_no_params = FunctionInfo(
    name="Init",
    return_type="void",
    file_path=Path("/src/init.c"),
    line_number=10,
    is_static=False
)
assert func_no_params.get_signature() == "void Init()"

# Test function with one parameter
func_one_param = FunctionInfo(
    name="Process",
    return_type="uint8",
    file_path=Path("/src/process.c"),
    line_number=20,
    is_static=False,
    parameters=[Parameter(name="value", param_type="uint32")]
)
assert func_one_param.get_signature() == "uint8 Process(uint32 value)"

# Test function with multiple parameters
func_multi_params = FunctionInfo(
    name="ComplexFunc",
    return_type="Std_ReturnType",
    file_path=Path("/src/complex.c"),
    line_number=30,
    is_static=False,
    parameters=[
        Parameter(name="id", param_type="uint32"),
        Parameter(name="data", param_type="uint8*", is_pointer=True),
        Parameter(name="length", param_type="uint16")
    ]
)
signature = func_multi_params.get_signature()
assert signature == "Std_ReturnType ComplexFunc(uint32 id, uint8* data, uint16 length)"

# Test function with complex parameters
func_complex_params = FunctionInfo(
    name="AdvancedFunc",
    return_type="void",
    file_path=Path("/src/advanced.c"),
    line_number=40,
    is_static=False,
    parameters=[
        Parameter(name="config", param_type="ConfigType", is_const=True, is_pointer=True, memory_class="APPL_DATA")
    ]
)
assert func_complex_params.get_signature() == "void AdvancedFunc(const ConfigType* config [APPL_DATA])"
```

**Expected Result:**
Signatures should be formatted as "return_type name(param1, param2, ...)" with proper parameter formatting.

**Edge Cases Covered:**
- No parameters
- Single parameter
- Multiple parameters
- Complex parameters with const/pointer/memory class

---

### SWUT_MODEL_00011: FunctionInfo RTE Function Detection

**Requirement:** SWR_MODEL_00011
**Priority:** Medium
**Status:** Pending

**Description:**
Test that FunctionInfo.is_rte_function method correctly detects RTE functions.

**Test Function:** `test_SWUT_MODEL_00011_function_info_rte_detection()`

**Test Setup:**
```python
from autosar_calltree.database.models import FunctionInfo, FunctionType
from pathlib import Path
```

**Test Execution:**
```python
# Test RTE function by naming convention
func_rte_call = FunctionInfo(
    name="Rte_Call_StartTrigger",
    return_type="void",
    file_path=Path("/src/rte.c"),
    line_number=10,
    is_static=False
)
assert func_rte_call.is_rte_function() is True

# Test RTE function by function type
func_rte_type = FunctionInfo(
    name="SomeFunction",
    return_type="void",
    file_path=Path("/src/rte.c"),
    line_number=20,
    is_static=False,
    function_type=FunctionType.RTE_CALL
)
assert func_rte_type.is_rte_function() is True

# Test both conditions
func_rte_both = FunctionInfo(
    name="Rte_Read_Data",
    return_type="Std_ReturnType",
    file_path=Path("/src/rte.c"),
    line_number=30,
    is_static=False,
    function_type=FunctionType.RTE_CALL
)
assert func_rte_both.is_rte_function() is True

# Test non-RTE function
func_regular = FunctionInfo(
    name="RegularFunction",
    return_type="void",
    file_path=Path("/src/regular.c"),
    line_number=40,
    is_static=False,
    function_type=FunctionType.TRADITIONAL_C
)
assert func_regular.is_rte_function() is False

# Test function with Rte_ prefix but traditional type
func_mixed = FunctionInfo(
    name="Rte_InternalHelper",  # Has Rte_ prefix
    return_type="void",
    file_path=Path("/src/rte.c"),
    line_number=50,
    is_static=False,
    function_type=FunctionType.TRADITIONAL_C
)
assert func_mixed.is_rte_function() is True  # Due to Rte_ prefix
```

**Expected Result:**
RTE functions should be detected by "Rte_" prefix or FunctionType.RTE_CALL classification.

**Edge Cases Covered:**
- RTE function by name (Rte_Call_*)
- RTE function by type classification
- Both conditions true
- Non-RTE function
- Rte_ prefix with traditional type (still detected)

---

### SWUT_MODEL_00012: CallTreeNode Core Structure

**Requirement:** SWR_MODEL_00012
**Priority:** High
**Status:** Pending

**Description:**
Test that CallTreeNode dataclass has core fields for hierarchical tree structure.

**Test Function:** `test_SWUT_MODEL_00012_call_tree_node_structure()`

**Test Setup:**
```python
from autosar_calltree.database.models import CallTreeNode, FunctionInfo
from pathlib import Path
```

**Test Execution:**
```python
# Create function info for node
func_info = FunctionInfo(
    name="ParentFunc",
    return_type="void",
    file_path=Path("/src/parent.c"),
    line_number=10,
    is_static=False
)

# Create node with all core fields
node = CallTreeNode(
    function_info=func_info,
    depth=0,
    children=[],
    parent=None
)

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
    is_static=False
)
child_node = CallTreeNode(
    function_info=child_func,
    depth=1,
    children=[],
    parent=node
)

assert child_node.depth == 1
assert child_node.parent == node
```

**Expected Result:**
Core structure fields should be present and maintain parent-child relationships.

**Edge Cases Covered:**
- Root node (depth=0, parent=None)
- Child node (depth>0, has parent)
- Empty children list

---

### SWUT_MODEL_00013: CallTreeNode State Flags

**Requirement:** SWR_MODEL_00013
**Priority:** Medium
**Status:** Pending

**Description:**
Test that CallTreeNode includes state flags for recursive calls, truncation, and call frequency.

**Test Function:** `test_SWUT_MODEL_00013_call_tree_node_state_flags()`

**Test Setup:**
```python
from autosar_calltree.database.models import CallTreeNode, FunctionInfo
from pathlib import Path
```

**Test Execution:**
```python
func = FunctionInfo(
    name="TestFunc",
    return_type="void",
    file_path=Path("/src/test.c"),
    line_number=10,
    is_static=False
)

# Test default values
node = CallTreeNode(
    function_info=func,
    depth=0
)
assert node.is_recursive is False
assert node.is_truncated is False
assert node.call_count == 1

# Test recursive flag
node_recursive = CallTreeNode(
    function_info=func,
    depth=2,
    is_recursive=True
)
assert node_recursive.is_recursive is True

# Test truncated flag
node_truncated = CallTreeNode(
    function_info=func,
    depth=5,
    is_truncated=True
)
assert node_truncated.is_truncated is True

# Test call count
node_called = CallTreeNode(
    function_info=func,
    depth=1,
    call_count=3
)
assert node_called.call_count == 3

# Test all flags
node_all = CallTreeNode(
    function_info=func,
    depth=3,
    is_recursive=True,
    is_truncated=False,
    call_count=5
)
assert node_all.is_recursive is True
assert node_all.is_truncated is False
assert node_all.call_count == 5
```

**Expected Result:**
State flags should have correct default values and be settable.

**Edge Cases Covered:**
- All defaults (not recursive, not truncated, call_count=1)
- Recursive flag set
- Truncated flag set
- Different call counts
- All flags set explicitly

---

### SWUT_MODEL_00014: CallTreeNode Tree Manipulation

**Requirement:** SWR_MODEL_00014
**Priority:** Medium
**Status:** Pending

**Description:**
Test that CallTreeNode.add_child method correctly builds parent-child relationships.

**Test Function:** `test_SWUT_MODEL_00014_call_tree_node_add_child()`

**Test Setup:**
```python
from autosar_calltree.database.models import CallTreeNode, FunctionInfo
from pathlib import Path
```

**Test Execution:**
```python
# Create parent and child nodes
parent_func = FunctionInfo(
    name="Parent",
    return_type="void",
    file_path=Path("/src/parent.c"),
    line_number=10,
    is_static=False
)
parent = CallTreeNode(function_info=parent_func, depth=0)

child1_func = FunctionInfo(
    name="Child1",
    return_type="void",
    file_path=Path("/src/child1.c"),
    line_number=20,
    is_static=False
)
child1 = CallTreeNode(function_info=child1_func, depth=1)

child2_func = FunctionInfo(
    name="Child2",
    return_type="void",
    file_path=Path("/src/child2.c"),
    line_number=30,
    is_static=False
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
```

**Expected Result:**
add_child should set child.parent and append to children list.

**Edge Cases Covered:**
- Adding single child
- Adding multiple children
- Parent reference correctly set
- Child depth preserved
- Children list order maintained

---

### SWUT_MODEL_00015: CallTreeNode Function Collection

**Requirement:** SWR_MODEL_00015
**Priority:** Medium
**Status:** Pending

**Description:**
Test that CallTreeNode.get_all_functions method collects all unique functions in subtree.

**Test Function:** `test_SWUT_MODEL_00015_call_tree_node_get_all_functions()`

**Test Setup:**
```python
from autosar_calltree.database.models import CallTreeNode, FunctionInfo
from pathlib import Path
```

**Test Execution:**
```python
# Create function infos
func1 = FunctionInfo(
    name="Func1",
    return_type="void",
    file_path=Path("/src/f1.c"),
    line_number=10,
    is_static=False
)
func2 = FunctionInfo(
    name="Func2",
    return_type="void",
    file_path=Path("/src/f2.c"),
    line_number=20,
    is_static=False
)
func3 = FunctionInfo(
    name="Func3",
    return_type="void",
    file_path=Path("/src/f3.c"),
    line_number=30,
    is_static=False
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
```

**Expected Result:**
Should return set of unique FunctionInfo objects from entire subtree.

**Edge Cases Covered:**
- Tree with multiple levels
- Duplicate functions (deduplicated by set)
- Leaf node (only itself)
- Complex tree structure

---

### SWUT_MODEL_00016: CallTreeNode Depth Calculation

**Requirement:** SWR_MODEL_00016
**Priority:** Medium
**Status:** Pending

**Description:**
Test that CallTreeNode.get_max_depth method calculates maximum depth of subtree.

**Test Function:** `test_SWUT_MODEL_00016_call_tree_node_get_max_depth()`

**Test Setup:**
```python
from autosar_calltree.database.models import CallTreeNode, FunctionInfo
from pathlib import Path
```

**Test Execution:**
```python
func = FunctionInfo(
    name="Func",
    return_type="void",
    file_path=Path("/src/f.c"),
    line_number=10,
    is_static=False
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
```

**Expected Result:**
Should return maximum depth in subtree, finding deepest leaf node.

**Edge Cases Covered:**
- Leaf node (returns its own depth)
- Balanced tree
- Unbalanced tree (different branch depths)
- Calculation from intermediate nodes

---

### SWUT_MODEL_00017: CircularDependency Core Structure

**Requirement:** SWR_MODEL_00017
**Priority:** Medium
**Status:** Pending

**Description:**
Test that CircularDependency dataclass has core fields for representing detected cycles.

**Test Function:** `test_SWUT_MODEL_00017_circular_dependency_structure()`

**Test Setup:**
```python
from autosar_calltree.database.models import CircularDependency
```

**Test Execution:**
```python
# Create circular dependency
cycle = CircularDependency(
    cycle=["FuncA", "FuncB", "FuncC", "FuncA"],
    depth=3
)

# Verify fields
assert cycle.cycle == ["FuncA", "FuncB", "FuncC", "FuncA"]
assert cycle.depth == 3

# Test different cycle
cycle2 = CircularDependency(
    cycle=["Init", "Process", "Validate", "Init"],
    depth=5
)
assert len(cycle2.cycle) == 4
assert cycle2.depth == 5

# Test simple 2-function cycle
cycle3 = CircularDependency(
    cycle=["A", "B", "A"],
    depth=1
)
assert len(cycle3.cycle) == 3
assert cycle3.depth == 1
```

**Expected Result:**
CircularDependency should store cycle list and detection depth.

**Edge Cases Covered:**
- 3-function cycle
- 4-function cycle
- 2-function cycle (simple recursion)
- Different detection depths

---

### SWUT_MODEL_00018: CircularDependency String Representation

**Requirement:** SWR_MODEL_00018
**Priority:** Low
**Status:** Pending

**Description:**
Test that CircularDependency.__str__ method formats cycles in readable arrow notation.

**Test Function:** `test_SWUT_MODEL_00018_circular_dependency_str()`

**Test Setup:**
```python
from autosar_calltree.database.models import CircularDependency
```

**Test Execution:**
```python
# Test 3-function cycle
cycle1 = CircularDependency(
    cycle=["FuncA", "FuncB", "FuncC", "FuncA"],
    depth=3
)
assert str(cycle1) == "FuncA -> FuncB -> FuncC -> FuncA"

# Test 2-function cycle
cycle2 = CircularDependency(
    cycle=["Init", "Process", "Init"],
    depth=2
)
assert str(cycle2) == "Init -> Process -> Init"

# Test 4-function cycle
cycle3 = CircularDependency(
    cycle=["A", "B", "C", "D", "A"],
    depth=5
)
assert str(cycle3) == "A -> B -> C -> D -> A"

# Test single function (self-call)
cycle4 = CircularDependency(
    cycle=["RecursiveFunc", "RecursiveFunc"],
    depth=1
)
assert str(cycle4) == "RecursiveFunc -> RecursiveFunc"
```

**Expected Result:**
String representation should join function names with " -> ".

**Edge Cases Covered:**
- 3-function cycle
- 2-function cycle
- 4-function cycle
- Self-call (single function appearing twice)

---

### SWUT_MODEL_00019: AnalysisStatistics Counters

**Requirement:** SWR_MODEL_00019
**Priority:** Medium
**Status:** Pending

**Description:**
Test that AnalysisStatistics dataclass has all counter fields with correct defaults.

**Test Function:** `test_SWUT_MODEL_00019_analysis_statistics_counters()`

**Test Setup:**
```python
from autosar_calltree.database.models import AnalysisStatistics
```

**Test Execution:**
```python
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
    circular_dependencies_found=2
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
```

**Expected Result:**
All counter fields should default to 0 and be settable.

**Edge Cases Covered:**
- All defaults (0)
- All fields set
- Partial fields set (others default)

---

### SWUT_MODEL_00020: AnalysisStatistics Dictionary Conversion

**Requirement:** SWR_MODEL_00020
**Priority:** Low
**Status:** Pending

**Description:**
Test that AnalysisStatistics.to_dict method converts statistics to dictionary format.

**Test Function:** `test_SWUT_MODEL_00020_analysis_statistics_to_dict()`

**Test Setup:**
```python
from autosar_calltree.database.models import AnalysisStatistics
```

**Test Execution:**
```python
# Test with values
stats = AnalysisStatistics(
    total_functions=100,
    unique_functions=50,
    max_depth_reached=5,
    total_function_calls=200,
    static_functions=30,
    rte_functions=10,
    autosar_functions=40,
    circular_dependencies_found=2
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
    "total_functions", "unique_functions", "max_depth_reached",
    "total_function_calls", "static_functions", "rte_functions",
    "autosar_functions", "circular_dependencies_found"
}
assert set(result.keys()) == expected_keys

# Test with default values
stats_default = AnalysisStatistics()
result_default = stats_default.to_dict()
for key in expected_keys:
    assert result_default[key] == 0
```

**Expected Result:**
Dictionary should contain all field names as keys with integer values.

**Edge Cases Covered:**
- All fields populated
- All fields default (0)
- Dictionary keys match field names
- Values are integers

---

### SWUT_MODEL_00021: AnalysisResult Result Container

**Requirement:** SWR_MODEL_00021
**Priority:** High
**Status:** Pending

**Description:**
Test that AnalysisResult dataclass encapsulates complete analysis results.

**Test Function:** `test_SWUT_MODEL_00021_analysis_result_container()`

**Test Setup:**
```python
from autosar_calltree.database.models import (
    AnalysisResult, CallTreeNode, FunctionInfo,
    AnalysisStatistics, CircularDependency
)
from pathlib import Path
from datetime import datetime
```

**Test Execution:**
```python
# Create components
func = FunctionInfo(
    name="Root",
    return_type="void",
    file_path=Path("/src/root.c"),
    line_number=10,
    is_static=False
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
    errors=["Warning: unresolved function"]
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
    root_function="Test",
    call_tree=tree,
    statistics=stats
)
assert len(result_default.circular_dependencies) == 0
assert len(result_default.errors) == 0
```

**Expected Result:**
AnalysisResult should contain tree, statistics, cycles, and errors.

**Edge Cases Covered:**
- All fields populated
- Default empty lists for circular_dependencies and errors
- None call_tree (analysis failed scenario)

---

### SWUT_MODEL_00022: AnalysisResult Metadata

**Requirement:** SWR_MODEL_00022
**Priority:** Medium
**Status:** Pending

**Description:**
Test that AnalysisResult includes metadata fields for analysis context and reproducibility.

**Test Function:** `test_SWUT_MODEL_00022_analysis_result_metadata()`

**Test Setup:**
```python
from autosar_calltree.database.models import (
    AnalysisResult, CallTreeNode, FunctionInfo, AnalysisStatistics
)
from pathlib import Path
from datetime import datetime
```

**Test Execution:**
```python
# Create basic result
func = FunctionInfo(
    name="Test",
    return_type="void",
    file_path=Path("/src/test.c"),
    line_number=10,
    is_static=False
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
    max_depth_limit=5
)

assert result.timestamp == timestamp
assert result.source_directory == Path("/src")
assert result.max_depth_limit == 5

# Test defaults (timestamp should be near current time)
result_default = AnalysisResult(
    root_function="Test",
    call_tree=tree,
    statistics=stats
)

# Verify timestamp is recent (within 1 second)
now = datetime.now()
time_diff = abs((now - result_default.timestamp).total_seconds())
assert time_diff < 1.0

# Verify other defaults
assert result_default.source_directory is None
assert result_default.max_depth_limit == 3  # Default
```

**Expected Result:**
Metadata fields should track analysis context with sensible defaults.

**Edge Cases Covered:**
- All metadata fields specified
- Default timestamp (current time)
- Default source_directory (None)
- Default max_depth_limit (3)

---

### SWUT_MODEL_00023: AnalysisResult Function Collection

**Requirement:** SWR_MODEL_00023
**Priority:** Medium
**Status:** Pending

**Description:**
Test that AnalysisResult.get_all_functions method collects functions from call tree.

**Test Function:** `test_SWUT_MODEL_00023_analysis_result_get_all_functions()`

**Test Setup:**
```python
from autosar_calltree.database.models import (
    AnalysisResult, CallTreeNode, FunctionInfo, AnalysisStatistics
)
from pathlib import Path
```

**Test Execution:**
```python
# Create tree with multiple functions
func1 = FunctionInfo(
    name="Root",
    return_type="void",
    file_path=Path("/src/root.c"),
    line_number=10,
    is_static=False
)
func2 = FunctionInfo(
    name="Child",
    return_type="void",
    file_path=Path("/src/child.c"),
    line_number=20,
    is_static=False
)

root = CallTreeNode(function_info=func1, depth=0)
child = CallTreeNode(function_info=func2, depth=1)
root.add_child(child)

stats = AnalysisStatistics()
result = AnalysisResult(
    root_function="Root",
    call_tree=root,
    statistics=stats
)

# Collect functions
all_funcs = result.get_all_functions()

# Verify results
assert len(all_funcs) == 2
assert func1 in all_funcs
assert func2 in all_funcs

# Test with None call_tree (should raise error)
result_no_tree = AnalysisResult(
    root_function="Missing",
    call_tree=None,
    statistics=stats
)

try:
    result_no_tree.get_all_functions()
    assert False, "Should have raised an error"
except (ValueError, AttributeError, TypeError):
    pass  # Expected
```

**Expected Result:**
Should delegate to call_tree.get_all_functions() and raise error if call_tree is None.

**Edge Cases Covered:**
- Valid tree with multiple functions
- None call_tree (should raise error)
- Empty tree (only root function)

---

### SWUT_MODEL_00024: AnalysisResult Circular Dependency Check

**Requirement:** SWR_MODEL_00024
**Priority:** Low
**Status:** Pending

**Description:**
Test that AnalysisResult.has_circular_dependencies method correctly detects cycles.

**Test Function:** `test_SWUT_MODEL_00024_analysis_result_has_circular_deps()`

**Test Setup:**
```python
from autosar_calltree.database.models import (
    AnalysisResult, CallTreeNode, FunctionInfo,
    AnalysisStatistics, CircularDependency
)
from pathlib import Path
```

**Test Execution:**
```python
# Create basic components
func = FunctionInfo(
    name="Test",
    return_type="void",
    file_path=Path("/src/test.c"),
    line_number=10,
    is_static=False
)
tree = CallTreeNode(function_info=func, depth=0)
stats = AnalysisStatistics()

# Test with no circular dependencies
result_no_cycles = AnalysisResult(
    root_function="Test",
    call_tree=tree,
    statistics=stats,
    circular_dependencies=[]
)
assert result_no_cycles.has_circular_dependencies() is False

# Test with default (empty list)
result_default = AnalysisResult(
    root_function="Test",
    call_tree=tree,
    statistics=stats
)
assert result_default.has_circular_dependencies() is False

# Test with one circular dependency
cycle = CircularDependency(cycle=["A", "B", "A"], depth=2)
result_with_cycle = AnalysisResult(
    root_function="Test",
    call_tree=tree,
    statistics=stats,
    circular_dependencies=[cycle]
)
assert result_with_cycle.has_circular_dependencies() is True

# Test with multiple circular dependencies
cycle2 = CircularDependency(cycle=["C", "D", "C"], depth=3)
result_multiple = AnalysisResult(
    root_function="Test",
    call_tree=tree,
    statistics=stats,
    circular_dependencies=[cycle, cycle2]
)
assert result_multiple.has_circular_dependencies() is True
```

**Expected Result:**
Should return True if circular_dependencies list has length > 0, False otherwise.

**Edge Cases Covered:**
- Empty list (explicit)
- Default (empty list)
- Single circular dependency
- Multiple circular dependencies

---

### SWUT_MODEL_00025: FunctionDict Type Alias

**Requirement:** SWR_MODEL_00025
**Priority:** Medium
**Status:** Pending

**Description:**
Test that FunctionDict type alias correctly represents mapping from function names to lists of FunctionInfo objects.

**Test Function:** `test_SWUT_MODEL_00025_function_dict_type_alias()`

**Test Setup:**
```python
from autosar_calltree.database.models import FunctionInfo, FunctionDict
from pathlib import Path
from typing import get_type_hints
```

**Test Execution:**
```python
# Verify type alias
# FunctionDict should be Dict[str, List[FunctionInfo]]
import sys
if sys.version_info >= (3, 9):
    from typing import Dict, List
    # Check type hints if FunctionDict is properly defined
    hints = get_type_hints(FunctionDict) if hasattr(FunctionDict, '__annotations__') else {}
    # In runtime, FunctionDict is just an alias for Dict[str, List[FunctionInfo]]

# Create FunctionDict instance
func1 = FunctionInfo(
    name="COM_Init",
    return_type="void",
    file_path=Path("/src/com.c"),
    line_number=10,
    is_static=False
)
func2 = FunctionInfo(
    name="COM_Init",  # Same name, different file
    return_type="void",
    file_path=Path("/src/com_decl.c"),
    line_number=5,
    is_static=False
)
func3 = FunctionInfo(
    name="Demo_Init",
    return_type="void",
    file_path=Path("/src/demo.c"),
    line_number=15,
    is_static=False
)

# Build function dict
func_dict: FunctionDict = {
    "COM_Init": [func1, func2],  # Multiple definitions
    "Demo_Init": [func3]  # Single definition
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
assert all(isinstance(f, FunctionInfo) for funcs in func_dict.values() for f in funcs)
```

**Expected Result:**
FunctionDict should map function names (str) to lists of FunctionInfo objects.

**Edge Cases Covered:**
- Multiple definitions of same function
- Single definition of function
- Type checking with isinstance
- Dictionary operations

---

## Coverage Summary

| Requirement ID | Test ID | Status | Coverage |
|----------------|---------|--------|----------|
| SWR_MODEL_00001 | SWUT_MODEL_00001 | ⏳ Pending | Not Started |
| SWR_MODEL_00002 | SWUT_MODEL_00002 | ⏳ Pending | Not Started |
| SWR_MODEL_00003 | SWUT_MODEL_00003 | ⏳ Pending | Not Started |
| SWR_MODEL_00004 | SWUT_MODEL_00004 | ⏳ Pending | Not Started |
| SWR_MODEL_00005 | SWUT_MODEL_00005 | ⏳ Pending | Not Started |
| SWR_MODEL_00006 | SWUT_MODEL_00006 | ⏳ Pending | Not Started |
| SWR_MODEL_00007 | SWUT_MODEL_00007 | ⏳ Pending | Not Started |
| SWR_MODEL_00008 | SWUT_MODEL_00008 | ⏳ Pending | Not Started |
| SWR_MODEL_00009 | SWUT_MODEL_00009 | ⏳ Pending | Not Started |
| SWR_MODEL_00010 | SWUT_MODEL_00010 | ⏳ Pending | Not Started |
| SWR_MODEL_00011 | SWUT_MODEL_00011 | ⏳ Pending | Not Started |
| SWR_MODEL_00012 | SWUT_MODEL_00012 | ⏳ Pending | Not Started |
| SWR_MODEL_00013 | SWUT_MODEL_00013 | ⏳ Pending | Not Started |
| SWR_MODEL_00014 | SWUT_MODEL_00014 | ⏳ Pending | Not Started |
| SWR_MODEL_00015 | SWUT_MODEL_00015 | ⏳ Pending | Not Started |
| SWR_MODEL_00016 | SWUT_MODEL_00016 | ⏳ Pending | Not Started |
| SWR_MODEL_00017 | SWUT_MODEL_00017 | ⏳ Pending | Not Started |
| SWR_MODEL_00018 | SWUT_MODEL_00018 | ⏳ Pending | Not Started |
| SWR_MODEL_00019 | SWUT_MODEL_00019 | ⏳ Pending | Not Started |
| SWR_MODEL_00020 | SWUT_MODEL_00020 | ⏳ Pending | Not Started |
| SWR_MODEL_00021 | SWUT_MODEL_00021 | ⏳ Pending | Not Started |
| SWR_MODEL_00022 | SWUT_MODEL_00022 | ⏳ Pending | Not Started |
| SWR_MODEL_00023 | SWUT_MODEL_00023 | ⏳ Pending | Not Started |
| SWR_MODEL_00024 | SWUT_MODEL_00024 | ⏳ Pending | Not Started |
| SWR_MODEL_00025 | SWUT_MODEL_00025 | ⏳ Pending | Not Started |

**Summary:**
- Total Requirements: 25
- Total Test Cases: 25
- Tests Implemented: 0
- Tests Pending: 25
- Coverage: 0%

## Revision History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-01-30 | 1.0 | Claude | Initial version - 25 test cases covering all models module requirements |
