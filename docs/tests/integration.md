# Integration and End-to-End Tests

## Overview

This document describes the integration and end-to-end test cases for the AUTOSAR Call Tree Analyzer.

**Test Type**: Integration / End-to-End Tests

**Requirement IDs**: SWR_E2E_00001 - SWR_E2E_00018

**Test IDs**: SWUT_E2E_00001 - SWUT_E2E_00018

**Purpose**: Validates complete workflows from CLI invocation through parsing, analysis, and output generation.

## Test Cases

### SWUT_E2E_00001 - Basic Workflow Analysis

**Requirement:** SWR_E2E_00001
**Priority:** High
**Status:** ✅ Pass

**Test Purpose:**
Validates end-to-end workflow: source scanning, parsing, analysis, and Mermaid output generation.

**Test Function:** `test_SWUT_E2E_00001_basic_workflow_analysis()`

**Test Steps:**
1. Create test source files with AUTOSAR functions
2. Run CLI command with start function
3. Verify output file created
4. Verify Mermaid diagram contains expected participants
5. Verify call sequence is correct

**Expected Result:**
- Output file created successfully
- Valid Mermaid syntax
- All functions appear as participants
- Call arrows show correct sequence

---

### SWUT_E2E_00002 - Cache Functionality

**Requirement:** SWR_E2E_00002
**Priority:** High
**Status:** ✅ Pass

**Test Purpose:**
Validates that cache is created on first run and reused on subsequent runs.

**Test Function:** `test_SWUT_E2E_00002_cache_functionality()`

**Test Steps:**
1. Clear any existing cache
2. Run analysis (first run)
3. Verify cache file created
4. Run analysis again (second run)
5. Verify cache was used (faster execution)

**Expected Result:**
- Cache file created in `.cache/` directory
- Second run is faster (uses cache)
- Both runs produce identical output

---

### SWUT_E2E_00003 - Module Configuration Integration

**Requirement:** SWR_E2E_00003
**Priority:** Medium
**Status:** ✅ Pass

**Test Purpose:**
Validates module configuration is loaded and used for module-level diagrams.

**Test Function:** `test_SWUT_E2E_00003_module_configuration_integration()`

**Test Steps:**
1. Create module mapping YAML file
2. Create test source files matching mappings
3. Run CLI with `--use-module-names`
4. Verify diagram uses module names as participants

**Expected Result:**
- Module names appear as participants instead of function names
- Function names appear on arrows
- Module column appears in function table

---

### SWUT_E2E_00004 - Parameters on Diagram Arrows

**Requirement:** SWR_E2E_00004
**Priority:** Medium
**Status:** ✅ Pass

**Test Purpose:**
Validates that function parameters are shown on diagram arrows when enabled.

**Test Function:** `test_SWUT_E2E_00004_parameters_on_diagram_arrows()`

**Test Steps:**
1. Create functions with various parameter types
2. Run analysis with `--show-params`
3. Verify parameters appear on arrows

**Expected Result:**
- Parameters shown in format: `function(param1, param2)`
- Pointer types show asterisk
- Const types show const prefix

---

### SWUT_E2E_00005 - Qualified Names

**Requirement:** SWR_E2E_00005
**Priority:** Medium
**Status:** ✅ Pass

**Test Purpose:**
Validates qualified name generation for disambiguating functions.

**Test Function:** `test_SWUT_E2E_00005_qualified_names()`

**Test Steps:**
1. Create multiple functions with same name in different files
2. Run analysis with `--qualified-names`
3. Verify qualified names appear in output

**Expected Result:**
- Functions show as `filename::function_name` format
- Disambiguates between duplicate function names

---

### SWUT_E2E_00006 - XMI Output Format

**Requirement:** SWR_E2E_00006
**Priority:** Medium
**Status:** ✅ Pass

**Test Purpose:**
Validates XMI/UML 2.5 output generation.

**Test Function:** `test_SWUT_E2E_00006_xmi_output_format()`

**Test Steps:**
1. Run analysis with `--format xmi`
2. Verify XMI file created
3. Parse and validate XML structure
4. Verify UML namespaces present

**Expected Result:**
- Valid XML document
- Contains UML 2.5 namespaces
- Contains sequence diagram elements

---

### SWUT_E2E_00007 - Both Output Formats

**Requirement:** SWR_E2E_00007
**Priority:** Low
**Status:** ✅ Pass

**Test Purpose:**
Validates generating both Mermaid and XMI outputs simultaneously.

**Test Function:** `test_SWUT_E2E_00007_both_output_formats()`

**Test Steps:**
1. Run analysis with `--format both`
2. Verify both `.md` and `.xmi` files created
3. Validate both files

