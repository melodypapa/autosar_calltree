# Mermaid Generator Test Cases

## Overview
This document describes the test cases for the Mermaid Generator module (mermaid_generator.py).

## Requirements Summary

| ID | Title | Priority |
|----|-------|----------|
| SWR_GENERATOR_00001 | Generator Initialization | High |
| SWR_GENERATOR_00002 | Mermaid Sequence Diagram Generation | High |
| SWR_GENERATOR_00003 | Participant Collection | High |
| SWR_GENERATOR_00004 | Module-Based Participants | High |
| SWR_GENERATOR_00005 | Function-Based Participants | High |
| SWR_GENERATOR_00006 | RTE Abbreviation | Medium |
| SWR_GENERATOR_00007 | Sequence Call Generation | High |
| SWR_GENERATOR_00008 | Parameter Display on Arrows | High |
| SWR_GENERATOR_00009 | Recursive Call Handling | Medium |
| SWR_GENERATOR_00010 | Return Statement Generation | Low |
| SWR_GENERATOR_00011 | Function Table Generation | High |
| SWR_GENERATOR_00012 | Module Column in Table | High |
| SWR_GENERATOR_00013 | Parameter Formatting | Medium |
| SWR_GENERATOR_00014 | Text Tree Generation | Medium |
| SWR_GENERATOR_00015 | Circular Dependencies Section | Medium |
| SWR_GENERATOR_00016 | Metadata Generation | High |
| SWR_GENERATOR_00017 | File Output | High |
| SWR_GENERATOR_00018 | String Output Generation | Medium |
| SWR_GENERATOR_00019 | Empty Call Tree Handling | High |
| SWR_GENERATOR_00020 | Fallback for Unmapped Modules | Medium |

## Test Cases

### SWUT_GENERATOR_00001: Generator Initialization

**Requirement:** SWR_GENERATOR_00001
**Priority:** High
**Status:** Implemented

**Description:**
Verify that MermaidGenerator can be initialized with various options.

**Test Function:** `test_SWUT_GENERATOR_00001_initialization()`

**Test Setup:**
```python
# Default initialization
gen1 = MermaidGenerator()
# Custom options
gen2 = MermaidGenerator(abbreviate_rte=False, use_module_names=True, include_returns=True)
```

**Test Execution:**
```python
assert gen1.abbreviate_rte == True
assert gen1.use_module_names == False
assert gen1.include_returns == False

assert gen2.abbreviate_rte == False
assert gen2.use_module_names == True
assert gen2.include_returns == True
assert gen2.participant_map == {}
assert gen2.next_participant_id == 1
```

**Expected Result:**
Generator initializes with correct options.

---

### SWUT_GENERATOR_00002: Mermaid Sequence Diagram Header

**Requirement:** SWR_GENERATOR_00002
**Priority:** High
**Status:** Implemented

**Description:**
Verify that generated Mermaid diagram starts with correct header.

**Test Function:** `test_SWUT_GENERATOR_00002_mermaid_header()`

**Test Setup:**
```python
result = create_mock_analysis_result()
gen = MermaidGenerator()
```

**Test Execution:**
```python
diagram = gen._generate_mermaid_diagram(result.call_tree)
lines = diagram.split("\n")
assert lines[0] == "sequenceDiagram"
```

**Expected Result:**
Diagram starts with "sequenceDiagram" keyword.

---

### SWUT_GENERATOR_00003: Participant Collection - Function Names

**Requirement:** SWR_GENERATOR_00003, SWR_GENERATOR_00005
**Priority:** High
**Status:** Implemented

**Description:**
Verify that participants are collected as function names when use_module_names=False.

**Test Function:** `test_SWUT_GENERATOR_00003_collect_participants_functions()`

**Test Setup:**
```python
root = create_mock_call_tree([
    ("Demo_Init", "demo.c", None),
    ("HW_Init", "hw.c", None),
    ("SW_Init", "sw.c", None),
])
gen = MermaidGenerator(use_module_names=False)
```

**Test Execution:**
```python
participants = gen._collect_participants(root)
assert "Demo_Init" in participants
assert "HW_Init" in participants
assert "SW_Init" in participants
assert len(participants) == 3
```

**Expected Result:**
All unique function names collected as participants.

---

### SWUT_GENERATOR_00004: Participant Collection - Module Names

**Requirement:** SWR_GENERATOR_00003, SWR_GENERATOR_00004
**Priority:** High
**Status:** Implemented

