# CLI Requirements

## Module: Command-Line Interface

**Author:** Claude
**Date:** 2026-01-30
**Version:** 1.0
**Status:** Final

---

## SWR_CLI_00001: Command Structure and Entry Point

**Priority:** High
**Status:** Implemented

**Description:**
The CLI shall provide a Click-based command entry point that accepts analysis commands, list functions, and search operations.

**Rationale:**
Users need a single, intuitive command interface to access all analyzer functionality.

**Verification:**
- CLI entry point exists in `src/autosar_calltree/cli/main.py`
- Command accepts analysis, list, and search modes
- Click decorators properly configured

---

## SWR_CLI_00002: Start Function Option

**Priority:** High
**Status:** Implemented

**Description:**
The CLI shall provide a `--start-function` / `-s` option to specify the root function for call tree analysis.

**Requirements:**
- Optional parameter (not required for --list-functions or --search)
- Accepts function name as string
- Required for analysis mode

**Rationale:**
Users must specify which function to use as the root of the call tree.

**Verification:**
- Option accepts function name
- Validation error when missing in analysis mode
- Error message suggests --list-functions

---

## SWR_CLI_00003: Source Directory Option

**Priority:** High
**Status:** Implemented

**Description:**
The CLI shall provide a `--source-dir` / `-i` option to specify the C source directory for analysis.

**Requirements:**
- Default value: `./demo`
- Must exist and be a directory
- Path validation by Click

**Rationale:**
Users need to specify which codebase to analyze.

**Verification:**
- Default points to ./demo
- Click validates directory existence
- Error on non-existent paths

---

## SWR_CLI_00004: Output Path Option

**Priority:** Medium
**Status:** Implemented

**Description:**
The CLI shall provide an `--output` / `-o` option to specify the output file path.

**Requirements:**
- Default value: `call_tree.md`
- Accepts any file path
- Creates/overwrites output file

**Rationale:**
Users need control over where generated diagrams are saved.

**Verification:**
- Default is call_tree.md
- Custom paths accepted
- File created successfully

---

## SWR_CLI_00005: Max Depth Option

**Priority:** Medium
**Status:** Implemented

**Description:**
The CLI shall provide a `--max-depth` / `-d` option to control traversal depth.

**Requirements:**
- Default value: 3
- Accepts positive integer
- Passed to CallTreeBuilder

**Rationale:**
Users need to limit call tree depth to manage complexity.

**Verification:**
- Default is 3
- Integer validation
- Depth limit enforced in analysis

---

## SWR_CLI_00006: Output Format Option

**Priority:** Medium
**Status:** Partially Implemented

**Description:**
The CLI shall provide a `--format` / `-f` option to select output format.

**Requirements:**
- Choices: "mermaid", "xmi", "both"
- Default: "mermaid"
- Case-insensitive matching
- XMI shows warning (not yet implemented)

**Rationale:**
Users need to choose between Mermaid diagrams and XMI output.

**Verification:**
- Accepts valid choices
- Default is mermaid
- XMI shows warning
- Both generates .mermaid.md file

---

## SWR_CLI_00007: Cache Options

**Priority:** Medium
**Status:** Implemented

**Description:**
The CLI shall provide cache control options: `--cache-dir`, `--no-cache`, and `--rebuild-cache`.

**Requirements:**
- `--cache-dir`: Optional custom cache directory
- `--no-cache`: Disable cache usage
- `--rebuild-cache`: Force cache rebuild
- Default: <source-dir>/.cache

**Rationale:**
Users need control over caching for performance vs. freshness.

**Verification:**
- Custom cache directory supported
- --no-cache disables caching
- --rebuild-cache forces rebuild
- Defaults to source/.cache

---

## SWR_CLI_00008: Verbose Output

**Priority:** Low
**Status:** Implemented

**Description:**
The CLI shall provide a `--verbose` / `-v` flag for detailed output.

**Requirements:**
- Shows database statistics
- Shows module distribution
- Shows configuration details
- Shows file-by-file progress

**Rationale:**
Users need detailed feedback for debugging and understanding analysis progress.

**Verification:**
- Statistics table printed
- Module distribution shown
- Configuration details displayed
- Progress shown per file

---

## SWR_CLI_00009: List Functions Command

**Priority:** High
**Status:** Implemented

**Description:**
The CLI shall provide a `--list-functions` / `-l` flag to list all available functions.

**Requirements:**
- Lists all unique function names
- Shows total count
- Numbered list format
- Exits after listing (no analysis)

**Rationale:**
Users need to discover available functions before starting analysis.

**Verification:**
- Lists all function names
- Numbered 1..N
- Shows total count
- No analysis performed

---

## SWR_CLI_00010: Search Functions Command

**Priority:** Medium
**Status:** Implemented

**Description:**
The CLI shall provide a `--search` option to find functions matching a pattern.

**Requirements:**
- Accepts search pattern string
- Shows function name and file location
- Shows match count
- "No matches found" message if empty

**Rationale:**
Users need to find specific functions by name pattern.

**Verification:**
- Pattern matching works
- File locations shown (file:line)
- Match count displayed
- Empty results handled

---

## SWR_CLI_00011: Module Configuration Options

**Priority:** Medium
**Status:** Implemented

**Description:**
The CLI shall provide `--module-config` and `--use-module-names` options for module-level diagrams.

**Requirements:**
- `--module-config`: Path to YAML config file
- `--use-module-names`: Enable module names as participants
- Warning if --use-module-names without --module-config
- Config validation and error handling

**Rationale:**
Users need to generate architecture-level diagrams showing SW module interactions.

**Verification:**
- YAML config loaded successfully
- Module names used in diagrams
- Warning shown for missing config
- Config errors handled gracefully

---

## SWR_CLI_00012: RTE Abbreviation Control

**Priority:** Low
**Status:** Implemented

**Description:**
The CLI shall provide a `--no-abbreviate-rte` flag to disable RTE function name abbreviation.

**Requirements:**
- Default: abbreviate RTE names
- Flag preserves full RTE names
- Passed to MermaidGenerator

**Rationale:**
Some users prefer full RTE names for clarity over abbreviated names.

**Verification:**
- Default abbreviates RTE names
- Flag preserves full names
- Generator respects setting

---

## SWR_CLI_00013: Rich Console Output

**Priority:** Medium
**Status:** Implemented

**Description:**
The CLI shall use Rich library for formatted console output with colors, tables, and progress indicators.

**Requirements:**
- Colored output (cyan, green, yellow, red, bold)
- Progress spinners for long operations
- Tables for statistics display
- Clean, professional appearance

**Rationale:**
Rich output improves user experience and makes the tool more professional.

**Verification:**
- Colors used appropriately
- Progress spinners shown
- Statistics in table format
- Professional appearance

---

## SWR_CLI_00014: Error Handling and Exit Codes

**Priority:** High
**Status:** Implemented

**Description:**
The CLI shall provide comprehensive error handling with appropriate exit codes.

**Requirements:**
- Exit code 0: Success
- Exit code 1: Error (missing function, config error, analysis error)
- Exit code 130: Keyboard interrupt
- Clear error messages
- Exception handling with traceback in verbose mode

**Rationale:**
Users need clear feedback on failures and proper exit codes for scripting.

**Verification:**
- Success exits with 0
- Errors exit with 1
- Ctrl+C exits with 130
- Error messages are clear
- Traceback in verbose mode

---

## Revision History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-01-30 | 1.0 | Claude | Initial CLI requirements specification |