**Expected Result:**
- Mermaid file with valid syntax
- XMI file with valid XML
- Both contain same call tree information

---

### SWUT_E2E_00008 - Max Depth Enforcement

**Requirement:** SWR_E2E_00008
**Priority:** High
**Status:** ✅ Pass

**Test Purpose:**
Validates that max-depth limit is enforced during traversal.

**Test Function:** `test_SWUT_E2E_00008_max_depth_enforcement()`

**Test Steps:**
1. Create deeply nested call chain (depth > max)
2. Run analysis with `--max-depth 2`
3. Verify output respects depth limit

**Expected Result:**
- Only 2 levels of calls shown
- Deeper functions not included
- Statistics show truncated call count

---

### SWUT_E2E_00009 - Circular Dependency Detection

**Requirement:** SWR_E2E_00009
**Priority:** High
**Status:** ✅ Pass

**Test Purpose:**
Validates detection and reporting of circular dependencies.

**Test Function:** `test_SWUT_E2E_00009_circular_dependency_detection()`

**Test Steps:**
1. Create source with recursive function call
2. Run analysis
3. Verify circular dependency reported
4. Verify special marker in diagram

**Expected Result:**
- Circular dependency section in output
- Recursive call marked in diagram
- No infinite loop during traversal

---

### SWUT_E2E_00010 - Function Listing

**Requirement:** SWR_E2E_00010
**Priority:** Low
**Status:** ✅ Pass

**Test Purpose:**
Validates `--list-functions` lists all discoverable functions.

**Test Function:** `test_SWUT_E2E_00010_function_listing()`

**Test Steps:**
1. Create multiple source files
2. Run CLI with `--list-functions`
3. Verify all functions listed

**Expected Result:**
- All functions from all files listed
- Includes file locations
- Includes function signatures

---

### SWUT_E2E_00011 - Function Search

**Requirement:** SWR_E2E_00011
**Priority:** Low
**Status:** ✅ Pass

**Test Purpose:**
Validates `--search` finds functions by pattern.

**Test Function:** `test_SWUT_E2E_00011_function_search()`

**Test Steps:**
1. Create functions with various names
2. Run CLI with `--search "Init"`
3. Verify matching functions returned

**Expected Result:**
- Only functions matching pattern shown
- Case-insensitive matching
- Shows file locations

---

### SWUT_E2E_00012 - Error Handling - Missing Start Function

**Requirement:** SWR_E2E_00012
**Priority:** High
**Status:** ✅ Pass

**Test Purpose:**
Validates graceful error when start function not found.

**Test Function:** `test_SWUT_E2E_00012_error_handling_missing_start_function()`

**Test Steps:**
1. Run analysis with non-existent start function
2. Verify error message
3. Verify exit code is non-zero

**Expected Result:**
- Clear error message
- Exit code 1
- No output file created

---

### SWUT_E2E_00013 - Error Handling - Invalid Source Directory

**Requirement:** SWR_E2E_00013
**Priority:** High
**Status:** ✅ Pass

**Test Purpose:**
Validates error handling for invalid source directory.

**Test Function:** `test_SWUT_E2E_00013_error_handling_invalid_source_directory()`

**Test Steps:**
1. Run CLI with non-existent source directory
2. Verify error message
3. Verify exit code is non-zero

**Expected Result:**
- Clear error message
- Exit code 1
- Suggests valid directories

---

### SWUT_E2E_00014 - Error Handling - Invalid Module Config

**Requirement:** SWR_E2E_00014
**Priority:** Medium
**Status:** ✅ Pass

**Test Purpose:**
Validates error handling for invalid module configuration.

**Test Function:** `test_SWUT_E2E_00014_error_handling_invalid_module_config()`

**Test Steps:**
1. Create invalid YAML config file
2. Run CLI with `--module-config` pointing to invalid file
3. Verify validation error

**Expected Result:**
- Clear validation error message
- Indicates specific validation failure
- Exit code 1

---

### SWUT_E2E_00015 - Statistics Accuracy

**Requirement:** SWR_E2E_00015
**Priority**: Medium
**Status:** ✅ Pass

**Test Purpose:**
Validates statistics accuracy in metadata section.

**Test Function:** `test_SWUT_E2E_00015_statistics_accuracy()`

**Test Steps:**
1. Create known call tree structure
2. Run analysis
3. Verify statistics match expected

**Expected Result:**
- Total functions count accurate
- Total calls count accurate
- Max depth accurate
- Unique functions count accurate

---

### SWUT_E2E_00016 - Performance - Large Codebase

**Requirement:** SWR_E2E_00016
**Priority:** Low
**Status:** ✅ Pass

