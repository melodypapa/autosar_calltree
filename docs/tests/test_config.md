# Config Package Test Cases

## Overview

This document describes test cases for the Config package, organized by requirement structure.

**Requirements Document**: [requirements_config.md](../requirements/requirements_config.md)

**Package**: `autosar_calltree.config`
**Source Files**: `module_config.py`
**Requirement IDs**: SWR_CONFIG_00001 - SWR_CONFIG_00008
**Coverage**: 97%

---

## YAML Configuration Tests

### SWUT_CONFIG_00001 - YAML Configuration File Support

**Requirement**: SWR_CONFIG_00001
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that ModuleConfig class can successfully load a valid YAML configuration file.

**Test Approach**
The test verifies that:
1. YAML file with version, file_mappings, and pattern_mappings loads
2. All mappings are populated correctly
3. Default module is read correctly
4. Configuration structure is validated

**Expected Behavior**
Module configuration is loaded from YAML file with all mapping types recognized.

**Edge Cases**
- Valid YAML with all sections
- Mix of file_mappings and pattern_mappings
- Optional default_module
- YAML files with comments

---

### SWUT_CONFIG_00002 - Configuration Loading and Validation

**Requirement**: SWR_CONFIG_00005
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that configuration loading validates required fields and structure.

**Test Approach**
The test verifies that:
1. YAML syntax is validated
2. Required fields are present or explicit default
3. Data types are correct (dict for mappings, str for values)
4. Invalid configurations raise ValueError

**Expected Behavior**
Invalid configurations are rejected with clear error messages during initialization.

**Edge Cases**
- Missing version field
- Invalid YAML syntax
- Wrong data types for fields
- Empty configuration file

---

### SWUT_CONFIG_00003 - File Mappings

**Requirement**: SWR_CONFIG_00002
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that exact filename to module mappings work correctly.

**Test Approach**
The test verifies that:
1. Format `filename.c: ModuleName` is recognized
2. Exact filename matching is case-insensitive
3. File extensions are required in mapping
4. Highest priority is given to file mappings

**Expected Behavior**
File mappings provide exact filename matches to module names with highest priority.

**Edge Cases**
- Files in subdirectories (only basename used)
- Case variations in filenames
- Files without extensions
- Duplicate file mappings

---

### SWUT_CONFIG_00004 - Pattern Mappings

**Requirement**: SWR_CONFIG_00003
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that glob pattern to module mappings work correctly.

**Test Approach**
The test verifies that:
1. Format `"pattern*.c": ModuleName` is recognized
2. Glob patterns support wildcards (* and ?)
3. Patterns are compiled to regex for matching
4. First matching pattern wins

**Expected Behavior**
Pattern mappings enable flexible module assignment using glob-style wildcards.

**Edge Cases**
- Patterns with multiple wildcards
- Overlapping patterns
- Patterns matching many files
- Patterns matching no files

---

### SWUT_CONFIG_00005 - Default Module

**Requirement**: SWR_CONFIG_00004
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that default module assignment works for unmapped files.

**Test Approach**
The test verifies that:
1. default_module field is read from YAML
2. Default module is returned when no patterns match
3. Default has lowest priority
4. No default returns None

**Expected Behavior**
Default module provides fallback module assignment for files not matching any pattern.

**Edge Cases**
- No default module specified
- Default module same as mapped module
- All files match patterns (default never used)

---

### SWUT_CONFIG_00006 - Configuration Version

**Requirement**: SWR_CONFIG_00006
**Priority**: Low
**Status**: ✅ Pass

**Description**
Validates that configuration version is tracked for compatibility.

**Test Approach**
The test verifies that:
1. version field is read from YAML
2. Current version is "1.0"
3. Version field is stored for future compatibility checks
4. Missing version is handled gracefully

**Expected Behavior**
Configuration version enables future compatibility checks and format migration.

**Edge Cases**
- Missing version field
- Unsupported version number
- Different version formats

---

## Module Lookup Tests

### SWUT_CONFIG_00007 - Module Lookup

**Requirement**: SWR_CONFIG_00007
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that get_module_for_file method returns correct module for a source file.

**Test Approach**
The test verifies that:
1. Exact file mappings are checked first
2. Pattern mappings are checked in order
3. Default module is returned if no match
4. None is returned if no match and no default
5. Lookup uses only basename (not full path)

**Expected Behavior**
Module lookup follows priority order: exact file → first pattern → default → None.

**Edge Cases**
- Files in deeply nested directories
- Files matching both exact and pattern
- Files matching multiple patterns
- Unmapped files with/without default

---

### SWUT_CONFIG_00008 - Lookup Caching

**Requirement**: SWR_CONFIG_00008
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that lookup results are cached for performance.

**Test Approach**
The test verifies that:
1. First lookup populates cache
2. Second lookup uses cached value
3. Cache key is filename only
4. Cache stores None results for unmapped files

**Expected Behavior**
Module lookups are cached by filename, avoiding repeated pattern matching.

**Edge Cases**
- Cache hit vs cache miss
- Cached None values
- Clearing cache
- Many repeated lookups

---

## Requirements Traceability Matrix

| Requirement ID | Test ID | Status | Notes |
|---------------|-----------|---------|--------|
| SWR_CONFIG_00001 | SWUT_CONFIG_00001 | ✅ Pass | YAML file support |
| SWR_CONFIG_00002 | SWUT_CONFIG_00003 | ✅ Pass | File mappings |
| SWR_CONFIG_00003 | SWUT_CONFIG_00004 | ✅ Pass | Pattern mappings |
| SWR_CONFIG_00004 | SWUT_CONFIG_00005 | ✅ Pass | Default module |
| SWR_CONFIG_00005 | SWUT_CONFIG_00002 | ✅ Pass | Configuration validation |
| SWR_CONFIG_00006 | SWUT_CONFIG_00006 | ✅ Pass | Configuration version |
| SWR_CONFIG_00007 | SWUT_CONFIG_00007 | ✅ Pass | Module lookup |
| SWR_CONFIG_00008 | SWUT_CONFIG_00008 | ✅ Pass | Lookup caching |

## Coverage Summary

- **Total Requirements**: 8
- **Total Tests**: 8
- **Tests Passing**: 8/8 (100%)
- **Code Coverage**: 97%

## Running Tests

```bash
# Run all config tests
pytest tests/unit/test_module_config.py

# Run specific test
pytest tests/unit/test_module_config.py::TestClass::test_SWUT_CONFIG_00001

# Run with coverage
pytest tests/unit/test_module_config.py --cov=autosar_calltree/config --cov-report=term-missing
```

## Change History

| Date | Version | Author | Change Description |
|-------|---------|---------|-------------------|
| 2026-02-11 | 2.0 | Reorganized by requirement structure, removed Test Function labels, using natural language |
| 2026-02-10 | 1.0 | Initial test documentation |
