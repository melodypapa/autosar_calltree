# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AUTOSAR Call Tree Analyzer is a Python tool that statically analyzes C/AUTOSAR codebases to generate function call trees. It parses automotive embedded code (with AUTOSAR macros like `FUNC`, `VAR`, `P2VAR`) and outputs Mermaid sequence diagrams.

**Key capability**: Handles AUTOSAR's proprietary macros that traditional C parsers cannot understand. Use this when working with automotive embedded systems code.

## Development Commands

```bash
# Installation (development mode with dev dependencies)
pip install -e ".[dev]"

# Run all tests (pytest configured in pyproject.toml)
pytest

# Run specific test module
pytest tests/test_parser.py

# Run specific test case
pytest tests/test_parser.py::TestParser::test_function_detection

# Verbose test output with live stdout
pytest -vv -s tests/

# Coverage report (HTML + terminal)
pytest --cov=autosar_calltree --cov-report=html --cov-report=term

# Type checking (mypy configured for strict mode)
mypy src/

# Code formatting
black src tests
isort src tests

# Linting
flake8 src tests

# Build package
python -m build

# Test CLI entry point
calltree --help
# or
python -m autosar_calltree.cli --help
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
   - `CParser`: Fallback for traditional C function declarations
   - Both extract: function signatures, parameters, return types, and function calls within bodies
   - **Progressive Enhancement**: Try AUTOSAR parser first, fall back to C parser

2. **Database** (`src/autosar_calltree/database/`)
   - `FunctionDatabase`: Scans source directory, parses all files, builds in-memory index
   - Caching layer: Pickle-based (`.cache/function_db.pkl`) with metadata validation for fast reloads
   - `models.py`: Core dataclasses (`FunctionInfo`, `Parameter`, `AnalysisResult`)
   - **Smart Function Lookup**: Critical for resolving multiple function definitions (see below)

3. **Analyzer** (`src/autosar_calltree/analyzers/`)
   - `CallTreeBuilder`: Depth-first traversal from start function, builds directed call graph
   - Detects circular dependencies/recursive calls
   - Respects `max_depth` limits, tracks statistics

4. **Generators** (`src/autosar_calltree/generators/`)
   - `MermaidGenerator`: Creates Markdown with Mermaid sequence diagrams
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
- MermaidGenerator can use module names as participants instead of function names
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

- **Type annotations**: Required everywhere (`disallow_untyped_defs = true` in mypy)
- **Dataclasses**: Use for data models (`FunctionInfo`, `Parameter`, etc.)
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

## Known Limitations

- XMI output format is not yet implemented (CLI shows warning)
- No test files exist yet in `tests/` directory
- Large source trees (thousands of files) may need performance optimization

## File Locations

- Source code: `src/autosar_calltree/`
- Tests: `tests/` (currently empty)
- Cache: `.cache/function_db.pkl` (in source directory)
- Demo sources: `demo/`
- Module configs: `demo/module_mapping.yaml`
- Requirements: `docs/requirements/`
- Traceability: `docs/TRACEABILITY.md`