**Description:**
Verify that participants are collected as module names when use_module_names=True.

**Test Function:** `test_SWUT_GENERATOR_00004_collect_participants_modules()`

**Test Setup:**
```python
root = create_mock_call_tree([
    ("Demo_Init", "demo.c", "DemoModule"),
    ("HW_Init", "hw.c", "HardwareModule"),
    ("SW_Init", "sw.c", "SoftwareModule"),
])
gen = MermaidGenerator(use_module_names=True)
```

**Test Execution:**
```python
participants = gen._collect_participants(root)
assert "DemoModule" in participants
assert "HardwareModule" in participants
assert "SoftwareModule" in participants
assert len(participants) == 3
```

**Expected Result:**
Module names used as participants.

---

### SWUT_GENERATOR_00005: Module Fallback to Filename

**Requirement:** SWR_GENERATOR_00004, SWR_GENERATOR_00020
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that functions without module assignment use filename as participant.

**Test Function:** `test_SWUT_GENERATOR_00005_module_fallback_to_filename()`

**Test Setup:**
```python
root = create_mock_call_tree([
    ("Demo_Init", "demo.c", "DemoModule"),
    ("Unmapped_Init", "unmapped.c", None),  # No module
])
gen = MermaidGenerator(use_module_names=True)
```

**Test Execution:**
```python
participants = gen._collect_participants(root)
assert "DemoModule" in participants
assert "unmapped" in participants  # Filename without extension
assert len(participants) == 2
```

**Expected Result:**
Filename used when module is None.

---

### SWUT_GENERATOR_00006: RTE Function Abbreviation

**Requirement:** SWR_GENERATOR_00006
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that long RTE function names are abbreviated.

**Test Function:** `test_SWUT_GENERATOR_00006_rte_abbreviation()`

**Test Setup:**
```python
gen = MermaidGenerator(abbreviate_rte=True)
```

**Test Execution:**
```python
abbrev = gen._abbreviate_rte_name("Rte_Read_P_Voltage_Value")
assert abbrev == "Rte_Read_PVV"

abbrev2 = gen._abbreviate_rte_name("Rte_Write_SW_Data_State")
assert abbrev2 == "Rte_Write_SDS"
```

**Expected Result:**
Long RTE names abbreviated to Rte_Operation_XXX format.

---

### SWUT_GENERATOR_00007: RTE Abbreviation Disabled

**Requirement:** SWR_GENERATOR_00006
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that RTE abbreviation can be disabled.

**Test Function:** `test_SWUT_GENERATOR_00007_rte_abbreviation_disabled()`

**Test Setup:**
```python
gen = MermaidGenerator(abbreviate_rte=False)
```

**Test Execution:**
```python
abbrev = gen._get_participant_name("Rte_Read_P_Voltage_Value")
assert abbrev == "Rte_Read_P_Voltage_Value"
```

**Expected Result:**
Full RTE name used when abbreviate_rte=False.

---

### SWUT_GENERATOR_00008: Short RTE Name Not Abbreviated

**Requirement:** SWR_GENERATOR_00006
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that short RTE names are not abbreviated.

**Test Function:** `test_SWUT_GENERATOR_00008_short_rte_not_abbreviated()`

**Test Setup:**
```python
gen = MermaidGenerator(abbreviate_rte=True)
```

**Test Execution:**
```python
abbrev = gen._abbreviate_rte_name("Rte_Call")
assert abbrev == "Rte_Call"  # Too short to abbreviate
```

**Expected Result:**
Short RTE names left unchanged.

---

### SWUT_GENERATOR_00009: Sequence Call Generation - Function Mode

**Requirement:** SWR_GENERATOR_00007
**Priority:** High
**Status:** Implemented

**Description:**
Verify that sequence calls are generated correctly with function participants.

**Test Function:** `test_SWUT_GENERATOR_00009_sequence_calls_function_mode()`

**Test Setup:**
```python
root = create_mock_call_tree([
    ("Demo_Init", "demo.c", None, [("HW_Init", "hw.c", None)]),
])
gen = MermaidGenerator(use_module_names=False)
lines = []
```

**Test Execution:**
```python
gen._generate_sequence_calls(root, lines)
output = "\n".join(lines)
assert "Demo_Init->>HW_Init: call" in output
```

**Expected Result:**
Arrows show "call" label between function participants.

---

### SWUT_GENERATOR_00010: Sequence Call Generation - Module Mode

