# Generators Package Test Cases

## Overview

This document describes test cases for the Generators package, organized by requirement structure.

**Requirements Document**: [requirements_generators.md](../requirements/requirements_generators.md)

**Package**: `autosar_calltree.generators`
**Source Files**: `mermaid_generator.py`, `xmi_generator.py`
**Requirement IDs**: SWR_GEN_00001 - SWR_GEN_00025
**Coverage**: 89%

---

## Mermaid Generator Tests

### SWUT_GEN_00001 - Mermaid Sequence Diagram Generation

**Requirement**: SWR_GEN_00001
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that Mermaid sequence diagrams are generated from call tree analysis results.

**Test Approach**
The test verifies that:
1. generate() method creates Mermaid markdown output
2. Output file is written correctly
3. Diagram contains valid Mermaid syntax
4. Analysis result is used correctly

**Expected Behavior**
MermaidGenerator produces complete markdown files with embedded Mermaid sequence diagrams.

**Edge Cases**
- Empty call trees
- Trees with only root node
- Large complex trees
- Trees with cycles

---

### SWUT_GEN_00002 - Participant Management

**Requirement**: SWR_GEN_00002
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that participants in sequence diagram are managed correctly.

**Test Approach**
The test verifies that:
1. Participants are collected in encounter order
2. Each participant gets unique ID
3. Participant map tracks all participants
4. Participants are declared in diagram header

**Expected Behavior**
Participants are tracked in order of first appearance and declared correctly in Mermaid.

**Edge Cases**
- Many participants (50+)
- Module name collisions
- Function name collisions
- Mixed function and module participants

---

### SWUT_GEN_00003 - Module-Based Participants

**Requirement**: SWR_GEN_00003
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that SW modules are used as participants when configured.

**Test Approach**
The test verifies that:
1. use_module_names=True enables module participants
2. Module names are extracted from function_info.sw_module
3. Module name appears as participant in diagram
4. Function names appear on arrows

**Expected Behavior**
Module-level diagrams show module interactions with function names on call arrows.

**Edge Cases**
- Functions without assigned modules
- Multiple functions in same module
- Module names with special characters

---

### SWUT_GEN_00004 - Function Names on Arrows

**Requirement**: SWR_GEN_00004
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that function names are displayed on call arrows with parameters.

**Test Approach**
The test verifies that:
1. Arrow format is `Source->Target: function_name(params)`
2. Parameter names are included (not types)
3. Empty parameters show no parentheses
4. Function name is readable

**Expected Behavior**
Call arrows show the complete function signature with parameters for clarity.

**Edge Cases**
- Functions with many parameters
- Functions with no parameters
- Long function names
- Complex parameter types

---

### SWUT_GEN_00005 - Parameter Display

**Requirement**: SWR_GEN_00005
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that function parameters are displayed on call arrows.

**Test Approach**
The test verifies that:
1. Parameter names are extracted correctly
2. Parameter types are not shown (names only)
3. Multiple parameters are comma-separated
4. Empty parameter lists handled gracefully

**Expected Behavior**
Parameters are shown as readable comma-separated names on diagram arrows.

**Edge Cases**
- Functions with 10+ parameters
- Functions with pointer parameters
- Functions with array parameters
- Functions with no parameters

---

### SWUT_GEN_00006 - Opt Block Generation

**Requirement**: SWR_GEN_00006
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that Mermaid opt blocks are generated for conditional calls.

**Test Approach**
The test verifies that:
1. is_conditional=True triggers opt block
2. Condition text appears in opt block label
3. Conditional calls are nested in opt block
4. End keyword closes opt block

**Expected Behavior**
Conditional function calls generate `opt condition ... end` blocks in Mermaid diagram.

**Edge Cases**
- Nested conditionals
- Multi-line condition text
- Special characters in conditions
- Empty condition text

---

### SWUT_GEN_00007 - Alt Block Generation

**Requirement**: SWR_GEN_00007
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that Mermaid alt blocks are generated for if/else chains.

**Test Approach**
The test verifies that:
1. Multiple conditions at same level generate alt block
2. Each condition gets an alt/else clause
3. Final else gets no condition label
4. End keyword closes alt block

**Expected Behavior**
If/else chains generate `alt condition1 ... else condition2 ... else ... end` blocks.

**Edge Cases**
- Two-way conditionals (if/else)
- Three-way conditionals (if/else if/else)
- Many branches (5+)
- Mixed alt and opt blocks

---

