# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AUTOSAR Call Tree Analyzer is a Python tool that statically analyzes C/AUTOSAR codebases to generate function call trees. It parses automotive embedded code (with AUTOSAR macros like `FUNC`, `VAR`, `P2VAR`) and outputs Mermaid sequence diagrams and XMI/UML 2.5 documents.

**Key capability**: Handles AUTOSAR's proprietary macros that traditional C parsers cannot understand. Use this when working with automotive embedded systems code.

**Latest feature (v0.7.0)**: IBM Rhapsody XMI export for cross-platform compatibility with Rhapsody 8.0+

## Development Commands

```bash
# Installation (development mode with dev dependencies)
pip install -e ".[dev]"

# Run all tests (pytest configured in pyproject.toml)
pytest

# Run specific test module
pytest tests/unit/test_c_parser.py

# Run specific test case
pytest tests/unit/test_c_parser.py::TestCParser::test_function_detection

# Verbose test output with live stdout
pytest -vv -s tests/

# Coverage report (HTML + terminal)
pytest --cov=autosar_calltree --cov-report=html --cov-report=term

# Type checking (mypy configured for strict mode)
mypy src/

# Code formatting (use both for consistency)
black src tests
isort src tests

# Linting (CI uses ruff, isort, flake8, mypy)
ruff check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/

# Build package
python -m build

# Install with pycparser support (optional, for enhanced C parsing)
pip install -e ".[parser]"

# Test CLI entry point
calltree --help
# or
python -m autosar_calltree.cli --help

# Check requirements traceability
python scripts/check_traceability.py
```

## CLI Usage Examples

```bash
# Basic analysis (uses default source dir ./demo)
calltree --start-function Demo_Init --source-dir ./demo

# Use SW module configuration for architecture-level diagrams
calltree --start-function Demo_Init --source-dir demo \
         --module-config demo/module_mapping.yaml \
         --use-module-names \
         --output demo/demo.md

# Control depth and output format
calltree --start-function Demo_Init --max-depth 2 --format xmi --output diagrams/demo.xmi

# Generate Rhapsody-compatible XMI
calltree --start-function Demo_Init --source-dir ./demo --format rhapsody

# Use SW module configuration for architecture-level Rhapsody diagrams
calltree --start-function Demo_Init --source-dir demo \
         --module-config demo/module_mapping.yaml \
         --use-module-names \
         --format rhapsody \
         --output demo/rhapsody_demo.xmi

# Generate both Mermaid and XMI
calltree --start-function Demo_MainFunction --format both --max-depth 4

# List all available functions
calltree --list-functions --source-dir ./demo

# Search for functions by pattern
calltree --search "ADLK" --source-dir ./demo

# Force cache rebuild
calltree ... --rebuild-cache
```

## Architecture

The codebase follows a layered pipeline architecture:

```
Source Files → Parsers → Database → Analyzer → Generator → Output
```

### Core Layers

1. **Parsers** (`src/autosar_calltree/parsers/`)
   - `AutosarParser`: Handles AUTOSAR-specific macros (`FUNC`, `FUNC_P2VAR`, `FUNC_P2CONST`, `VAR`, `P2VAR`, `P2CONST`, etc.)
   - `CParser`: Regex-based fallback for traditional C function declarations; also extracts function calls with conditional context (if/else blocks)
   - `CParserPyCParser` (optional, requires pycparser): AST-based parser using pycparser for more reliable parsing of standard C code
   - **Progressive Enhancement**: Try AUTOSAR parser first, fall back to C parser (regex-based or pycparser-based if installed)
   - Both extract: function signatures, parameters, return types, and function calls within bodies

2. **Database** (`src/autosar_calltree/database/`)
   - `FunctionDatabase`: Scans source directory, parses all files, builds in-memory index
   - Caching layer: Pickle-based (`.cache/function_db.pkl`) with metadata validation for fast reloads
   - `models.py`: Core dataclasses (`FunctionInfo`, `Parameter`, `FunctionCall`, `AnalysisResult`)
   - **Smart Function Lookup**: Critical for resolving multiple function definitions (see below)

