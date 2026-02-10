# Analyzers Package Requirements

**Package**: `autosar_calltree.analyzers`
**Source Files**: `call_tree_builder.py`
**Requirements**: SWR_ANALYZER_00001 - SWR_ANALYZER_00015 (15 requirements)

---

## Overview

The analyzers package provides call tree analysis functionality, building directed call graphs from function definitions and their call relationships.

**Core Class**: `CallTreeBuilder`

---

## Builder Initialization (SWR_ANALYZER_00001 - SWR_ANALYZER_00003)

### SWR_ANALYZER_00001 - Builder Initialization
**Purpose**: Initialize builder with function database

**Parameter**: `FunctionDatabase` instance

**Storage**: Reference to database for function lookups

**Implementation**: `CallTreeBuilder.__init__(db)`

---

### SWR_ANALYZER_00002 - State Management
**Purpose**: Reset builder state between builds

**State Tracked**:
- Call stack (for cycle detection)
- Visited functions (for unique tracking)
- Statistics (for reporting)

**Implementation**: Reset at start of each `build_tree()` call

---

### SWR_ANALYZER_00003 - Start Function Validation
**Purpose**: Validate start function exists

**Behavior**:
- Lookup start function in database
- Return error result if not found
- Show warning if multiple definitions exist

**Implementation**: Validation at start of `build_tree()`

---

## Tree Traversal (SWR_ANALYZER_00004 - SWR_ANALYZER_00008)

### SWR_ANALYZER_00004 - Depth-First Traversal Algorithm
**Purpose**: Build call tree using DFS

**Algorithm**:
1. Start at root function
2. For each function call, create child node
3. Recursively process called functions
4. Track depth and visited functions

**Method**: `_build_tree_recursive()`

---

### SWR_ANALYZER_00005 - Cycle Detection
**Purpose**: Detect circular dependencies

**Detection Method**: Track call stack

**Behavior**:
- If function already in stack → cycle detected
- Create `CircularDependency` object
- Mark node as `is_recursive=True`
- Don't explore children of recursive call

**Implementation**: Call stack tracking in `_build_tree_recursive()`

---

### SWR_ANALYZER_00006 - Cycle Handling in Tree
**Purpose**: Properly handle cycles in call graph

**Behavior**:
- Mark node as recursive
- Don't traverse children of recursive call
- Record cycle in result

**Rationale**: Prevent infinite recursion

---

### SWR_ANALYZER_00007 - Max Depth Enforcement
**Purpose**: Respect max_depth limit

**Behavior**:
- Check depth before adding children
- Mark `is_truncated=True` if limit reached
- Don't add children beyond limit

**Implementation**: Depth check before recursive calls

---

### SWR_ANALYZER_00008 - Node Depth Tracking
**Purpose**: Track depth of each node in tree

**Storage**: `depth` field in `CallTreeNode`

**Use**: Statistics and truncation decisions

---

## Result Generation (SWR_ANALYZER_00009 - SWR_ANALYZER_00012)

### SWR_ANALYZER_00009 - AnalysisResult Creation
**Purpose**: Create complete analysis result

**Method**: `build_tree(start_function, max_depth, include_rte)`

**Returns**: `AnalysisResult` object with:
- Root function and call tree
- Statistics
- Circular dependencies
- Errors (if any)
- Metadata (timestamp, source dir, max depth)

---

### SWR_ANALYZER_00010 - Statistics Collection
**Purpose**: Collect statistics during traversal

**Metrics**:
- Total nodes (function calls)
- Max depth reached
- Unique functions
- Circular dependencies found

**Implementation**: Update statistics during traversal

---

### SWR_ANALYZER_00011 - Unique Function Tracking
**Purpose**: Track unique functions in tree

**Method**: Use set to track function names

**Use**: Count unique functions in statistics

---

### SWR_ANALYZER_00012 - Missing Function Handling
**Purpose**: Handle functions not in database

**Behavior**:
- Skip missing functions with warning
- Continue building tree
- Optional logging in verbose mode

**Rationale**: Allow partial analysis

---

## RTE Calls (SWR_ANALYZER_00013 - SWR_ANALYZER_00015)

### SWR_ANALYZER_00013 - RTE Call Filtering
**Purpose**: Optionally include/exclude RTE calls

**Parameter**: `include_rte` flag

**Default**: False (RTE calls excluded)

**Implementation**: Check `is_rte_function` before adding to tree

---

### SWR_ANALYZER_00014 - Qualified Name Usage
**Purpose**: Use qualified names for cycle detection

**Format**: `"file::function"`

**Use**: Differentiate static functions with same name

---

### SWR_ANALYZER_00015 - Verbose Logging
**Purpose**: Log progress during tree building

**Messages**:
- Current function being processed
- Depth level
- Cycle detection
- Missing functions

**Trigger**: Verbose flag (not yet implemented)

---

## Summary

**Total Requirements**: 15
**Implementation Status**: ✅ All Implemented

**Package Structure**:
```
autosar_calltree.analyzers/
└── call_tree_builder.py    # SWR_ANALYZER_00001 - SWR_ANALYZER_00015
```

**Key Features**:
- Depth-first call graph traversal
- Automatic cycle detection
- Configurable max depth
- RTE call filtering
- Comprehensive statistics