**Requirement:** SWR_GENERATOR_00004, SWR_GENERATOR_00007
**Priority:** High
**Status:** Implemented

**Description:**
Verify that sequence calls show function names on arrows in module mode.

**Test Function:** `test_SWUT_GENERATOR_00010_sequence_calls_module_mode()`

**Test Setup:**
```python
root = create_mock_call_tree([
    ("Demo_Init", "demo.c", "DemoModule", [("HW_Init", "hw.c", "HardwareModule")]),
])
gen = MermaidGenerator(use_module_names=True)
lines = []
```

**Test Execution:**
```python
gen._generate_sequence_calls(root, lines)
output = "\n".join(lines)
assert "DemoModule->>HardwareModule: HW_Init" in output
```

**Expected Result:**
Arrows show function name between module participants.

---

### SWUT_GENERATOR_00011: Parameter Display on Arrows

**Requirement:** SWR_GENERATOR_00008
**Priority:** High
**Status:** Implemented

**Description:**
Verify that function parameters are displayed on sequence arrows.

**Test Function:** `test_SWUT_GENERATOR_00011_parameters_on_arrows()`

**Test Setup:**
```python
# Create function with parameters
params = [Parameter("timerId", "uint32", False, False)]
root = create_mock_call_tree_with_params([
    ("Demo_Init", "demo.c", "DemoModule", params, []),
])
gen = MermaidGenerator(use_module_names=True)
lines = []
```

**Test Execution:**
```python
gen._generate_sequence_calls(root, lines)
output = "\n".join(lines)
assert "Demo_Init(timerId)" in output
```

**Expected Result:**
Function names include parameters in parentheses.

---

### SWUT_GENERATOR_00012: Multiple Parameters Display

**Requirement:** SWR_GENERATOR_00008
**Priority:** High
**Status:** Implemented

**Description:**
Verify that multiple parameters are comma-separated.

**Test Function:** `test_SWUT_GENERATOR_00012_multiple_parameters()`

**Test Setup:**
```python
params = [
    Parameter("value", "uint32", False, False),
    Parameter("status", "uint8*", False, False),
]
root = create_mock_call_tree_with_params([("Func", "f.c", "Mod", params, [])])
gen = MermaidGenerator(use_module_names=True)
lines = []
```

**Test Execution:**
```python
gen._generate_sequence_calls(root, lines)
output = "\n".join(lines)
assert "Func(value, status)" in output
```

**Expected Result:**
Parameters separated by commas.

---

### SWUT_GENERATOR_00013: Recursive Call Handling

**Requirement:** SWR_GENERATOR_00009
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that recursive calls use special arrow syntax.

**Test Function:** `test_SWUT_GENERATOR_00013_recursive_call_handling()`

**Test Setup:**
```python
root = create_mock_call_tree([
    ("Demo_Init", "demo.c", "DemoModule", [("HW_Init", "hw.c", "HardwareModule")]),
])
# Mark child as recursive
root.children[0].is_recursive = True
gen = MermaidGenerator(use_module_names=True)
lines = []
```

**Test Execution:**
```python
gen._generate_sequence_calls(root, lines)
output = "\n".join(lines)
# Check for recursive arrow style (dashed with X)
assert "DemoModule->>HardwareModule: HW_Init" in output
```

**Expected Result:**
Recursive calls marked appropriately.

---

### SWUT_GENERATOR_00014: Return Statement Generation

**Requirement:** SWR_GENERATOR_00010
**Priority:** Low
**Status:** Implemented

**Description:**
Verify that return statements are generated when include_returns=True.

**Test Function:** `test_SWUT_GENERATOR_00014_return_statements()`

**Test Setup:**
```python
root = create_mock_call_tree([
    ("Demo_Init", "demo.c", "DemoModule", [("HW_Init", "hw.c", "HardwareModule")]),
])
gen = MermaidGenerator(use_module_names=True, include_returns=True)
lines = []
```

**Test Execution:**
```python
gen._generate_sequence_calls(root, lines)
output = "\n".join(lines)
assert "HardwareModule-->>DemoModule: return" in output
```

**Expected Result:**
Return arrows generated when enabled.

---

### SWUT_GENERATOR_00015: Return Statements Disabled by Default

**Requirement:** SWR_GENERATOR_00010
**Priority:** Low
**Status:** Implemented

**Description:**
Verify that return statements are not generated by default.

**Test Function:** `test_SWUT_GENERATOR_00015_returns_disabled_default()`