**Test Purpose:**
Validates acceptable performance on larger codebases.

**Test Function:** `test_SWUT_E2E_00016_performance_large_codebase()`

**Test Steps:**
1. Create test codebase with 100+ functions
2. Run analysis and measure time
3. Verify completes within acceptable time

**Expected Result:**
- Analysis completes within 10 seconds
- Memory usage reasonable
- No performance regressions

---

### SWUT_E2E_00017 - Verbose Output

**Requirement:** SWR_E2E_00017
**Priority:** Low
**Status:** ✅ Pass

**Test Purpose:**
Validates verbose output shows progress information.

**Test Function:** `test_SWUT_E2E_00017_verbose_output()`

**Test Steps:**
1. Run analysis with `--verbose`
2. Verify progress messages displayed
3. Verify statistics shown

**Expected Result:**
- File scanning progress shown
- Function discovery progress shown
- Tree building progress shown
- Final statistics displayed

---

### SWUT_E2E_00018 - Cache Invalidation

**Requirement:** SWR_E2E_00018
**Priority:** Medium
**Status:** ✅ Pass

**Test Purpose:**
Validates cache is invalidated when source files change.

**Test Function:** `test_SWUT_E2E_00018_cache_invalidation()`

**Test Steps:**
1. Run analysis and create cache
2. Modify a source file
3. Run analysis again
4. Verify cache was rebuilt

**Expected Result:**
- Cache invalidated on source change
- New cache created
- Updated results reflect changes

---

## Requirements Traceability Matrix

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_E2E_00001 | SWUT_E2E_00001 | test_SWUT_E2E_00001_basic_workflow_analysis | ✅ Pass |
| SWR_E2E_00002 | SWUT_E2E_00002 | test_SWUT_E2E_00002_cache_functionality | ✅ Pass |
| SWR_E2E_00003 | SWUT_E2E_00003 | test_SWUT_E2E_00003_module_configuration_integration | ✅ Pass |
| SWR_E2E_00004 | SWUT_E2E_00004 | test_SWUT_E2E_00004_parameters_on_diagram_arrows | ✅ Pass |
| SWR_E2E_00005 | SWUT_E2E_00005 | test_SWUT_E2E_00005_qualified_names | ✅ Pass |
| SWR_E2E_00006 | SWUT_E2E_00006 | test_SWUT_E2E_00006_xmi_output_format | ✅ Pass |
| SWR_E2E_00007 | SWUT_E2E_00007 | test_SWUT_E2E_00007_both_output_formats | ✅ Pass |
| SWR_E2E_00008 | SWUT_E2E_00008 | test_SWUT_E2E_00008_max_depth_enforcement | ✅ Pass |
| SWR_E2E_00009 | SWUT_E2E_00009 | test_SWUT_E2E_00009_circular_dependency_detection | ✅ Pass |
| SWR_E2E_00010 | SWUT_E2E_00010 | test_SWUT_E2E_00010_function_listing | ✅ Pass |
| SWR_E2E_00011 | SWUT_E2E_00011 | test_SWUT_E2E_00011_function_search | ✅ Pass |
| SWR_E2E_00012 | SWUT_E2E_00012 | test_SWUT_E2E_00012_error_handling_missing_start_function | ✅ Pass |
| SWR_E2E_00013 | SWUT_E2E_00013 | test_SWUT_E2E_00013_error_handling_invalid_source_directory | ✅ Pass |
| SWR_E2E_00014 | SWUT_E2E_00014 | test_SWUT_E2E_00014_error_handling_invalid_module_config | ✅ Pass |
| SWR_E2E_00015 | SWUT_E2E_00015 | test_SWUT_E2E_00015_statistics_accuracy | ✅ Pass |
| SWR_E2E_00016 | SWUT_E2E_00016 | test_SWUT_E2E_00016_performance_large_codebase | ✅ Pass |
| SWR_E2E_00017 | SWUT_E2E_00017 | test_SWUT_E2E_00017_verbose_output | ✅ Pass |
| SWR_E2E_00018 | SWUT_E2E_00018 | test_SWUT_E2E_00018_cache_invalidation | ✅ Pass |

## Coverage Summary

- **Total Requirements**: 18
- **Total Tests**: 18
- **Tests Passing**: 18/18 (100%)
- **Test Type**: Integration / End-to-End

## Running Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run specific integration test
pytest tests/integration/test_cli.py::test_basic_workflow

# Run with coverage
pytest tests/integration/ --cov=autosar_calltree --cov-report=html --cov-report=term
```

## Change History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-02-10 | 1.0 | Claude | Initial integration test documentation with traceability matrix |