### SWUT_GEN_00008 - Loop Block Generation

**Requirement**: SWR_GEN_00008
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that Mermaid loop blocks are generated for loop calls.

**Test Approach**
The test verifies that:
1. is_loop=True triggers loop block
2. Loop condition appears in block label
3. Calls in loop are nested in block
4. "loop" prefix indicates loop (for Mermaid compatibility)

**Expected Behavior**
Loop calls generate `opt loop condition ... end` blocks for visualization.

**Edge Cases**
- Nested loops
- Complex loop conditions
- Loops with many iterations
- Mixed loop and conditional

---

### SWUT_GEN_00009 - Function Table Generation

**Requirement**: SWR_GEN_00009
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that function table is generated in output document.

**Test Approach**
The test verifies that:
1. Table section is created after diagram
2. Columns include: Function, Return Type, File, Line, Module
3. All functions in tree are listed
4. Table format is valid markdown

**Expected Behavior**
Function table provides complete reference of all functions with their metadata.

**Edge Cases**
- Large number of functions (100+)
- Functions with very long names
- Functions without modules
- Functions with complex return types

---

### SWUT_GEN_00010 - Module Column in Table

**Requirement**: SWR_GEN_00010
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that module column appears in function table when configured.

**Test Approach**
The test verifies that:
1. Module column is included when use_module_names=True
2. Module names are displayed in table
3. Filename fallback is shown when no module
4. Module column is omitted when not configured

**Expected Behavior**
Module column shows SW module assignment or filename fallback for each function.

**Edge Cases**
- Functions with no module assigned
- Module names with spaces
- Very long module names
- Module names matching function names

---

### SWUT_GEN_00011 - Metadata Section

**Requirement**: SWR_GEN_00011
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that metadata section is included in generated document.

**Test Approach**
The test verifies that:
1. Metadata section appears after function table
2. Analysis timestamp is included
3. Source directory is shown
4. Start function and max depth are listed
5. Statistics are included

**Expected Behavior**
Metadata section provides complete context about the analysis for reproducibility.

**Edge Cases**
- Missing metadata fields
- Very long file paths
- Timestamp formatting
- Statistics with zero values

---

### SWUT_GEN_00012 - Text Tree Generation

**Requirement**: SWR_GEN_00012
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that ASCII art text tree is generated.

**Test Approach**
The test verifies that:
1. Text tree uses box-drawing characters (│, └, ├)
2. Tree structure matches call tree
3. Indentation levels represent depth
4. Function names are shown at each node

**Expected Behavior**
Text tree provides visual ASCII representation of call hierarchy.

**Edge Cases**
- Deep trees (10+ levels)
- Wide trees (many children)
- Very long function names
- Truncated branches

---

### SWUT_GEN_00013 - Statistics Display

**Requirement**: SWR_GEN_00013
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that analysis statistics are displayed in output.

**Test Approach**
The test verifies that:
1. Statistics section appears in output
2. Total and unique function counts shown
3. Max depth reached is displayed
4. Circular dependency count is shown
5. RTE function count is included

**Expected Behavior**
Statistics section provides quantitative summary of the analysis results.

**Edge Cases**
- Zero values for all counts
- Very large counts
- Missing statistics fields
- Statistics formatting

---

### SWUT_GEN_00014 - Circular Dependencies Section

**Requirement**: SWR_GEN_00014
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that circular dependencies are documented in output.

**Test Approach**
The test verifies that:
1. Circular dependencies section is created
2. Each cycle is listed with function names
3. Arrow notation shows cycle flow
4. Section is omitted if no cycles

**Expected Behavior**
Circular dependencies section clearly documents all detected cycles.

**Edge Cases**
- No circular dependencies (section omitted)
- Multiple cycles
- Self-recursion (A→A)
- Long cycles (5+ functions)

---

### SWUT_GEN_00015 - Mermaid File Format

**Requirement**: SWR_GEN_00015
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that Mermaid markdown format is correct.

