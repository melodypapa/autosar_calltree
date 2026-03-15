# CLI Package Requirements

**Package**: `autosar_calltree.cli`
**Source Files**: `main.py`
**Requirements**: SWR_CLI_00001 - SWR_CLI_00025 (25 requirements)

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

**Required**: Yes (unless using `--list-functions` or `--search`)

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

**Choices**: `mermaid`, `rhapsody`

**Default**: `mermaid`

**Behavior**:
- `mermaid`: Generate Mermaid markdown
- `rhapsody`: Generate Rhapsody XMI 2.1

---

### SWR_CLI_00007 - Cache Options
**Purpose**: Control caching behavior

**Flags**:
- `--cache-dir PATH`: Cache directory
- `--no-cache`: Disable caching
- `--rebuild-cache`: Force cache rebuild

**Implementation**: Cache control in `FunctionDatabase`

---

### SWR_CLI_00008 - Output Format Selection
**Purpose**: Select output format (Mermaid or Rhapsody XMI)

**Flag**: `--format [mermaid|rhapsody]`

**Options**:
- `mermaid`: Generate Mermaid sequence diagram (default)
- `rhapsody`: Generate Rhapsody-compatible XMI 2.1

**Behavior**:
- Default output file: `call_tree.md` for Mermaid
- Default output file: `call_tree.xmi` for Rhapsody
- Use `--output` to specify custom output path

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

## Diagram Feature Options (SWR_CLI_00016 - SWR_CLI_00017)

### SWR_CLI_00016 - Loop Detection Option
**Purpose**: Enable loop detection in call tree

**Flag**: `--enable-loops`

**Default**: False

**Behavior**: Detect for/while loops and generate loop blocks in diagrams

**Implementation**: Passed to `CallTreeBuilder.build_tree()`

---

### SWR_CLI_00017 - Conditional Detection Option
**Purpose**: Enable if/else conditional detection in call tree

**Flag**: `--enable-conditionals`

**Default**: False

**Behavior**: Detect if/else blocks and generate opt/alt blocks in diagrams

**Implementation**: Passed to `CallTreeBuilder.build_tree()`

---

## Rhapsody Options (SWR_CLI_00018 - SWR_CLI_00019)

### SWR_CLI_00018 - Rhapsody Package Path Option
**Purpose**: Specify nested package structure for Rhapsody XMI

**Flag**: `--rhapsody-package-path PATH`

**Default**: None (flat package structure)

**Format**: `Package1/Package2/Package3`

**Behavior**: Creates nested packages in XMI structure

**Implementation**: Passed to `RhapsodyXmiGenerator`

---

### SWR_CLI_00019 - Rhapsody Model Name Option
**Purpose**: Specify custom UML model name for Rhapsody XMI

**Flag**: `--rhapsody-model-name NAME`

**Default**: `CallTree_{root_function}`

**Behavior**: Sets the UML model name in XMI document

**Implementation**: Passed to `RhapsodyXmiGenerator`

---

## Preprocessor Options (SWR_CLI_00020 - SWR_CLI_00023)

### SWR_CLI_00020 - CPP Configuration Option
**Purpose**: Specify C preprocessor configuration

**Flag**: `--cpp-config PATH`

**Default**: None (uses regex-based preprocessing)

**Format**: YAML file with preprocessor settings

**Contents**:
- `command`: CPP executable path
- `include_dirs`: List of -I directories
- `extra_flags`: Additional flags (-D, -std, etc.)
- `enabled`: Enable/disable CPP preprocessing

**Implementation**: Passed to `PreprocessorConfig` and `FunctionDatabase`

---

### SWR_CLI_00021 - Keep Temporary Files Option
**Purpose**: Keep preprocessed files for debugging

**Flag**: `--keep-temp`

**Default**: False (clean up temp files)

**Behavior**: Preserve .i files in temp directory after processing

**Use Case**: Debug preprocessing issues

**Implementation**: Passed to `CPPPreprocessor`

---

### SWR_CLI_00022 - Temporary Directory Option
**Purpose**: Specify custom temp directory for preprocessed files

**Flag**: `--temp-dir PATH`

**Default**: System temp directory with `autosar_prep_` prefix

**Behavior**: Store preprocessed .i files in specified directory

**Implementation**: Passed to `CPPPreprocessor`

---

### SWR_CLI_00023 - Preprocess-Only Option
**Purpose**: Run only preprocessing stage for debugging

**Flag**: `--preprocess-only`

**Default**: False

**Behavior**: Run Stage 1 (preprocessing) only, skip Stage 2 (parsing)

**Use Case**: Debug preprocessing issues without full analysis

**Implementation**: Passed to `FunctionDatabase.build_database()`

---

## Error Handling (SWR_CLI_00024 - SWR_CLI_00025)

### SWR_CLI_00024 - Exit Codes
**Purpose**: Use standard exit codes

**Codes**:
- 0: Success
- 1: Error (missing function, invalid input, etc.)
- 130: Keyboard interrupt (Ctrl+C)

**Implementation**: `sys.exit()` with appropriate code

---

### SWR_CLI_00025 - Error Messages and Interrupt Handling
**Purpose**: Handle errors and interrupts gracefully

**Error Messages**:
- Clear description of error
- Suggestions for resolution
- File/line information when applicable

**Keyboard Interrupt**:
- Cancel current operation
- Show "Interrupted by user" message
- Exit with code 130

**Implementation**: Try-except blocks with detailed error reporting

---

## Summary

**Total Requirements**: 25
**Implementation Status**: ✅ All Implemented

**Package Structure**:
```
autosar_calltree.cli/
└── main.py    # SWR_CLI_00001 - SWR_CLI_00025
```

**Key Features**:
- Click-based command structure
- Multiple output formats (Mermaid, Rhapsody XMI 2.1)
- Configurable caching
- Rich console output
- Function search and listing
- Module configuration support
- Loop and conditional detection options
- Rhapsody-specific options (package path, model name)
- Two-stage preprocessing pipeline with CLI options
- Comprehensive error handling