**Test Setup:**
```python
root = create_mock_call_tree([
    ("Demo_Init", "demo.c", "DemoModule", [("HW_Init", "hw.c", "HardwareModule")]),
])
gen = MermaidGenerator(use_module_names=True)  # include_returns defaults to False
lines = []
```

**Test Execution:**
```python
gen._generate_sequence_calls(root, lines)
output = "\n".join(lines)
assert "return" not in output.lower()
```

**Expected Result:**
No return arrows when disabled.

---

### SWUT_GENERATOR_00016: Function Table - Function Mode

**Requirement:** SWR_GENERATOR_00011
**Priority:** High
**Status:** Implemented

**Description:**
Verify that function table has correct format when use_module_names=False.

**Test Function:** `test_SWUT_GENERATOR_00016_function_table_format()`

**Test Setup:**
```python
root = create_mock_call_tree([("Demo_Init", "demo.c", None)])
gen = MermaidGenerator(use_module_names=False)
```

**Test Execution:**
```python
table = gen._generate_function_table(root)
lines = table.split("\n")
# Check header doesn't include Module column
assert "| Function | File | Line |" in lines[1]
assert "| Module |" not in table
```

**Expected Result:**
Table format without Module column.

---

### SWUT_GENERATOR_00017: Function Table - Module Mode

**Requirement:** SWR_GENERATOR_00011, SWR_GENERATOR_00012
**Priority:** High
**Status:** Implemented

**Description:**
Verify that function table includes Module column when use_module_names=True.

**Test Function:** `test_SWUT_GENERATOR_00017_function_table_module_column()`

**Test Setup:**
```python
root = create_mock_call_tree([
    ("Demo_Init", "demo.c", "DemoModule"),
    ("HW_Init", "hw.c", "HardwareModule"),
])
gen = MermaidGenerator(use_module_names=True)
```

**Test Execution:**
```python
table = gen._generate_function_table(root)
lines = table.split("\n")
# Check header includes Module column
assert "| Function | Module | File | Line |" in lines[1]
assert "| Demo_Init | DemoModule |" in table
assert "| HW_Init | HardwareModule |" in table
```

**Expected Result:**
Table includes Module column with values.

---

### SWUT_GENERATOR_00018: Function Table - N/A for Unmapped

**Requirement:** SWR_GENERATOR_00012
**Priority:** High
**Status:** Implemented

**Description:**
Verify that unmapped functions show "N/A" in Module column.

**Test Function:** `test_SWUT_GENERATOR_00018_function_table_na_for_unmapped()`

**Test Setup:**
```python
root = create_mock_call_tree([
    ("Demo_Init", "demo.c", "DemoModule"),
    ("Unmapped", "unmapped.c", None),  # No module
])
gen = MermaidGenerator(use_module_names=True)
```

**Test Execution:**
```python
table = gen._generate_function_table(root)
assert "| Unmapped | N/A |" in table
```

**Expected Result:**
Unmapped functions show "N/A".

---

### SWUT_GENERATOR_00019: Parameter Formatting for Table

**Requirement:** SWR_GENERATOR_00013
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that parameters are formatted correctly for function table.

**Test Function:** `test_SWUT_GENERATOR_00019_parameter_formatting_table()`

**Test Setup:**
```python
params = [
    Parameter("value", "uint32", False, False),
    Parameter("ptr", "uint8*", True, False),
]
func = create_mock_function("Func", "file.c", params)
gen = MermaidGenerator()
```

**Test Execution:**
```python
formatted = gen._format_parameters(func)
assert "`uint32 value`" in formatted
assert "`uint8* ptr`" in formatted
```

**Expected Result:**
Parameters formatted as `type name` with pointer indicator.

---

### SWUT_GENERATOR_00020: Void Parameter Display

**Requirement:** SWR_GENERATOR_00013
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that functions with no parameters show "void".

**Test Function:** `test_SWUT_GENERATOR_00020_void_parameters()`

**Test Setup:**
```python
func = create_mock_function("Func", "file.c", [])
gen = MermaidGenerator()
```

**Test Execution:**
```python
formatted = gen._format_parameters(func)
assert formatted == "`void`"
```

**Expected Result:**
Empty parameter list shows "void".

---

### SWUT_GENERATOR_00021: Parameter Formatting for Diagram

**Requirement:** SWR_GENERATOR_00008, SWR_GENERATOR_00013
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that parameters are formatted for sequence diagram (names only).

**Test Function:** `test_SWUT_GENERATOR_00021_parameter_formatting_diagram()`