3. **Analyzer** (`src/autosar_calltree/analyzers/`)
   - `CallTreeBuilder`: Depth-first traversal from start function, builds directed call graph
   - Detects circular dependencies/recursive calls
   - Respects `max_depth` limits, tracks statistics

4. **Generators** (`src/autosar_calltree/generators/`)
   - `MermaidGenerator`: Creates Markdown with Mermaid sequence diagrams; supports opt/alt/else blocks
   - `XMIGenerator`: Creates XMI/UML 2.5 documents with combined fragments (opt/alt/else)
   - Supports both function-level and module-level diagrams
   - Includes metadata, function tables, text-based trees

5. **CLI** (`src/autosar_calltree/cli/`)
   - Click-based interface with rich console output
   - Entry point: `autosar_calltree.cli:cli`

### Data Flow Example

```python
from autosar_calltree.database.function_database import FunctionDatabase
from autosar_calltree.analyzers.call_tree_builder import CallTreeBuilder
from autosar_calltree.generators.mermaid_generator import MermaidGenerator
from autosar_calltree.config.module_config import ModuleConfig
from pathlib import Path

# 1. Load module configuration (optional)
config = ModuleConfig(Path("demo/module_mapping.yaml"))

# 2. Build database (with caching)
db = FunctionDatabase(source_dir="./demo", module_config=config)
db.build_database(use_cache=True, verbose=True)

# 3. Build call tree
builder = CallTreeBuilder(db)
result = builder.build_tree(
    start_function="Demo_Init",
    max_depth=3,
    include_rte=True
)

# 4. Generate output with module names
generator = MermaidGenerator(use_module_names=True)
generator.generate(result, output_path="call_tree.md")
```

## Critical Implementation Details

### Conditional Function Call Tracking (v0.5.0)

**Feature**: Automatically detects function calls inside `if`/`else` blocks and generates `opt`/`alt`/`else` blocks in output.

**Implementation**:
1. `CParser._extract_function_calls_with_conditional_context()` parses function bodies line-by-line to track if/else nesting
2. Extracts condition text (e.g., `"update_mode == 0x05"`) from if statements
3. `FunctionCall` model has `is_conditional` and `condition` fields
4. `CallTreeNode` has `is_optional` and `condition` fields for opt block generation
5. `MermaidGenerator` and `XMIGenerator` use these fields to generate conditional blocks

**Example**:
```c
// Source code
if (update_mode == 0x05) {
    COM_SendLINMessage(0x456, (uint8*)0x20003000);
}
```

**Generated Mermaid**:
```mermaid
opt update_mode == 0x05
  Demo_Update->>COM_SendLINMessage: call(msg_id, data)
end
```

**Generated XMI**:
```xml
<uml:fragment name="opt" interactionOperator="opt">
  <uml:operand name="update_mode == 0x05">
    <uml:message name="COM_SendLINMessage" ... />
  </uml:operand>
</uml:fragment>
```

### Smart Function Lookup Strategy (CRITICAL)

**Why it's needed**: AUTOSAR codebases often have multiple definitions of the same function (e.g., declarations in headers included in multiple files, plus the actual implementation). The database must select the correct definition to generate accurate cross-module call diagrams.

**Implementation**: `FunctionDatabase._select_best_function_match()` uses a 4-level selection strategy:

1. **Level 1 - Prefer implementations**: Functions with actual function calls (has implementation) over empty declarations
2. **Level 2 - File name heuristics**: Functions from files matching the function name pattern (e.g., `COM_InitCommunication` should be in `communication.c` or `com_*.c`)
3. **Level 3 - Cross-module awareness**: For cross-module calls, avoid functions from the calling file to prevent selecting local declarations
4. **Level 4 - Module preference**: Prefer functions with assigned SW modules over unassigned ones

**Example**: When `Demo_Init` (in demo.c) calls `COM_InitCommunication`, the database must select the implementation from communication.c, not the declaration from demo.c's included header. The smart lookup ensures Mermaid diagrams show `DemoModule->CommunicationModule` instead of `DemoModule->DemoModule`.

