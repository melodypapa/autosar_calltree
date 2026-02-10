# Database Package Requirements

**Package**: `autosar_calltree.database`
**Source Files**: `models.py`, `function_database.py`
**Requirements**: SWR_DB_00001 - SWR_DB_00035 (35 requirements)

---

## Data Models (SWR_DB_00001 - SWR_DB_00010)

### SWR_DB_00001 - FunctionType Enum
**Purpose**: Enumeration for classifying function types

**Values**:
- `AUTOSAR_FUNC`: Standard AUTOSAR FUNC macros
- `AUTOSAR_FUNC_P2VAR`: Pointer return AUTOSAR functions
- `AUTOSAR_FUNC_P2CONST`: Const pointer return AUTOSAR functions
- `TRADITIONAL_C`: Traditional C function declarations
- `RTE_CALL`: RTE calls
- `UNKNOWN`: Unknown function type

**Implementation**: Python `enum` class in `models.py`

---

### SWR_DB_00002 - Parameter Dataclass
**Purpose**: Model function parameters with type information

**Fields**:
- `name`: Parameter name (str)
- `param_type`: Parameter type (str)
- `is_pointer`: Pointer flag (bool)
- `is_const`: Const flag (bool)
- `memory_class`: AUTOSAR memory class (str, optional)

**Implementation**: `@dataclass` in `models.py`

---

### SWR_DB_00003 - FunctionInfo Dataclass
**Purpose**: Core model for function metadata

**Fields**:
- **Identity**: `name`, `return_type`, `file_path`, `line_number`, `is_static`
- **Type**: `function_type` (FunctionType), `memory_class`, `macro_type`
- **Relationships**: `parameters` (List[Parameter]), `calls` (List[FunctionCall])
- **Disambiguation**: `qualified_name`, `sw_module`

**Methods**:
- `__hash__`: Hash based on qualified_name
- `__eq__`: Equality based on qualified_name
- `is_rte_function`: Check if RTE call

**Implementation**: `@dataclass` in `models.py`

---

### SWR_DB_00004 - FunctionCall Dataclass
**Purpose**: Model function calls with conditional and loop context

**Fields**:
- `name`: Function name (str)
- `is_conditional`: Conditional call flag (bool)
- `condition`: Condition text (str, optional)
- `is_loop`: Loop call flag (bool)
- `loop_condition`: Loop condition text (str, optional)

**Implementation**: `@dataclass` in `models.py`

---

### SWR_DB_00005 - CallTreeNode Dataclass
**Purpose**: Tree structure for call graph traversal

**Fields**:
- `function_info`: Associated FunctionInfo
- `depth`: Depth in call tree (int)
- `children`: List of child nodes
- `parent`: Parent node (optional)
- `is_recursive`: Recursive call flag
- `is_truncated`: Truncation flag (max depth)
- `is_optional`: Optional call flag (for opt blocks)
- `condition`: Condition text (for opt blocks)
- `call_count`: Number of calls

**Methods**:
- `add_child(child)`: Add child node
- `get_all_functions()`: Get all functions in subtree
- `get_max_depth()`: Get maximum depth

**Implementation**: `@dataclass` in `models.py`

---

### SWR_DB_00006 - CircularDependency Dataclass
**Purpose**: Track circular dependencies in call graph

**Fields**:
- `cycle`: List of FunctionInfo in cycle
- `depth`: Depth where cycle detected

**Methods**:
- `__str__`: String representation

**Implementation**: `@dataclass` in `models.py`

---

### SWR_DB_00007 - AnalysisStatistics Dataclass
**Purpose**: Collect statistics about call tree analysis

**Fields**:
- `total_functions`: Total function count
- `unique_functions`: Unique function count
- `max_depth_reached`: Maximum depth
- `total_function_calls`: Total calls
- `static_functions`: Static function count
- `rte_functions`: RTE function count
- `autosar_functions`: AUTOSAR function count
- `circular_dependencies_found`: Circular dependency count

**Methods**:
- `to_dict()`: Convert to dictionary

**Implementation**: `@dataclass` in `models.py`

---

### SWR_DB_00008 - AnalysisResult Dataclass
**Purpose**: Complete result of call tree analysis

**Fields**:
- `root_function`: Root FunctionInfo
- `call_tree`: Root CallTreeNode
- `statistics`: AnalysisStatistics
- `circular_dependencies`: List of CircularDependency
- `errors`: List of error messages
- `timestamp`: Analysis timestamp
- `source_directory`: Source directory path
- `max_depth_limit`: Maximum depth limit

**Methods**:
- `get_all_functions()`: Get all functions in tree
- `has_circular_dependencies()`: Check for circular dependencies

**Implementation**: `@dataclass` in `models.py`

---

