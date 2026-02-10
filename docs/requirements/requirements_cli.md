# CLI Package Requirements

**Package**: `autosar_calltree.cli`
**Source Files**: `main.py`
**Requirements**: SWR_CLI_00001 - SWR_CLI_00015 (15 requirements)

---

## Overview

The CLI package provides a command-line interface for the AUTOSAR Call Tree Analyzer, using Click for command definition and Rich for enhanced console output.

**Entry Point**: `autosar_calltree.cli:cli`

---

## Command Structure (SWR_CLI_00001 - SWR_CLI_00003)

### SWR_CLI_00001 - Click-Based Command Structure
**Purpose**: Use Click framework for CLI

**Framework**: Click library

**Entry Point**: `@click.command()` decorator

**Implementation**: `cli()` function in `main.py`

---

### SWR_CLI_00002 - Start Function Option
**Purpose**: Specify root function for call tree

**Flag**: `--start-function` / `-s`

**Required**: Yes

**Validation**: Function must exist in database

**Error**: Exit with error code 1 if not found

---

### SWR_CLI_00003 - Source Directory Option
**Purpose**: Specify source code directory

**Flag**: `--source-dir` / `-i`

**Default**: `./demo`

**Validation**: Directory must exist

---

## Output Options (SWR_CLI_00004 - SWR_CLI_00008)

### SWR_CLI_00004 - Output Path Option
**Purpose**: Specify output file path

**Flag**: `--output` / `-o`

**Default**: `call_tree.md`

**Behavior**: Create/overwrite file at specified path

---

### SWR_CLI_00005 - Max Depth Option
**Purpose**: Limit traversal depth

**Flag**: `--max-depth` / `-d`

**Default**: 3

**Validation**: Must be positive integer

**Use**: Stop traversal at specified depth

---

### SWR_CLI_00006 - Output Format Option
**Purpose**: Specify output format

**Flag**: `--format` / `-f`

**Choices**: `mermaid`, `xmi`, `both`

**Default**: `mermaid`

**Behavior**:
- `mermaid`: Generate Mermaid markdown
- `xmi`: Generate XMI file
- `both`: Generate both formats

---

### SWR_CLI_00007 - Cache Options
**Purpose**: Control caching behavior

**Flags**:
- `--cache-dir PATH`: Cache directory
- `--no-cache`: Disable caching
- `--rebuild-cache`: Force cache rebuild

**Implementation**: Cache control in `FunctionDatabase`

---

### SWR_CLI_00008 - Multiple Output Files
**Purpose**: Handle multiple output files with `--format both`

**Behavior**:
- Generate `.md` file for Mermaid
- Generate `.xmi` file for XMI
- Use `--output` as base name

---

## Display Options (SWR_CLI_00009 - SWR_CLI_00012)

### SWR_CLI_00009 - Verbose Output
**Purpose**: Enable detailed progress messages

**Flag**: `--verbose` / `-v`

**Shows**:
- Parser type being used
- File-by-file processing progress
- Statistics
- Warnings and errors

---

### SWR_CLI_00010 - List Functions Command
**Purpose**: List all available functions

**Flag**: `--list-functions` / `-l`

**Output**: Table with:
- Function name
- File name
- Module (if configured)
- Line number

**Behavior**: Exit after listing (no analysis)

---

### SWR_CLI_00011 - Search Functions Command
**Purpose**: Search for functions by pattern

**Flag**: `--search PATTERN`

**Output**: Table of matching functions

**Behavior**: Exit after searching (no analysis)

---

### SWR_CLI_00012 - Rich Console Output
**Purpose**: Use Rich library for enhanced output

**Features**:
- Colored text
- Progress bars
- Tables with formatting
- Panel/box drawing

**Implementation**: Rich console in CLI

---

## Module Configuration (SWR_CLI_00013 - SWR_CLI_00015)

### SWR_CLI_00013 - Module Configuration Options
**Purpose**: Support SW module mapping

**Flags**:
- `--module-config PATH`: YAML config file
- `--use-module-names`: Use modules as participants

**Integration**: Pass to `ModuleConfig` and generators

---

### SWR_CLI_00014 - RTE Abbreviation Control
**Purpose**: Control RTE name abbreviation

**Flag**: `--no-abbreviate-rte`

**Default**: Abbreviate (e.g., `Rte_Call` → `Rte`)

**Behavior**: Show full RTE names when flag set

---

### SWR_CLI_00015 - Parameter Display Control
**Purpose**: Control parameter display in diagrams

**Default**: Show parameters

**Future Enhancement**: `--hide-parameters` flag

**Implementation**: Pass to generators

---

## Error Handling (SWR_CLI_00016 - SWR_CLI_00018)

### SWR_CLI_00016 - Exit Codes
**Purpose**: Use standard exit codes

**Codes**:
- 0: Success
- 1: Error (missing function, invalid input, etc.)
- 130: Keyboard interrupt (Ctrl+C)

**Implementation**: `sys.exit()` with appropriate code

---

### SWR_CLI_00017 - Error Messages
**Purpose**: Show user-friendly error messages

**Messages**:
- Clear description of error
- Suggestions for resolution
- File/line information when applicable

**Implementation**: Try-except with detailed error reporting

---

### SWR_CLI_00018 - Keyboard Interrupt Handling
**Purpose**: Handle Ctrl+C gracefully

**Behavior**:
- Cancel current operation
- Show "Interrupted by user" message
- Exit with code 130

**Implementation**: Try-except for `KeyboardInterrupt`

---

## Summary

**Total Requirements**: 18
**Implementation Status**: ✅ All Implemented

**Package Structure**:
```
autosar_calltree.cli/
└── main.py    # SWR_CLI_00001 - SWR_CLI_00018
```

**Key Features**:
- Click-based command structure
- Multiple output formats (Mermaid, XMI, both)
- Configurable caching
- Rich console output
- Function search and listing
- Module configuration support
- Comprehensive error handling