### SW Module Configuration System

**Purpose**: Map C source files to SW modules for architecture-level diagrams showing module interactions instead of individual function calls.

**Architecture**:
- `ModuleConfig` class (`config/module_config.py`): Loads YAML, validates, performs lookups
- Supports exact filename mappings and glob patterns
- Lookup results cached for performance
- Module assignment integrated into database building via `FunctionDatabase._add_function()`
- Module information preserved in cache

**YAML Format**:
```yaml
version: "1.0"

file_mappings:
  demo.c: DemoModule

pattern_mappings:
  "hw_*.c": HardwareModule
  "sw_*.c": SoftwareModule
  "communication.c": CommunicationModule

default_module: "Other"
```

**Integration**:
- Functions get `sw_module` field set during database building
- Generators can use module names as participants instead of function names
- CLI option `--use-module-names` enables module-level diagrams
- Function tables include module column

### Cache Loading Progress

**Implementation**: `FunctionDatabase._load_from_cache()` shows file-by-file progress in verbose mode:
```
Loading 4 files from cache...
  [1/4] demo.c: 2 functions
  [2/4] communication.c: 1 functions
  [3/4] hardware.c: 1 functions
  [4/4] software.c: 1 functions
```

**Cache Validation**:
- Metadata-based validation (source directory, file count)
- Graceful fallback to rebuild on cache errors
- Preserves module assignments from cache

### Function Database Indexing

The database maintains three indexes for efficient lookup:

1. **`functions`**: `Dict[str, List[FunctionInfo]]` - Function name to all definitions
   - Key: function name (e.g., "COM_InitCommunication")
   - Value: List of all FunctionInfo objects with that name
   - Used for general lookups, requires smart selection when multiple exist

2. **`qualified_functions`**: `Dict[str, FunctionInfo]` - Qualified name to function
   - Key: "file::function" (e.g., "communication::COM_InitCommunication")
   - Value: Single FunctionInfo object
   - Used for resolving static functions when context file is known

3. **`functions_by_file`**: `Dict[str, List[FunctionInfo]]` - File to functions
   - Key: Full file path
   - Value: All functions defined in that file
   - Used for cache serialization and file-by-file progress

### AUTOSAR Macro Patterns

The parser recognizes these AUTOSAR macros:

```c
// Function declarations
FUNC(void, RTE_CODE) Function_Name(void);
FUNC(Std_ReturnType, RTE_CODE) Com_Test(VAR(uint32, AUTOMATIC) timerId);
STATIC FUNC(uint8, CODE) Internal_Function(void);

// Pointer returns
FUNC_P2VAR(uint8, AUTOMATIC, Demo_VAR) GetBuffer(void);
FUNC_P2CONST(ConfigType, AUTOMATIC, APPL_VAR) GetConfig(void);

// Parameters
VAR(uint32, AUTOMATIC) variable
P2VAR(uint8, AUTOMATIC, APPL_DATA) buffer
P2CONST(ConfigType, AUTOMATIC, APPL_DATA) config
CONST(uint16, AUTOMATIC) constant
```

**Parsing Strategy**:
- AUTOSAR parser uses regex patterns to match macro syntax
- Falls back to C parser for traditional declarations
- C parser filters out C keywords (auto, break, case, char, const, etc.) to avoid false positives

## Code Conventions

- **Type annotations**: Required where practicable (`disallow_untyped_defs = false` in mypy, but aim for full coverage)
- **Dataclasses**: Use for data models (`FunctionInfo`, `Parameter`, `FunctionCall`, etc.)
- **Imports**: Standard library → third-party → local (absolute imports preferred)
- **Line length**: 88 characters (Black default)
- **Paths**: Use `pathlib.Path` objects, convert to `str` only at I/O boundaries
- **Error handling**: Parse errors are logged but don't stop scanning; propagate errors for invalid user input

## Important Patterns