**Test Setup:**
```python
params = [
    Parameter("value", "uint32", False, False),
    Parameter("status", "uint8*", True, False),
]
func = create_mock_function("Func", "file.c", params)
gen = MermaidGenerator()
```

**Test Execution:**
```python
formatted = gen._format_parameters_for_diagram(func)
assert formatted == "value, status"
```

**Expected Result:**
Only parameter names, comma-separated.

---

### SWUT_GENERATOR_00022: Text Tree Generation

**Requirement:** SWR_GENERATOR_00014
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that text tree is generated with correct formatting.

**Test Function:** `test_SWUT_GENERATOR_00022_text_tree_generation()`

**Test Setup:**
```python
root = create_mock_call_tree([
    ("Demo_Init", "demo.c", "DemoModule", [
        ("HW_Init", "hw.c", "HardwareModule", []),
        ("SW_Init", "sw.c", "SoftwareModule", []),
    ]),
])
gen = MermaidGenerator()
```

**Test Execution:**
```python
tree = gen._generate_text_tree(root)
assert "Demo_Init (demo.c:1)" in tree
assert "└── HW_Init (hw.c:1)" in tree
assert "└── SW_Init (sw.c:1)" in tree
```

**Expected Result:**
Tree structure with correct connectors and file info.

---

### SWUT_GENERATOR_00023: Circular Dependencies Section

**Requirement:** SWR_GENERATOR_00015
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that circular dependencies are displayed in section.

**Test Function:** `test_SWUT_GENERATOR_00023_circular_dependencies_section()`

**Test Setup:**
```python
result = create_mock_analysis_result()
result.circular_dependencies = [
    CircularDependency(cycle=["FuncA", "FuncB", "FuncA"], depth=3),
]
gen = MermaidGenerator()
```

**Test Execution:**
```python
section = gen._generate_circular_deps_section(result)
assert "## Circular Dependencies" in section
assert "Found 1 circular dependencies" in section
assert "FuncA → FuncB → FuncA" in section
```

**Expected Result:**
Circular dependencies listed with cycle and depth.

---

### SWUT_GENERATOR_00024: Metadata Generation

**Requirement:** SWR_GENERATOR_00016
**Priority:** High
**Status:** Implemented

**Description:**
Verify that metadata section is generated correctly.

**Test Function:** `test_SWUT_GENERATOR_00024_metadata_generation()`

**Test Setup:**
```python
result = create_mock_analysis_result()
result.root_function = "Demo_Init"
result.statistics.total_functions = 10
result.statistics.unique_functions = 8
result.statistics.max_depth_reached = 3
result.statistics.circular_dependencies_found = 0
gen = MermaidGenerator()
```

**Test Execution:**
```python
metadata = gen._generate_metadata(result)
assert "## Metadata" in metadata
assert "**Root Function**: `Demo_Init`" in metadata
assert "**Total Functions**: 10" in metadata
assert "**Unique Functions**: 8" in metadata
assert "**Max Depth**: 3" in metadata
```

**Expected Result:**
Metadata includes all statistics fields.

---

### SWUT_GENERATOR_00025: File Output Generation

**Requirement:** SWR_GENERATOR_00017
**Priority:** High
**Status:** Implemented

**Description:**
Verify that generate() creates markdown file with all sections.

**Test Function:** `test_SWUT_GENERATOR_00025_file_output()`

**Test Setup:**
```python
result = create_mock_analysis_result()
gen = MermaidGenerator()
output_path = tmp_path / "output.md"
```

**Test Execution:**
```python
gen.generate(result, str(output_path))
assert output_path.exists()
content = output_path.read_text()
assert "# Call Tree:" in content
assert "## Metadata" in content
assert "## Sequence Diagram" in content
assert "```mermaid" in content
assert "## Function Details" in content
```

**Expected Result:**
File created with all sections.

---

### SWUT_GENERATOR_00026: String Output Generation

**Requirement:** SWR_GENERATOR_00018
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that generate_to_string returns complete markdown.

**Test Function:** `test_SWUT_GENERATOR_00026_string_output()`

**Test Setup:**
```python
result = create_mock_analysis_result()
gen = MermaidGenerator()
```

**Test Execution:**
```python
output = gen.generate_to_string(result)
assert "# Call Tree:" in output
assert "## Metadata" in output
assert "## Sequence Diagram" in output
assert "```mermaid" in output
```

**Expected Result:**
String contains all sections.

---

### SWUT_GENERATOR_00027: Empty Call Tree Error

**Requirement:** SWR_GENERATOR_00019
**Priority:** High
**Status:** Implemented

**Description:**
Verify that ValueError is raised for empty call tree.

**Test Function:** `test_SWUT_GENERATOR_00027_empty_call_tree_error()`

**Test Setup:**
```python
result = create_mock_analysis_result()
result.call_tree = None
gen = MermaidGenerator()
output_path = tmp_path / "output.md"
```

**Test Execution:**
```python
with pytest.raises(ValueError, match="call tree is None"):
    gen.generate(result, str(output_path))
