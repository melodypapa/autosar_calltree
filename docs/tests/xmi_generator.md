# XMI Generator Test Cases

## Overview

This document describes the test cases for the XMI (UML 2.5) Generator module.

**Requirements Document**: [../requirements/requirements_xmi.md](../requirements/requirements_xmi.md)

**Requirement IDs**: SWR_XMI_00001 - SWR_XMI_00003

**Test IDs**: SWUT_XMI_00001 - SWUT_XMI_00003

**Coverage**: 70%

## Test Cases

### SWUT_XMI_00001 - XMI Namespace Compliance

**Requirement:** SWR_XMI_00001
**Priority:** High
**Status:** ✅ Pass

**Test Purpose:**
Validates that the XMI generator produces documents with correct UML 2.5 namespace declarations and XML structure.

**Test Function:** `test_SWUT_XMI_00001_xmi_namespace_compliance()`

**Test Steps:**
1. Create a simple call tree with one function
2. Generate XMI output
3. Parse the XML document
4. Verify namespace declarations
5. Verify root element structure

**Expected Result:**
- Document contains UML namespace: `http://www.eclipse.org/uml2/5.0.0/UML`
- Document contains XMI namespace: `http://www.omg.org/spec/XMI/20131001`
- Root element is `<uml:Model>` with proper xmi:version and xmlns attributes

**Edge Cases Covered:**
- Empty call tree
- Single function call tree
- Multiple function call tree

---

### SWUT_XMI_00002 - Sequence Diagram Representation

**Requirement:** SWR_XMI_00002
**Priority:** High
**Status:** ✅ Pass

**Test Purpose:**
Validates that the XMI generator correctly represents sequence diagrams with proper participants, messages, and interactions.

**Test Function:** `test_SWUT_XMI_00002_sequence_diagram_representation()`

**Test Steps:**
1. Create a call tree with:
   - Start function calling multiple child functions
   - At least 2 levels of depth
   - Mix of different return types
2. Generate XMI output
3. Parse and verify:
   - `packagedElement` of type `uml:Interaction`
   - `lifeline` elements for each participant
   - `message` elements for each function call
   - Proper `sendEvent` and `receiveEvent` references
   - Message signatures include parameters

**Expected Result:**
- One Interaction element per root node
- Lifelines created for all functions in call tree
- Messages have correct names (function names)
- Messages have correct signatures (return type + parameters)
- Event references are valid (no broken references)

**Edge Cases Covered:**
- Recursive function calls
- Functions with no parameters
- Functions with multiple parameters
- Functions with pointer/const parameters

---

### SWUT_XMI_00003 - Opt Block Support

**Requirement:** SWR_XMI_00003
**Priority:** High
**Status:** ✅ Pass

**Test Purpose:**
Validates that the XMI generator correctly generates `opt` (optional) combined fragments for conditional function calls.

**Test Function:** `test_SWUT_XMI_00003_opt_block_support()`

**Test Steps:**
1. Create a call tree with:
   - A function calling another conditionally (`is_optional=True`)
   - Condition text set (e.g., "mode == 0x05")
   - Mix of optional and regular calls
2. Generate XMI output
3. Parse and verify:
   - `uml:Fragment` elements with `interactionOperator="opt"`
   - Fragment has `operand` containing the conditional messages
   - Condition text appears in operand name
   - Regular calls appear outside fragments

**Expected Result:**
- One `uml:Fragment` per group of optional calls
- Fragment interactionOperator is "opt"
- Operand contains the conditional message
- Operand name matches the condition text
- Regular calls are not wrapped in fragments

**Edge Cases Covered:**
- Multiple optional calls with same condition
- Optional call with empty condition
- Mix of optional and regular calls
- Nested optional calls (if supported)

---

## Requirements Traceability Matrix

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_XMI_00001 | SWUT_XMI_00001 | test_SWUT_XMI_00001_xmi_namespace_compliance | ✅ Pass |
| SWR_XMI_00002 | SWUT_XMI_00002 | test_SWUT_XMI_00002_sequence_diagram_representation | ✅ Pass |
| SWR_XMI_00003 | SWUT_XMI_00003 | test_SWUT_XMI_00003_opt_block_support | ✅ Pass |

## Coverage Summary

- **Total Requirements**: 3
- **Total Tests**: 3
- **Tests Passing**: 3/3 (100%)
- **Code Coverage**: 70%

## Running Tests

```bash
# Run all XMI generator tests
pytest tests/unit/test_xmi_generator.py

# Run specific test case
pytest tests/unit/test_xmi_generator.py::TestXMIGenerator::test_SWUT_XMI_00001_xmi_namespace_compliance

# Run with coverage
pytest tests/unit/test_xmi_generator.py --cov=src/autosar_calltree/generators/xmi_gen.py --cov-report=term-missing
```

## Change History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-02-10 | 1.0 | Claude | Initial test documentation for XMI generator with traceability matrix |