- **Dependency injection**: Components receive dependencies explicitly (e.g., `CallTreeBuilder(db)`)
- **Progressive enhancement**: Try AUTOSAR parser first, fall back to C parser
- **Caching**: Use `use_cache=True` when building database; cache invalidates on source checksum change
- **Stateless builders**: `CallTreeBuilder` is stateless per analysis; pass all dependencies explicitly
- **Requirements traceability**: Each major feature has requirement IDs (SWR_CONFIG_00001, etc.) in code comments and documented in `docs/requirements/`

## Working with AUTOSAR Sources

- Sample AUTOSAR sources should be placed under `demo/` for testing
- Use glob patterns (`*.c`, `*.h`) when scanning; avoid loading everything into memory
- AUTOSAR macros to recognize:
  - `FUNC(void, RTE_CODE) FuncName(void)`
  - `FUNC_P2VAR(uint8, AUTOMATIC, Demo_VAR) GetBuffer(void)`
  - `VAR(uint32, AUTOMATIC) var`, `P2VAR(uint8, AUTOMATIC, APPL_DATA) ptr`
  - `CONST(uint16, AUTOMATIC) constant`

## CI/CD Quality Gates

The CI workflow (`.github/workflows/ci.yml`) runs these checks in sequence:

1. **Quality Checks** (must pass before tests):
   - `ruff check` - Fast Python linting
   - `isort --check-only` - Import sorting verification
   - `flake8` - Style guide enforcement (checks for newlines at EOF, etc.)
   - `mypy` - Static type checking

2. **Tests** (matrix: Python 3.10-3.13):
   - `pytest` with coverage reporting
   - Uploads coverage to Codecov

3. **Requirements Traceability**:
   - Validates all requirements have corresponding tests

**Common CI Issues**:
- Flake8 W292: Missing newline at end of file → Add final newline
- Flake8 W391: Blank line at end of file → Remove trailing blank lines
- Mypy var-annotated: Missing type annotation → Add `: TypeHint` to variable declarations

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual modules
│   ├── test_autosar_parser.py
│   ├── test_c_parser.py
│   ├── test_call_tree_builder.py
│   ├── test_function_database.py
│   ├── test_mermaid_generator.py
│   ├── test_models.py
│   └── test_module_config.py
├── integration/             # End-to-end CLI tests
│   └── test_cli.py
└── conftest.py              # Shared pytest fixtures
```

**Test coverage**: See README.md for current statistics.

## File Locations

- Source code: `src/autosar_calltree/`
- Tests: `tests/`
- Cache: `.cache/function_db.pkl` (in source directory)
- Demo sources: `demo/`
- Module configs: `demo/module_mapping.yaml`
- Requirements: `docs/requirements/`
- Traceability: `docs/TRACEABILITY.md`
- Scripts: `scripts/` (traceability checking, etc.)

## Version History

- **v0.6.1** (2026-02-11): Alternative pycparser-based C parser for more reliable standard C parsing
- **v0.6.0** (2026-02-10): Loop detection and multi-line if condition extraction for complex AUTOSAR code
- **v0.5.0** (2026-02-04): Conditional function call tracking with opt/alt/else blocks
- **v0.4.0**: XMI/UML 2.5 output format implementation
- **v0.3.0**: SW module configuration system

## Optional: pycparser Integration

The project includes an optional pycparser-based C parser (`CParserPyCParser`) that provides more reliable parsing of standard C code through AST analysis.

**Installation**:
```bash
pip install -e ".[parser]"  # Includes pycparser
```

**Benefits over regex-based CParser**:
- More accurate function signature extraction (handles complex types, nested pointers)
- Better const/volatile qualifier preservation
- Reliable parameter parsing for complex declarations
- Fewer false positives from C keywords

**Limitations**:
- Requires pycparser installation (not in core dependencies)
- Does not track conditional/loop context (TODO: `# TODO: Track if/else context` in code)
- Still requires AutosarParser for AUTOSAR macros (pycparser cannot parse them)

**Usage**: The parser is not yet integrated into the main CLI. To use it programmatically:
```python
from autosar_calltree.parsers.c_parser_pycparser import CParserPyCParser

parser = CParserPyCParser()
functions = parser.parse_file(Path("example.c"))
```