### SWR_DB_00009 - Type Hints and Dataclasses
**Purpose**: Consistent type annotations and dataclass usage

**Requirements**:
- All models use `@dataclass` decorator
- Full type annotations on all fields and methods
- Use `typing` module for complex types
- Type aliases for common patterns (e.g., `FunctionDict`)

**Implementation**: Throughout `models.py`

---

### SWR_DB_00010 - Model Validation
**Purpose**: Ensure data integrity in models

**Requirements**:
- Validate required fields
- Validate data types
- Validate invariants (e.g., qualified_name format)

**Implementation**: Post-init validation or Pydantic models

---

## Function Database (SWR_DB_00011 - SWR_DB_00025)

### SWR_DB_00011 - Database Initialization
**Purpose**: Initialize function database with source and cache directories

**Parameters**:
- `source_dir`: Root directory containing source files
- `cache_dir`: Cache directory (optional, default: `.cache` in source_dir)
- `module_config`: Module configuration (optional)

**Implementation**: `FunctionDatabase.__init__()` in `function_database.py`

---

### SWR_DB_00012 - Database Structure
**Purpose**: Maintain three indexes for efficient lookup

**Indexes**:
1. `functions`: Dict[str, List[FunctionInfo]] - by function name
2. `qualified_functions`: Dict[str, FunctionInfo] - by "file::function"
3. `functions_by_file`: Dict[str, List[FunctionInfo]] - by file path

**Implementation**: Instance variables in `FunctionDatabase`

---

### SWR_DB_00013 - Database Building
**Purpose**: Scan source files and build database

**Method**: `build_database(use_cache=True, rebuild_cache=False, verbose=False)`

**Process**:
1. Try load from cache (if enabled)
2. Otherwise, scan and parse all `.c` files
3. Save to cache

**Features**:
- Shows file-by-file progress
- Displays file sizes in human-readable format
- Collects parse errors without failing

**Implementation**: `FunctionDatabase.build_database()`

---

### SWR_DB_00014 - File Parsing
**Purpose**: Parse individual source files and add to database

**Process**:
1. Use C parser (auto-detects pycparser if available)
2. Extract functions (both AUTOSAR and traditional C)
3. Add to database with module assignment

**Implementation**: `FunctionDatabase._parse_file()`

---

### SWR_DB_00015 - Smart Function Lookup
**Purpose**: Select best function from multiple definitions

**Strategy** (4 levels):
1. **Prefer implementations**: Functions with actual calls
2. **File name heuristics**: Function name matches file
3. **Cross-module awareness**: Avoid local declarations
4. **Module preference**: Prefer functions with modules

**Implementation**: `FunctionDatabase._select_best_function_match()`

---

### SWR_DB_00016 - Function Lookup Methods
**Purpose**: Various lookup methods for different use cases

**Methods**:
- `lookup_function(name, context_file)`: Lookup by name
- `get_function_by_qualified_name(qualified_name)`: Lookup by "file::function"
- `get_all_function_names()`: Get all unique names
- `get_functions_in_file(file_path)`: Get functions in file
- `search_functions(pattern)`: Search by pattern

**Implementation**: Multiple methods in `FunctionDatabase`

---

### SWR_DB_00017 - Module Configuration Integration
**Purpose**: Assign SW modules to functions

**Process**:
- Use `module_config.get_module_for_file()` during `_add_function()`
- Track module statistics (functions per module)
- Include module info in cache

**Implementation**: Integration in `FunctionDatabase._add_function()`

---

### SWR_DB_00018 - Cache Management
**Purpose**: Save and load database from cache for performance

**Features**:
- **Metadata**: Timestamp, source directory, file count, parser type
- **Validation**: Check source directory and parser type match
- **Progress**: Show file-by-file loading progress
- **Errors**: Graceful fallback to rebuild on error

**Methods**:
- `_save_to_cache(verbose)`: Save to pickle file
- `_load_from_cache(verbose)`: Load from pickle file
- `clear_cache()`: Delete cache file

**Implementation**: Cache methods in `FunctionDatabase`

---

### SWR_DB_00019 - Cache Invalidation on Parser Change
**Purpose**: Rebuild cache when parser type changes

**Trigger**: `parser_type` mismatch between cache and current
- Old cache: regex parser
- New run: pycparser (or vice versa)

**Implementation**: Check in `_load_from_cache()`

---

### SWR_DB_00020 - Parser Auto-Detection
**Purpose**: Automatically use best available parser

**Logic**:
1. Try import pycparser-based parser
2. If available, use `CParserPyCParser`
3. Otherwise, use regex-based `CParser`

**Implementation**: Import logic in `function_database.py`

---

### SWR_DB_00021 - Database Statistics
**Purpose**: Provide statistics about database

