# CLI Package Test Cases

## Overview

This document describes test cases for the CLI package, organized by requirement structure.

**Requirements Document**: [requirements_cli.md](../requirements/requirements_cli.md)

**Package**: `autosar_calltree.cli`
**Source Files**: `main.py`
**Requirement IDs**: SWR_CLI_00001 - SWR_CLI_00018
**Coverage**: ~90%

---

## Command Structure Tests

### SWUT_CLI_00001 - Click-Based Command Structure

**Requirement**: SWR_CLI_00001
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that Click framework is used for CLI command structure.

**Test Approach**
The test verifies that:
1. @click.command() decorator is used
2. Entry point is registered correctly
3. Command can be invoked
4. Help text is available

**Expected Behavior**
CLI is built with Click framework providing command-line interface.

**Edge Cases**
- Command invocation without arguments
- Help command
- Version command

---

### SWUT_CLI_00002 - Start Function Option

**Requirement**: SWR_CLI_00002
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that --start-function option specifies root function for call tree.

**Test Approach**
The test verifies that:
1. --start-function or -s flag is recognized
2. Option is required (error if missing)
3. Function name is passed to analysis
4. Validation checks function exists in database

**Expected Behavior**
Start function option specifies the root function for call tree analysis.

**Edge Cases**
- Function not found in database
- Multiple definitions of function
- Case sensitivity
- Empty function name

---

### SWUT_CLI_00003 - Source Directory Option

**Requirement**: SWR_CLI_00003
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that --source-dir option specifies source code directory.

**Test Approach**
The test verifies that:
1. --source-dir or -i flag is recognized
2. Default value is ./demo
3. Directory existence is validated
4. Path is passed to database builder

**Expected Behavior**
Source directory option points to the C source code directory for analysis.

**Edge Cases**
- Directory doesn't exist
- Relative vs absolute paths
- Paths with spaces
- Empty directory

---

## Output Options Tests

### SWUT_CLI_00004 - Output Path Option

**Requirement**: SWR_CLI_00004
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that --output option specifies output file path.

**Test Approach**
The test verifies that:
1. --output or -o flag is recognized
2. Default value is call_tree.md
3. File can be created/overwritten
4. Path is passed to generator

**Expected Behavior**
Output path option determines where generated diagram is written.

