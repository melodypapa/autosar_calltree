# Analyzers Package Test Cases

## Overview

This document describes test cases for the Analyzers package, organized by requirement structure.

**Requirements Document**: [requirements_analyzers.md](../requirements/requirements_analyzers.md)

**Package**: `autosar_calltree.analyzers`
**Source Files**: `call_tree_builder.py`
**Requirement IDs**: SWR_ANALYZER_00001 - SWR_ANALYZER_00015
**Coverage**: 94%

---

## Builder Initialization Tests

### SWUT_ANALYZER_00001 - Builder Initialization

**Requirement**: SWR_ANALYZER_00001
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that CallTreeBuilder can be initialized with a FunctionDatabase instance.

**Test Approach**
The test verifies that:
1. CallTreeBuilder accepts a FunctionDatabase parameter
2. Database reference is stored correctly
3. Internal state is initialized (visited_functions, call_stack, statistics)
4. Builder is ready for tree building

**Expected Behavior**
CallTreeBuilder is initialized with database connection and clean state for building call trees.

**Edge Cases**
- None initialization (should raise error)
- Empty database
- Database with cached data

---

### SWUT_ANALYZER_00002 - State Management

**Requirement**: SWR_ANALYZER_00002
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that builder state is reset between builds.

**Test Approach**
The test verifies that:
1. Each build_tree() call resets internal state
2. Call stack is empty at start of build
3. Visited functions set is empty at start of build
4. Statistics are reset for new build
5. Multiple sequential builds work independently

**Expected Behavior**
Each tree building operation starts with clean state, preventing contamination from previous builds.

**Edge Cases**
- Multiple builds with same function
- Multiple builds with different functions
- Builds with errors vs successful builds

---

### SWUT_ANALYZER_00003 - Start Function Validation

**Requirement**: SWR_ANALYZER_00003
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that start function exists in database before building tree.

**Test Approach**
The test verifies that:
1. Start function is looked up in database
2. Error result is returned if function not found
3. Warning is shown if multiple definitions exist
4. Valid function starts tree building

**Expected Behavior**
Start function validation prevents attempts to build trees from non-existent functions.

**Edge Cases**
- Function not in database
- Multiple definitions of start function
- Case-sensitive vs insensitive lookup
- Empty function name

---

## Tree Traversal Tests

### SWUT_ANALYZER_00004 - Depth-First Traversal Algorithm

**Requirement**: SWR_ANALYZER_00004
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that call tree is built using depth-first traversal.

**Test Approach**
The test verifies that:
1. Traversal starts at root function
2. Children are processed in order encountered
3. Recursive calls go deep before exploring siblings
4. Complete call graph is traversed

**Expected Behavior**
DFS algorithm explores each call path to maximum depth before backtracking, building complete tree.

**Edge Cases**
- Wide trees (many children at each level)
- Deep trees (long call chains)
- Graphs with cross-links
- Multiple paths to same function

---

### SWUT_ANALYZER_00005 - Cycle Detection

**Requirement**: SWR_ANALYZER_00005
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that circular dependencies in call graph are detected.

**Test Approach**
The test verifies that:
1. Call stack tracks visited functions in current path
2. Function already in stack indicates cycle
3. CircularDependency objects are created for detected cycles
4. Direct recursion (function calls itself) is detected

**Expected Behavior**
Cycles are detected when a function is encountered that's already in the current traversal path.

**Edge Cases**
- Self-recursion (A calls A)
- Indirect recursion (A calls B calls A)
- Long cycles (A→B→C→D→A)
- Multiple cycles in same tree

---

### SWUT_ANALYZER_00006 - Cycle Handling in Tree

**Requirement**: SWR_ANALYZER_00006
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that cycles in call graph are handled correctly in tree structure.

**Test Approach**
The test verifies that:
1. Recursive calls are marked with is_recursive=True
2. Children of recursive calls are not explored
3. Infinite recursion is prevented
4. Cycle is recorded in result

**Expected Behavior**
When a cycle is detected, recursion stops and the cycle is noted without infinite traversal.

**Edge Cases**
- Multiple cycles in tree
- Cycle at root level
- Cycle in deep subtree
- Partial cycles (multiple paths to same function)