**Returns**:
- Parser type and availability
- Files scanned and functions found
- Unique function names
- Static functions count
- Parse errors
- Module statistics (functions per module)

**Method**: `get_statistics()` in `FunctionDatabase`

---

### SWR_DB_00022 - Parse Error Collection
**Purpose**: Collect parsing errors without failing

**Behavior**:
- Continue processing files on errors
- Store error messages in `parse_errors` list
- Show warnings in verbose mode

**Implementation**: Exception handling in `build_database()`

---

### SWR_DB_00023 - Source File Discovery
**Purpose**: Find all C source files recursively

**Pattern**: `**/*.c` using `Path.rglob()`

**Implementation**: File discovery in `build_database()`

---

### SWR_DB_00024 - Qualified Function Keys
**Purpose**: Support static function disambiguation

**Format**: `"file::function"` (e.g., "demo::Demo_Init")

**Use**: Differentiate static functions with same name in different files

**Implementation**: Key generation in `_add_function()`

---

### SWR_DB_00025 - Human-Readable File Sizes
**Purpose**: Display file sizes in human-readable format

**Formats**:
- Bytes (< 1024)
- KB (>= 1024, < 1M)
- MB (>= 1M)

**Implementation**: `_format_file_size()` helper function

---

## Caching (SWR_DB_00026 - SWR_DB_00030)

### SWR_DB_00026 - Cache Metadata Structure
**Purpose**: Store metadata for cache validation

**Fields**:
- `created_at`: Timestamp
- `source_directory`: Source directory path
- `file_count`: Number of files
- `parser_type`: Parser used (pycparser/regex)

**Implementation**: `@dataclass CacheMetadata` in `function_database.py`

---

### SWR_DB_00027 - Cache Loading Progress
**Purpose**: Show progress when loading from cache

**Format**: `[idx/total] filename: X functions`

**Trigger**: Verbose mode only

**Implementation**: Progress loop in `_load_from_cache()`

---

### SWR_DB_00028 - Cache Status Indication
**Purpose**: Distinguish loading from building

**Messages**:
- "Loading X files from cache..."
- "Building function database from..."

**Implementation**: Status messages in `build_database()`

---

### SWR_DB_00029 - Cache Error Handling
**Purpose**: Handle cache errors gracefully

**Behavior**:
- Return False on load error
- Rebuild database on failure
- Show warning in verbose mode

**Implementation**: Try-except in `_load_from_cache()`

---

### SWR_DB_00030 - Cache Performance
**Purpose**: Minimize overhead of caching

**Requirements**:
- Minimal overhead for progress reporting
- Only show progress in verbose mode
- Efficient serialization with pickle

**Implementation**: Optimized caching logic

---

## Parser Integration (SWR_DB_00031 - SWR_DB_00035)

### SWR_DB_00031 - pycparser Integration
**Purpose**: Optional integration of pycparser for better C parsing

**Install**: `pip install -e ".[parser]"`

**Benefits**:
- Handles complex declarations correctly
- Function pointers, arrays, nested pointers
- More reliable than regex

**Implementation**: Auto-detect in `FunctionDatabase.__init__()`

---

### SWR_DB_00032 - AUTOSAR Macro Support
**Purpose**: Parse AUTOSAR-specific macros

**Macros**:
- `FUNC(return_type, class)`
- `FUNC_P2VAR(...)`, `FUNC_P2CONST(...)`
- `VAR(...)`, `P2VAR(...)`, `P2CONST(...)`, `CONST(...)`

**Implementation**: `AutosarParser` used by both C parsers

---

### SWR_DB_00033 - Hybrid Parsing Strategy
**Purpose**: Handle both AUTOSAR and traditional C

**Process**:
1. Parse AUTOSAR functions using `AutosarParser`
2. Parse traditional C using `CParser` or `CParserPyCParser`
3. Merge results, avoiding duplicates

**Implementation**: Logic in both C parsers

---

### SWR_DB_00034 - Deduplication
**Purpose**: Avoid duplicate function entries

**Method**: Track (name, line_number) tuples

**Implementation**: Deduplication in C parsers

---

### SWR_DB_00035 - Function Body Extraction
**Purpose**: Extract function bodies to find calls

**Requirements**:
- Handle nested braces correctly
- Track if/else context for conditional calls
- Track loop context for loop detection

**Implementation**: Function body extraction in both C parsers

---

## Summary

**Total Requirements**: 35
**Implementation Status**: ✅ All Implemented

**Package Structure**:
```
autosar_calltree.database/
├── models.py              # SWR_DB_00001 - SWR_DB_00010 (Data Models)
└── function_database.py   # SWR_DB_00011 - SWR_DB_00035 (Database + Caching + Parser Integration)
```