```

**Expected Result:**
ValueError raised for None call tree.

---

### SWUT_GENERATOR_00028: Optional Content Sections

**Requirement:** SWR_GENERATOR_00017
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that optional sections can be disabled.

**Test Function:** `test_SWUT_GENERATOR_00028_optional_sections()`

**Test Setup:**
```python
result = create_mock_analysis_result()
gen = MermaidGenerator()
output_path = tmp_path / "output.md"
```

**Test Execution:**
```python
gen.generate(
    result,
    str(output_path),
    include_metadata=False,
    include_function_table=False,
    include_text_tree=False,
)
content = output_path.read_text()
assert "## Metadata" not in content
assert "## Function Details" not in content
assert "## Call Tree (Text)" not in content
assert "## Sequence Diagram" in content  # Always included
```

**Expected Result:**
Optional sections excluded when disabled.

---

### SWUT_GENERATOR_00029: Unique Functions in Table

**Requirement:** SWR_GENERATOR_00011
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that function table shows each function only once.

**Test Function:** `test_SWUT_GENERATOR_00029_unique_functions_in_table()`

**Test Setup:**
```python
# Create tree where same function appears multiple times
root = create_mock_call_tree([
    ("Demo_Init", "demo.c", "DemoModule", [
        ("HW_Init", "hw.c", "HardwareModule", []),
        ("SW_Init", "sw.c", "SoftwareModule", [("HW_Init", "hw.c", "HardwareModule", [])]),
    ]),
])
gen = MermaidGenerator()
```

**Test Execution:**
```python
table = gen._generate_function_table(root)
lines = [l for l in table.split("\n") if "HW_Init" in l]
# HW_Init should appear only once despite being called twice
assert len(lines) == 1
```

**Expected Result:**
Each function appears only once in table.

---

### SWUT_GENERATOR_00030: Sorted Function Table

**Requirement:** SWR_GENERATOR_00011
**Priority:** Low
**Status:** Implemented

**Description:**
Verify that function table is sorted alphabetically.

**Test Function:** `test_SWUT_GENERATOR_00030_sorted_function_table()`

**Test Setup:**
```python
root = create_mock_call_tree([
    ("Z_Function", "z.c", None),
    ("A_Function", "a.c", None),
    ("M_Function", "m.c", None),
])
gen = MermaidGenerator()
```

**Test Execution:**
```python
table = gen._generate_function_table(root)
lines = [l for l in table.split("\n") if "| `" in l]
# Extract function names from table
func_names = [l.split("|")[1].strip().strip("`") for l in lines if "| `" in l]
assert func_names == sorted(func_names)
```

**Expected Result:**
Functions sorted alphabetically.

---

### SWUT_GENERATOR_00031: Parent Directory Creation

**Requirement:** SWR_GENERATOR_00017
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that output creates parent directories if needed.

**Test Function:** `test_SWUT_GENERATOR_00031_parent_directory_creation()`

**Test Setup:**
```python
result = create_mock_analysis_result()
gen = MermaidGenerator()
output_path = tmp_path / "subdir1" / "subdir2" / "output.md"
```

**Test Execution:**
```python
gen.generate(result, str(output_path))
assert output_path.exists()
assert output_path.parent.is_dir()
```

**Expected Result:**
Parent directories created automatically.

---

## Coverage Summary

| Requirement ID | Test ID | Status | Coverage |
|----------------|---------|--------|----------|
| SWR_GENERATOR_00001 | SWUT_GENERATOR_00001 | ✅ Pass | Full |
| SWR_GENERATOR_00002 | SWUT_GENERATOR_00002 | ✅ Pass | Full |
| SWR_GENERATOR_00003 | SWUT_GENERATOR_00003-00005 | ✅ Pass | Full |
| SWR_GENERATOR_00004 | SWUT_GENERATOR_00004-00005, 00010, 00017-00018 | ✅ Pass | Full |
| SWR_GENERATOR_00005 | SWUT_GENERATOR_00003, 00009 | ✅ Pass | Full |
| SWR_GENERATOR_00006 | SWUT_GENERATOR_00006-00008 | ✅ Pass | Full |
| SWR_GENERATOR_00007 | SWUT_GENERATOR_00009-00010 | ✅ Pass | Full |
| SWR_GENERATOR_00008 | SWUT_GENERATOR_00011-00012, 00021 | ✅ Pass | Full |
| SWR_GENERATOR_00009 | SWUT_GENERATOR_00013 | ✅ Pass | Full |
| SWR_GENERATOR_00010 | SWUT_GENERATOR_00014-00015 | ✅ Pass | Full |
| SWR_GENERATOR_00011 | SWUT_GENERATOR_00016-00018, 00029-00030 | ✅ Pass | Full |
| SWR_GENERATOR_00012 | SWUT_GENERATOR_00017-00018 | ✅ Pass | Full |
| SWR_GENERATOR_00013 | SWUT_GENERATOR_00019-00021 | ✅ Pass | Full |
| SWR_GENERATOR_00014 | SWUT_GENERATOR_00022 | ✅ Pass | Full |
| SWR_GENERATOR_00015 | SWUT_GENERATOR_00023 | ✅ Pass | Full |
| SWR_GENERATOR_00016 | SWUT_GENERATOR_00024 | ✅ Pass | Full |
| SWR_GENERATOR_00017 | SWUT_GENERATOR_00025, 00028, 00031 | ✅ Pass | Full |
| SWR_GENERATOR_00018 | SWUT_GENERATOR_00026 | ✅ Pass | Full |
| SWR_GENERATOR_00019 | SWUT_GENERATOR_00027 | ✅ Pass | Full |
| SWR_GENERATOR_00020 | SWUT_GENERATOR_00005, 00018 | ✅ Pass | Full |

**Total Tests:** 31
**Requirements:** 20
**Coverage Target:** ≥90%

## Requirements Traceability Matrix

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_GENERATOR_00001 | SWUT_GENERATOR_00001 | test_SWUT_GENERATOR_00001_initialization | ✅ Pass |
| SWR_GENERATOR_00002 | SWUT_GENERATOR_00002 | test_SWUT_GENERATOR_00002_mermaid_header | ✅ Pass |
| SWR_GENERATOR_00003 | SWUT_GENERATOR_00003 | test_SWUT_GENERATOR_00003_collect_participants_functions | ✅ Pass |
| SWR_GENERATOR_00004 | SWUT_GENERATOR_00004 | test_SWUT_GENERATOR_00004_collect_participants_modules | ✅ Pass |
| SWR_GENERATOR_00005 | SWUT_GENERATOR_00005 | test_SWUT_GENERATOR_00005_module_fallback_to_filename | ✅ Pass |
| SWR_GENERATOR_00006 | SWUT_GENERATOR_00006 | test_SWUT_GENERATOR_00006_rte_abbreviation | ✅ Pass |
| SWR_GENERATOR_00006 | SWUT_GENERATOR_00007 | test_SWUT_GENERATOR_00007_rte_abbreviation_disabled | ✅ Pass |
| SWR_GENERATOR_00006 | SWUT_GENERATOR_00008 | test_SWUT_GENERATOR_00008_short_rte_not_abbreviated | ✅ Pass |
| SWR_GENERATOR_00007 | SWUT_GENERATOR_00009 | test_SWUT_GENERATOR_00009_sequence_calls_function_mode | ✅ Pass |
| SWR_GENERATOR_00004 | SWUT_GENERATOR_00010 | test_SWUT_GENERATOR_00010_sequence_calls_module_mode | ✅ Pass |
| SWR_GENERATOR_00008 | SWUT_GENERATOR_00011 | test_SWUT_GENERATOR_00011_parameters_on_arrows | ✅ Pass |
| SWR_GENERATOR_00008 | SWUT_GENERATOR_00012 | test_SWUT_GENERATOR_00012_multiple_parameters | ✅ Pass |
| SWR_GENERATOR_00009 | SWUT_GENERATOR_00013 | test_SWUT_GENERATOR_00013_recursive_call_handling | ✅ Pass |
| SWR_GENERATOR_00010 | SWUT_GENERATOR_00014 | test_SWUT_GENERATOR_00014_return_statements | ✅ Pass |
| SWR_GENERATOR_00010 | SWUT_GENERATOR_00015 | test_SWUT_GENERATOR_00015_returns_disabled_default | ✅ Pass |
| SWR_GENERATOR_00011 | SWUT_GENERATOR_00016 | test_SWUT_GENERATOR_00016_function_table_format | ✅ Pass |
| SWR_GENERATOR_00012 | SWUT_GENERATOR_00017 | test_SWUT_GENERATOR_00017_function_table_module_column | ✅ Pass |
| SWR_GENERATOR_00012 | SWUT_GENERATOR_00018 | test_SWUT_GENERATOR_00018_function_table_na_for_unmapped | ✅ Pass |
| SWR_GENERATOR_00013 | SWUT_GENERATOR_00019 | test_SWUT_GENERATOR_00019_parameter_formatting_table | ✅ Pass |
| SWR_GENERATOR_00013 | SWUT_GENERATOR_00020 | test_SWUT_GENERATOR_00020_void_parameters | ✅ Pass |
| SWR_GENERATOR_00013 | SWUT_GENERATOR_00021 | test_SWUT_GENERATOR_00021_parameter_formatting_diagram | ✅ Pass |
| SWR_GENERATOR_00014 | SWUT_GENERATOR_00022 | test_SWUT_GENERATOR_00022_text_tree_generation | ✅ Pass |
| SWR_GENERATOR_00015 | SWUT_GENERATOR_00023 | test_SWUT_GENERATOR_00023_circular_dependencies_section | ✅ Pass |
| SWR_GENERATOR_00016 | SWUT_GENERATOR_00024 | test_SWUT_GENERATOR_00024_metadata_generation | ✅ Pass |
| SWR_GENERATOR_00017 | SWUT_GENERATOR_00025 | test_SWUT_GENERATOR_00025_file_output | ✅ Pass |
| SWR_GENERATOR_00018 | SWUT_GENERATOR_00026 | test_SWUT_GENERATOR_00026_string_output | ✅ Pass |
| SWR_GENERATOR_00019 | SWUT_GENERATOR_00027 | test_SWUT_GENERATOR_00027_empty_call_tree_error | ✅ Pass |
| SWR_GENERATOR_00017 | SWUT_GENERATOR_00028 | test_SWUT_GENERATOR_00028_optional_sections | ✅ Pass |
| SWR_GENERATOR_00011 | SWUT_GENERATOR_00029 | test_SWUT_GENERATOR_00029_unique_functions_in_table | ✅ Pass |
| SWR_GENERATOR_00011 | SWUT_GENERATOR_00030 | test_SWUT_GENERATOR_00030_sorted_function_table | ✅ Pass |
| SWR_GENERATOR_00017 | SWUT_GENERATOR_00031 | test_SWUT_GENERATOR_00031_parent_directory_creation | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00032 | test_SWUT_GENERATOR_00032_opt_block_generation | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00033 | test_SWUT_GENERATOR_00033_multiple_optional_calls | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00034 | test_SWUT_GENERATOR_00034_mixed_optional_and_regular | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00035 | test_SWUT_GENERATOR_00035_nested_optional | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00036 | test_SWUT_GENERATOR_00036_recursive_not_opt | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00037 | test_SWUT_GENERATOR_00037_optional_with_returns | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00038 | test_SWUT_GENERATOR_00038_optional_function_mode | ✅ Pass |
| SWR_MERMAID_00005 | SWUT_GENERATOR_00039 | test_SWUT_GENERATOR_00039_loop_block_generation | ✅ Pass |
| SWR_MERMAID_00005 | SWUT_GENERATOR_00040 | test_SWUT_GENERATOR_00040_multiple_loop_calls | ✅ Pass |
| SWR_MERMAID_00005 | SWUT_GENERATOR_00041 | test_SWUT_GENERATOR_00041_mixed_loop_and_optional | ✅ Pass |

## Running Tests

```bash
# Run all Mermaid generator tests
pytest tests/unit/test_mermaid_generator.py

# Run specific test case
pytest tests/unit/test_mermaid_generator.py::TestMermaidGenerator::test_SWUT_GENERATOR_00001_initialization

# Run with coverage
pytest tests/unit/test_mermaid_generator.py --cov=src/autosar_calltree/generators/mermaid_gen.py --cov-report=term-missing
```

## Change History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-02-10 | 1.1 | Claude | Added requirements traceability matrix, updated to align with new structure |
| 2026-01-30 | 1.0 | Claude | Initial test documentation |