---

### SWUT_ANALYZER_00007 - Max Depth Enforcement

**Requirement**: SWR_ANALYZER_00007
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that max_depth limit is respected during traversal.

**Test Approach**
The test verifies that:
1. Traversal stops at specified depth
2. Nodes beyond max_depth are not added
3. is_truncated flag is set on limited nodes
4. Max depth of 0 allows only root function

**Expected Behavior**
Tree traversal respects max_depth parameter, preventing uncontrolled exploration of large codebases.

**Edge Cases**
- Max depth of 0 (root only)
- Max depth greater than actual tree depth
- Max depth of 1 (root and immediate children)
- Very large max depth values

---

### SWUT_ANALYZER_00008 - Node Depth Tracking

**Requirement**: SWR_ANALYZER_00008
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that depth of each node in tree is tracked correctly.

**Test Approach**
The test verifies that:
1. Root node has depth 0
2. Each child has depth = parent_depth + 1
3. Depth is consistent across tree
4. Depth field is used for truncation decisions

**Expected Behavior**
Node depth accurately represents distance from root, supporting depth limits and statistics.

**Edge Cases**
- Deep trees (>10 levels)
- Wide trees at varying depths
- Depth after cycle detection
- Depth after truncation

---

## Result Generation Tests

### SWUT_ANALYZER_00009 - AnalysisResult Creation

**Requirement**: SWR_ANALYZER_00009
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that complete analysis result objects are created.

**Test Approach**
The test verifies that:
1. build_tree() returns AnalysisResult object
2. Root function field is populated
3. Call tree is included
4. Statistics are calculated
5. Circular dependencies list is included
6. Errors list is populated if applicable

**Expected Behavior**
Complete AnalysisResult objects contain all information about the analysis: tree, statistics, cycles, and errors.

**Edge Cases**
- Successful analysis (no errors)
- Failed analysis (errors only, no tree)
- Analysis with circular dependencies
- Analysis with missing functions

---

### SWUT_ANALYZER_00010 - Statistics Collection

**Requirement**: SWR_ANALYZER_00010
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that statistics are collected during traversal.

**Test Approach**
The test verifies that:
1. Total node count is tracked
2. Max depth reached is recorded
3. Unique function count is calculated
4. Circular dependency count is incremented
5. Statistics object is created with correct values

**Expected Behavior**
Traversal collects comprehensive statistics about the tree for reporting and analysis.

**Edge Cases**
- Empty tree (only root)
- Tree with only unique functions
- Tree with many duplicate calls
- Tree with no circular dependencies

---

### SWUT_ANALYZER_00011 - Unique Function Tracking

**Requirement**: SWR_ANALYZER_00011
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that unique functions are tracked using a set.

**Test Approach**
The test verifies that:
1. First encounter of function adds to set
2. Subsequent encounters don't increase count
3. Set is used for unique function count
4. Functions are deduplicated correctly

**Expected Behavior**
Set-based tracking ensures unique function count accurately reflects distinct functions called.

**Edge Cases**
- Same function called multiple times
- Same function from different call sites
- Case sensitivity
- Function from different files (same name)

---

### SWUT_ANALYZER_00012 - Missing Function Handling

**Requirement**: SWR_ANALYZER_00012
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that functions not in database are handled gracefully.

**Test Approach**
The test verifies that:
1. Missing functions are skipped with warning
2. Tree building continues despite missing functions
3. Warning includes function name and context
4. Statistics note missing function count

**Expected Behavior**
Missing functions don't stop analysis - tree is built as completely as possible with warnings.

**Edge Cases**
- Root function not in database
- Leaf function not in database
- Multiple missing functions in chain
- All called functions missing

---

## RTE Calls Tests

### SWUT_ANALYZER_00013 - RTE Call Filtering

**Requirement**: SWR_ANALYZER_00013
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that RTE calls can be included or excluded from tree.

**Test Approach**
The test verifies that:
1. include_rte=False excludes RTE functions from tree
2. include_rte=True includes RTE functions
3. RTE detection uses is_rte_function() method
4. Filter works regardless of function position in tree

**Expected Behavior**
RTE calls are filtered based on include_rte flag, allowing control over RTE inclusion.