**Test Approach**
The test verifies that:
1. Output file has .md extension
2. Content starts with # heading
3. Mermaid diagram in ```mermaid code block
4. All sections are properly formatted

**Expected Behavior**
Generated file is valid markdown with embedded Mermaid diagram.

**Edge Cases**
- Very large diagrams
- Special characters in content
- Empty diagrams
- Diagrams with many sections

---

## XMI Generator Tests

### SWUT_GEN_00016 - XMI 2.5 Document Generation

**Requirement**: SWR_GEN_00016
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that XMI/UML 2.5 sequence diagrams are generated.

**Test Approach**
The test verifies that:
1. generate() method creates XMI XML file
2. XML declaration is correct
3. XMI namespaces are used
4. Output file has .xmi extension

**Expected Behavior**
XMIGenerator produces valid XMI 2.5 files with UML sequence diagrams.

**Edge Cases**
- Empty call trees
- Large complex trees
- Trees with cycles
- Special characters in names

---

### SWUT_GEN_00017 - XMI Namespaces and Schema

**Requirement**: SWR_GEN_00017
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that correct XMI and UML namespaces are used.

**Test Approach**
The test verifies that:
1. xmlns:uml namespace is correct
2. xmlns:xmi namespaces are correct
3. XMI version attribute is set
4. Schema references are valid

**Expected Behavior**
XMI document uses standard namespaces for UML 2.5 and XMI compatibility.

**Edge Cases**
- Different XMI versions
- Custom namespaces
- Missing namespace declarations

---

### SWUT_GEN_00018 - UML Lifeline Generation

**Requirement**: SWR_GEN_00018
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that UML lifelines are generated for participants.

**Test Approach**
The test verifies that:
1. uml:Lifeline elements are created
2. Each lifeline has unique ID
3. Lifeline name is participant (function or module)
4. represents attribute references property

**Expected Behavior**
Lifelines represent all participants in the sequence diagram.

**Edge Cases**
- Many lifelines
- Long participant names
- Special characters in names
- Module vs function participants

---

### SWUT_GEN_00019 - UML Message Generation

**Requirement**: SWR_GEN_00019
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that UML messages are generated for calls.

**Test Approach**
The test verifies that:
1. uml:Message elements are created
2. Each message has unique ID
3. Message name includes function and parameters
4. messageSort is "synchCall"
5. sendEvent and receiveEvent reference lifeline events

**Expected Behavior**
Messages represent function calls with proper UML event references.

**Edge Cases**
- Recursive calls
- Many messages
- Long function names with parameters
- Self-calls

---

### SWUT_GEN_00020 - XMI Opt Block Support

**Requirement**: SWR_GEN_00020
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that UML combined fragments for conditional calls are generated.

**Test Approach**
The test verifies that:
1. uml:CombinedFragment is created for conditional calls
2. interactionOperator is "opt"
3. operand element contains condition name
4. Nested message is inside operand

**Expected Behavior**
Conditional calls generate UML combined fragments with opt operator.

**Edge Cases**
- Nested conditionals
- Complex condition expressions
- Empty conditions
- Special characters in conditions

---

### SWUT_GEN_00021 - Module Support in XMI

**Requirement**: SWR_GEN_00021
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that modules are used as lifelines when configured.

**Test Approach**
The test verifies that:
1. use_module_names=True uses modules as lifelines
2. Lifeline names are module names
3. Message names show function names
4. Module configuration is respected

**Expected Behavior**
Module-level XMI diagrams show module lifelines with function messages.

**Edge Cases**
- Functions without modules
- Module name collisions
- Very long module names

---

### SWUT_GEN_00022 - Recursive Call Handling

**Requirement**: SWR_GEN_00022
**Priority**: Low
**Status**: ✅ Pass

**Description**
Validates that recursive calls are marked correctly in XMI.

**Test Approach**
The test verifies that:
1. Recursive calls use messageSort="reply"
2. Non-recursive calls use "synchCall"
3. Recursive calls are visually distinguished
4. Self-calls are handled

**Expected Behavior**
Recursive function calls are marked with reply message sort in XMI.

**Edge Cases**
- Indirect recursion
- Multiple recursive paths
- Deep recursion

---

### SWUT_GEN_00023 - XMI Metadata

**Requirement**: SWR_GEN_00023
**Priority**: Low
**Status**: ✅ Pass

**Description**
Validates that metadata is included in XMI document.

**Test Approach**
The test verifies that:
1. Timestamp is included in metadata
2. Source directory is documented
3. Tool information is present
4. Package documentation is included

**Expected Behavior**
XMI metadata documents analysis context and tool information.

**Edge Cases**
- Very long file paths
- Special characters in paths
- Empty metadata fields

---

### SWUT_GEN_00024 - XML Formatting

**Requirement**: SWR_GEN_00024
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that properly formatted XML is generated.

**Test Approach**
The test verifies that:
1. XML is well-formed (valid tags)
2. Proper indentation is used
3. Special characters are escaped
4. UTF-8 encoding is declared

**Expected Behavior**
XMI output is valid, well-formatted XML 1.0 document.

**Edge Cases**
- Special XML characters (<, >, &, ", ')
- Very long lines
- Deeply nested elements
- Unicode characters

---

### SWUT_GEN_00025 - XMI File Extension

**Requirement**: SWR_GEN_00025
**Priority**: Low
**Status**: ✅ Pass

**Description**
Validates that correct file extension is used for XMI output.

**Test Approach**
The test verifies that:
1. Output file has .xmi extension
2. MIME type is application/XMI
3. File naming follows output_path pattern

**Expected Behavior**
XMI files are saved with standard .xmi extension.

**Edge Cases**
- Custom output paths
- Output paths with existing extensions
- Directory output paths

---

## Requirements Traceability Matrix

| Requirement ID | Test ID | Status | Notes |
|---------------|-----------|---------|--------|
| SWR_GEN_00001 | SWUT_GEN_00001 | ✅ Pass | Mermaid diagram generation |
| SWR_GEN_00002 | SWUT_GEN_00002 | ✅ Pass | Participant management |
| SWR_GEN_00003 | SWUT_GEN_00003 | ✅ Pass | Module-based participants |
| SWR_GEN_00004 | SWUT_GEN_00004 | ✅ Pass | Function names on arrows |
| SWR_GEN_00005 | SWUT_GEN_00005 | ✅ Pass | Parameter display |
| SWR_GEN_00006 | SWUT_GEN_00006 | ✅ Pass | Opt block generation |
| SWR_GEN_00007 | SWUT_GEN_00007 | ✅ Pass | Alt block generation |
| SWR_GEN_00008 | SWUT_GEN_00008 | ✅ Pass | Loop block generation |
| SWR_GEN_00009 | SWUT_GEN_00009 | ✅ Pass | Function table generation |
| SWR_GEN_00010 | SWUT_GEN_00010 | ✅ Pass | Module column in table |
| SWR_GEN_00011 | SWUT_GEN_00011 | ✅ Pass | Metadata section |
| SWR_GEN_00012 | SWUT_GEN_00012 | ✅ Pass | Text tree generation |
| SWR_GEN_00013 | SWUT_GEN_00013 | ✅ Pass | Statistics display |
| SWR_GEN_00014 | SWUT_GEN_00014 | ✅ Pass | Circular dependencies section |
| SWR_GEN_00015 | SWUT_GEN_00015 | ✅ Pass | Mermaid file format |
| SWR_GEN_00016 | SWUT_GEN_00016 | ✅ Pass | XMI document generation |
| SWR_GEN_00017 | SWUT_GEN_00017 | ✅ Pass | XMI namespaces |
| SWR_GEN_00018 | SWUT_GEN_00018 | ✅ Pass | UML lifeline generation |
| SWR_GEN_00019 | SWUT_GEN_00019 | ✅ Pass | UML message generation |
| SWR_GEN_00020 | SWUT_GEN_00020 | ✅ Pass | XMI opt block support |
| SWR_GEN_00021 | SWUT_GEN_00021 | ✅ Pass | Module support in XMI |
| SWR_GEN_00022 | SWUT_GEN_00022 | ✅ Pass | Recursive call handling |
| SWR_GEN_00023 | SWUT_GEN_00023 | ✅ Pass | XMI metadata |
| SWR_GEN_00024 | SWUT_GEN_00024 | ✅ Pass | XML formatting |
| SWR_GEN_00025 | SWUT_GEN_00025 | ✅ Pass | XMI file extension |

## Coverage Summary

- **Total Requirements**: 25
- **Total Tests**: 25
- **Tests Passing**: 25/25 (100%)
- **Code Coverage**: 89%

## Running Tests

```bash
# Run all generator tests
pytest tests/unit/test_mermaid_generator.py
pytest tests/unit/test_xmi_generator.py

# Run specific test
pytest tests/unit/test_mermaid_generator.py::TestClass::test_SWUT_GEN_00001

# Run with coverage
pytest tests/unit/test_mermaid_generator.py tests/unit/test_xmi_generator.py --cov=autosar_calltree/generators --cov-report=term-missing
```

## Change History

| Date | Version | Author | Change Description |
|-------|---------|---------|-------------------|
| 2026-02-11 | 2.0 | Reorganized by requirement structure, removed Test Function labels, using natural language |
| 2026-02-10 | 1.0 | Initial test documentation |