**Edge Cases**
- Invalid path (directory doesn't exist)
- Read-only location
- Path with spaces
- Existing file (overwrite)

---

### SWUT_CLI_00005 - Max Depth Option

**Requirement**: SWR_CLI_00005
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that --max-depth option limits traversal depth.

**Test Approach**
The test verifies that:
1. --max-depth or -d flag is recognized
2. Default value is 3
3. Value must be positive integer
4. Depth limit is passed to analyzer

**Expected Behavior**
Max depth option controls how deep the call tree traversal goes.

**Edge Cases**
- Negative values (rejected)
- Zero value (root only)
- Very large values (100+)
- Non-integer values

---

### SWUT_CLI_00006 - Output Format Option

**Requirement**: SWR_CLI_00006
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that --format option selects output format.

**Test Approach**
The test verifies that:
1. --format or -f flag is recognized
2. Choices are: mermaid, xmi, both
3. Default is mermaid
4. Format determines generator selection

**Expected Behavior**
Output format option selects Mermaid, XMI, or both output types.

**Edge Cases**
- Invalid format (rejected)
- Both format creates two files
- Case sensitivity

---

### SWUT_CLI_00007 - Cache Options

**Requirement**: SWR_CLI_00007
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that cache behavior can be controlled via CLI options.

**Test Approach**
The test verifies that:
1. --cache-dir PATH sets cache location
2. --no-cache disables caching
3. --rebuild-cache forces cache rebuild
4. Options are passed to database correctly

**Expected Behavior**
Cache options provide fine-grained control over caching behavior.

**Edge Cases**
- Invalid cache path
- Read-only cache directory
- Multiple cache options together
- Cache directory creation

---

### SWUT_CLI_00008 - Multiple Output Files

**Requirement**: SWR_CLI_00008
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that --format both generates multiple output files.

**Test Approach**
The test verifies that:
1. Format "both" generates .md and .xmi files
2. --output path is used as base name
3. Both files are created successfully
4. File extensions are correct

**Expected Behavior**
Both output format generates Mermaid markdown and XMI files from base output name.

**Edge Cases**
- Output path with existing extension
- Both generators failing
- Partial success (one file created)

---

## Display Options Tests

### SWUT_CLI_00009 - Verbose Output

**Requirement**: SWR_CLI_00009
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that --verbose option enables detailed progress messages.

**Test Approach**
The test verifies that:
1. --verbose or -v flag is recognized
2. Parser type is shown
3. File-by-file processing progress is displayed
4. Statistics and warnings are printed

**Expected Behavior**
Verbose mode provides detailed feedback during CLI execution.

**Edge Cases**
- Verbose mode off (minimal output)
- Very large codebases (many progress messages)
- Progress bar vs text output

---

### SWUT_CLI_00010 - List Functions Command

**Requirement**: SWR_CLI_00010
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that --list-functions option lists all available functions.

**Test Approach**
The test verifies that:
1. --list-functions or -l flag triggers function listing
2. Table shows: Function name, File, Module, Line
3. All functions from database are listed
4. CLI exits after listing (no analysis)

**Expected Behavior**
List functions command displays all discovered functions in a formatted table.

**Edge Cases**
- Empty database (no functions)
- Very many functions (100+)
- Functions without modules
- Very long function names

---

### SWUT_CLI_00011 - Search Functions Command

**Requirement**: SWR_CLI_00011
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that --search option finds functions by pattern.

**Test Approach**
The test verifies that:
1. --search PATTERN triggers search mode
2. Pattern matching is case-insensitive
3. Matching functions are displayed in table
4. CLI exits after search (no analysis)

**Expected Behavior**
Search functions command filters functions by substring pattern.

**Edge Cases**
- Empty search pattern
- Pattern matching no functions
- Pattern matching many functions
- Special characters in pattern

---

### SWUT_CLI_00012 - Rich Console Output

**Requirement**: SWR_CLI_00012
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that Rich library provides enhanced console output.

**Test Approach**
The test verifies that:
1. Colored text is used for emphasis
2. Progress bars show during analysis
3. Tables are formatted with Rich
4. Panel/box drawing is used for sections

**Expected Behavior**
Rich console provides user-friendly formatted output with colors and tables.

**Edge Cases**
- Output redirection (no colors)
- Very narrow terminals
- Very wide tables
- Unicode vs ASCII fallback

---

## Module Configuration Tests

### SWUT_CLI_00013 - Module Configuration Options

**Requirement**: SWR_CLI_00013
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that module configuration is supported via CLI options.

**Test Approach**
The test verifies that:
1. --module-config PATH loads YAML configuration
2. --use-module-names enables module participants
3. Configuration is passed to database and generators
4. Missing config file is handled

**Expected Behavior**
Module configuration options enable SW module mapping and module-level diagrams.

**Edge Cases**
- Config file doesn't exist
- Invalid YAML format
- Module config without --use-module-names
- Module names not found in config

---

### SWUT_CLI_00014 - RTE Abbreviation Control

**Requirement**: SWR_CLI_00014
**Priority**: Low
**Status**: ✅ Pass

**Description**
Validates that --no-abbreviate-rte controls RTE name abbreviation.

**Test Approach**
The test verifies that:
1. Default behavior abbreviates long RTE names
2. --no-abbreviate-rte shows full RTE names
3. Option is passed to generators
4. Abbreviation format is Rte_Operation_XXX

**Expected Behavior**
RTE abbreviation option controls whether long RTE function names are shortened.

**Edge Cases**
- Short RTE names (no abbreviation needed)
- Non-RTE functions (unaffected)
- Custom abbreviation patterns

---

### SWUT_CLI_00015 - Parameter Display Control

**Requirement**: SWR_CLI_00015
**Priority**: Low
**Status**: ✅ Pass

**Description**
Validates that parameter display in diagrams can be controlled.

**Test Approach**
The test verifies that:
1. Parameters are shown by default
2. Option can disable parameter display
3. Setting is passed to generators
4. Diagrams respect the setting

**Expected Behavior**
Parameter display option controls whether function parameters appear on diagram arrows.

**Edge Cases**
- Functions with no parameters (unaffected)
- Very long parameter lists
- Mixed parameter usage

---

## Error Handling Tests

### SWUT_CLI_00016 - Exit Codes

**Requirement**: SWR_CLI_00016
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that standard exit codes are used for different scenarios.

**Test Approach**
The test verifies that:
1. Success exits with code 0
2. Errors exit with code 1
3. Ctrl+C exits with code 130
4. sys.exit() is used correctly

**Expected Behavior**
CLI uses standard exit codes to indicate success, errors, or interruption.

**Edge Cases**
- Multiple error types
- Error during cleanup
- Signal handlers

---

### SWUT_CLI_00017 - Error Messages

**Requirement**: SWR_CLI_00017
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that user-friendly error messages are shown.

**Test Approach**
The test verifies that:
1. Errors describe what went wrong
2. Suggestions for resolution are provided
3. File/line information included when applicable
4. Rich formatting highlights errors

**Expected Behavior**
Error messages provide clear, actionable information to users.

**Edge Cases**
- Missing required options
- Invalid file paths
- Parse errors
- Runtime errors

---

### SWUT_CLI_00018 - Keyboard Interrupt Handling

**Requirement**: SWR_CLI_00018
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that Ctrl+C is handled gracefully.

**Test Approach**
The test verifies that:
1. KeyboardInterrupt exception is caught
2. "Interrupted by user" message is shown
3. Exit code 130 is used
4. Partial cleanup occurs if possible

**Expected Behavior**
Keyboard interrupts are handled gracefully with user-friendly message.

**Edge Cases**
- Interrupt during file parsing
- Interrupt during output generation
- Multiple interrupts
- Interrupt during cleanup

---

## Requirements Traceability Matrix

| Requirement ID | Test ID | Status | Notes |
|---------------|-----------|---------|--------|
| SWR_CLI_00001 | SWUT_CLI_00001 | ✅ Pass | Click-based structure |
| SWR_CLI_00002 | SWUT_CLI_00002 | ✅ Pass | Start function option |
| SWR_CLI_00003 | SWUT_CLI_00003 | ✅ Pass | Source directory option |
| SWR_CLI_00004 | SWUT_CLI_00004 | ✅ Pass | Output path option |
| SWR_CLI_00005 | SWUT_CLI_00005 | ✅ Pass | Max depth option |
| SWR_CLI_00006 | SWUT_CLI_00006 | ✅ Pass | Output format option |
| SWR_CLI_00007 | SWUT_CLI_00007 | ✅ Pass | Cache options |
| SWR_CLI_00008 | SWUT_CLI_00008 | ✅ Pass | Multiple output files |
| SWR_CLI_00009 | SWUT_CLI_00009 | ✅ Pass | Verbose output |
| SWR_CLI_00010 | SWUT_CLI_00010 | ✅ Pass | List functions command |
| SWR_CLI_00011 | SWUT_CLI_00011 | ✅ Pass | Search functions command |
| SWR_CLI_00012 | SWUT_CLI_00012 | ✅ Pass | Rich console output |
| SWR_CLI_00013 | SWUT_CLI_00013 | ✅ Pass | Module configuration options |
| SWR_CLI_00014 | SWUT_CLI_00014 | ✅ Pass | RTE abbreviation control |
| SWR_CLI_00015 | SWUT_CLI_00015 | ✅ Pass | Parameter display control |
| SWR_CLI_00016 | SWUT_CLI_00016 | ✅ Pass | Exit codes |
| SWR_CLI_00017 | SWUT_CLI_00017 | ✅ Pass | Error messages |
| SWR_CLI_00018 | SWUT_CLI_00018 | ✅ Pass | Keyboard interrupt handling |

## Coverage Summary

- **Total Requirements**: 18
- **Total Tests**: 18
- **Tests Passing**: 18/18 (100%)
- **Code Coverage**: ~90%

## Running Tests

```bash
# Run all CLI tests
pytest tests/integration/test_cli.py

# Run specific test
pytest tests/integration/test_cli.py::TestClass::test_SWUT_CLI_00001

# Run with coverage
pytest tests/integration/test_cli.py --cov=autosar_calltree/cli --cov-report=term-missing
```

## Change History

| Date | Version | Author | Change Description |
|-------|---------|---------|-------------------|
| 2026-02-11 | 2.0 | Reorganized by requirement structure, removed Test Function labels, using natural language |
| 2026-02-10 | 1.0 | Initial test documentation |