**Edge Cases**
- Only RTE calls in tree
- Mixed RTE and non-RTE calls
- RTE calls at root level
- Nested RTE calls

---

### SWUT_ANALYZER_00014 - Qualified Name Usage

**Requirement**: SWR_ANALYZER_00014
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that qualified names are used for cycle detection.

**Test Approach**
The test verifies that:
1. Qualified names (file::function) are used in call stack
2. Static functions with same name in different files are distinguished
3. Qualified name format is "file_path::function_name"
4. Cycle detection uses qualified names

**Expected Behavior**
Qualified names prevent false cycle detection when static functions share names across files.

**Edge Cases**
- Same function name in different files
- Static vs global functions with same name
- Functions in deeply nested directories
- Functions with no qualified name

---

### SWUT_ANALYZER_00015 - Verbose Logging

**Requirement**: SWR_ANALYZER_00015
**Priority**: Low
**Status**: ✅ Pass

**Description**
Validates that progress is logged during tree building in verbose mode.

**Test Approach**
The test verifies that:
1. Current function being processed is logged
2. Depth level is indicated
3. Cycle detection events are logged
4. Missing function warnings are shown
5. Logging respects verbose flag

**Expected Behavior**
Verbose logging provides detailed progress information for debugging and monitoring long analyses.

**Edge Cases**
- Verbose mode off (no logging)
- Very large trees (many log messages)
- Trees with many cycles
- Trees with many missing functions

---

## Requirements Traceability Matrix

| Requirement ID | Test ID | Status | Notes |
|---------------|-----------|---------|--------|
| SWR_ANALYZER_00001 | SWUT_ANALYZER_00001 | ✅ Pass | Builder initialization |
| SWR_ANALYZER_00002 | SWUT_ANALYZER_00002 | ✅ Pass | State management |
| SWR_ANALYZER_00003 | SWUT_ANALYZER_00003 | ✅ Pass | Start function validation |
| SWR_ANALYZER_00004 | SWUT_ANALYZER_00004 | ✅ Pass | DFS traversal |
| SWR_ANALYZER_00005 | SWUT_ANALYZER_00005 | ✅ Pass | Cycle detection |
| SWR_ANALYZER_00006 | SWUT_ANALYZER_00006 | ✅ Pass | Cycle handling |
| SWR_ANALYZER_00007 | SWUT_ANALYZER_00007 | ✅ Pass | Max depth enforcement |
| SWR_ANALYZER_00008 | SWUT_ANALYZER_00008 | ✅ Pass | Depth tracking |
| SWR_ANALYZER_00009 | SWUT_ANALYZER_00009 | ✅ Pass | AnalysisResult creation |
| SWR_ANALYZER_00010 | SWUT_ANALYZER_00010 | ✅ Pass | Statistics collection |
| SWR_ANALYZER_00011 | SWUT_ANALYZER_00011 | ✅ Pass | Unique function tracking |
| SWR_ANALYZER_00012 | SWUT_ANALYZER_00012 | ✅ Pass | Missing function handling |
| SWR_ANALYZER_00013 | SWUT_ANALYZER_00013 | ✅ Pass | RTE call filtering |
| SWR_ANALYZER_00014 | SWUT_ANALYZER_00014 | ✅ Pass | Qualified name usage |
| SWR_ANALYZER_00015 | SWUT_ANALYZER_00015 | ✅ Pass | Verbose logging |

## Coverage Summary

- **Total Requirements**: 15
- **Total Tests**: 15
- **Tests Passing**: 15/15 (100%)
- **Code Coverage**: 94%

## Running Tests

```bash
# Run all analyzer tests
pytest tests/unit/test_call_tree_builder.py

# Run specific test
pytest tests/unit/test_call_tree_builder.py::TestClass::test_SWUT_ANALYZER_00001

# Run with coverage
pytest tests/unit/test_call_tree_builder.py --cov=autosar_calltree/analyzers --cov-report=term-missing
```

## Change History

| Date | Version | Author | Change Description |
|-------|---------|---------|-------------------|
| 2026-02-11 | 2.0 | Reorganized by requirement structure, removed Test Function labels, using natural language |
| 2026-02-10 | 1.0 | Initial test documentation |
