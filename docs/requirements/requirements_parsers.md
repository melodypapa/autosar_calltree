# Parsers Package Requirements

**Package**: `autosar_calltree.parsers`
**Source Files**: `autosar_parser.py`, `c_parser.py`, `c_parser_pycparser.py`
**Requirements**: SWR_PARSER_00001 - SWR_PARSER_00040 (40 requirements)

---

## Overview

The parsers package provides functionality for parsing C and AUTOSAR source code to extract function definitions, parameters, and call relationships.

**Three Parser Implementations**:
1. `AutosarParser` - AUTOSAR macro-specific parser
2. `CParser` - Regex-based traditional C parser with AUTOSAR fallback
3. `CParserPyCParser` - pycparser-based AST parser with AUTOSAR fallback

**Selection Logic**: `FunctionDatabase` auto-detects and uses the best available parser.

---

## AUTOSAR Parser (SWR_PARSER_00001 - SWR_PARSER_00010)

### SWR_PARSER_00001 - AUTOSAR Macro Recognition
**Purpose**: Recognize and parse AUTOSAR function macros

**Supported Macros**:
- `FUNC(return_type, memory_class) function_name(params)`
- `FUNC_P2VAR(return_type, ptr_class, mem_class) function_name(params)`
- `FUNC_P2CONST(return_type, ptr_class, mem_class) function_name(params)`
- `STATIC FUNC(...)`
- `STATIC FUNC_P2VAR(...)`
- `STATIC FUNC_P2CONST(...)`

**Implementation**: Regex patterns in `AutosarParser`

---

### SWR_PARSER_00002 - AUTOSAR Parameter Macros
**Purpose**: Parse AUTOSAR parameter macros

**Supported Macros**:
- `VAR(type, memory_class) name`
- `P2VAR(type, ptr_class, mem_class) name` (pointer)
- `P2CONST(type, ptr_class, mem_class) name` (const pointer)
- `CONST(type, mem_class) name` (const)

**Data Extracted**:
- Parameter type
- Parameter name
- Pointer flag (for P2VAR/P2CONST)
- Const flag (for P2CONST/CONST)

**Implementation**: Parameter regex patterns in `AutosarParser`

---

### SWR_PARSER_00003 - Parameter String Extraction
**Purpose**: Extract parameter list from function declaration

**Challenge**: Handle nested parentheses

**Implementation**: Balanced parenthesis counting

---

### SWR_PARSER_00004 - Parameter List Splitting
**Purpose**: Split parameters by comma

**Challenge**: Respect nested parentheses

**Implementation**: Smart split with depth tracking

---

### SWR_PARSER_00005 - Function Declaration Parsing
**Purpose**: Parse AUTOSAR function declaration into FunctionInfo

**Input**: Line of source code
**Output**: `FunctionInfo` object

**Fields Populated**:
- name, return_type, function_type
- file_path, line_number, is_static
- memory_class, macro_type
- parameters (list)

**Method**: `parse_function_declaration(line, file_path, line_number)`

---

### SWR_PARSER_00006 - Return Type Conversion
**Purpose**: Convert AUTOSAR macros to C types

**Conversions**:
- `FUNC(type, ...)` → `type`
- `FUNC_P2VAR(type, ...)` → `type*`
- `FUNC_P2CONST(type, ...)` → `const type*`

**Implementation**: String processing in `AutosarParser`

---

### SWR_PARSER_00007 - Static Function Detection
**Purpose**: Detect `STATIC` keyword in AUTOSAR macros

**Implementation**: Regex capture group for `STATIC`

---

### SWR_PARSER_00008 - Whitespace Tolerance
**Purpose**: Handle varying whitespace in AUTOSAR macros

**Examples**:
- `FUNC(void, RTE_CODE)`
- `FUNC( void, RTE_CODE )`
- `FUNC(  void  ,  RTE_CODE  )`

**Implementation**: Flexible regex with `\s*`

---

### SWR_PARSER_00009 - Empty Parameter Handling
**Purpose**: Handle `void` or empty parameter lists

**Implementation**: Return empty list for `void`

---

### SWR_PARSER_00010 - FunctionType Classification
**Purpose**: Classify AUTOSAR functions correctly

**Types**:
- `FUNC` → `FunctionType.AUTOSAR_FUNC`
- `FUNC_P2VAR` → `FunctionType.AUTOSAR_FUNC_P2VAR`
- `FUNC_P2CONST` → `FunctionType.AUTOSAR_FUNC_P2CONST`

**Implementation**: Set based on macro type

---

## C Parser - Regex-Based (SWR_PARSER_00011 - SWR_PARSER_00025)

### SWR_PARSER_00011 - Traditional C Function Pattern
**Purpose**: Match traditional C function declarations

**Pattern**: `[static] [inline] return_type function_name(params)`

**Example**: `static void helper_function(uint8* data)`

**Implementation**: Regex pattern in `CParser`

---

### SWR_PARSER_00012 - Keyword and Type Filtering
**Purpose**: Exclude C keywords and AUTOSAR types from function calls

**Excluded**:
- **C Keywords** (40+): if, else, while, for, return, etc.
- **AUTOSAR Types**: uint8, uint16, uint32, boolean, etc.
- **AUTOSAR Macros**: INT32_C, UINT32_C, etc.

**Implementation**: `C_KEYWORDS`, `AUTOSAR_TYPES`, `AUTOSAR_MACROS` sets

---

### SWR_PARSER_00013 - File-Level Parsing
**Purpose**: Parse entire C source file

**Process**:
1. Remove comments
2. Process line-by-line (prevents ReDoS)
3. Extract functions and calls
4. Track if/else and loop context

**Method**: `parse_file(file_path)`

---

### SWR_PARSER_00014 - Comment Removal
**Purpose**: Remove C-style comments

**Types**:
- Multi-line: `/* ... */`
- Single-line: `// ...`

**Implementation**: Regex substitution

---

### SWR_PARSER_00015 - Line-by-Line Processing
**Purpose**: Prevent catastrophic backtracking

**Benefit**: O(n) vs O(2^n) for pathological cases

**Implementation**: Process file line-by-line instead of single regex

---

### SWR_PARSER_00016 - Multi-Line Function Prototypes
**Purpose**: Handle function prototypes spanning multiple lines

**Challenge**: Return type, name, and parameters on different lines

**Implementation**: Multi-line collection with parenthesis tracking

---

### SWR_PARSER_00017 - Parameter String Parsing
**Purpose**: Parse C parameter syntax

**Handles**:
- `type name`
- `type* name` (pointer)
- `const type* name` (const pointer)
- `type name[]` (array)

**Implementation**: Regex parsing

---

### SWR_PARSER_00018 - Smart Split Parameters
**Purpose**: Split parameters by comma, respecting nested parentheses

**Method**: `_smart_split(text, delimiter)`

**Implementation**: Depth-aware splitting

---

### SWR_PARSER_00019 - Function Body Extraction
**Purpose**: Extract function body to find calls

**Challenge**: Handle nested braces

**Implementation**: Balanced brace counting

---

### SWR_PARSER_00020 - Function Call Extraction
**Purpose**: Extract function calls from body

**Pattern**: `identifier(`

**Features**:
- Track if/else context
- Track loop context
- Extract condition text
- Filter keywords and types

**Method**: `_extract_function_calls(function_body)`

---

### SWR_PARSER_00021 - Conditional Call Detection
**Purpose**: Detect function calls inside if/else blocks

**Context Tracked**:
- `if (condition) { call(); }`
- `else if (condition) { call(); }`
- `else { call(); }`

**Data**:
- `is_conditional=True`
- `condition="condition text"`

**Implementation**: Brace depth tracking in `_extract_function_calls()`

---

### SWR_PARSER_00022 - Multi-Line If Condition Extraction
**Purpose**: Extract conditions spanning multiple lines

**Challenge**: Balanced parentheses across lines

**Implementation**: Multi-line collection with parenthesis tracking

---

### SWR_PARSER_00023 - Loop Detection
**Purpose**: Detect for/while loops in function bodies

**Context Tracked**:
- `for (init; condition; increment) { call(); }`
- `while (condition) { call(); }`

**Data**:
- `is_loop=True`
- `loop_condition="condition text"`

**Implementation**: Loop context tracking in `_extract_function_calls()`

---

### SWR_PARSER_00024 - Condition Text Sanitization
**Purpose**: Sanitize condition text for Mermaid output

**Removals**:
- Unbalanced parentheses
- Preprocessor directives
- C code statements (braces, semicolons)
- Trailing artifacts

**Method**: `_sanitize_condition(condition)`

---

### SWR_PARSER_00025 - Progressive Enhancement
**Purpose**: Try AUTOSAR parser first, fall back to C parser

**Process**:
1. Check for "FUNC(" in content
2. Use AutosarParser for AUTOSAR functions
3. Use C parser for traditional C functions
4. Merge results

**Implementation**: Hybrid parsing in `CParser.parse_file()`

---

## C Parser - pycparser-Based (SWR_PARSER_00026 - SWR_PARSER_00035)

### SWR_PARSER_00026 - Optional Dependency
**Purpose**: pycparser is an optional dependency

**Install**: `pip install -e ".[parser]"`

**Fallback**: Use regex parser if not installed

**Implementation**: Try import with `PYCPARSER_AVAILABLE` flag

---

### SWR_PARSER_00027 - AST-Based Parsing
**Purpose**: Use pycparser AST for accurate C parsing

**Benefits**:
- Handles complex declarations correctly
- Function pointers, arrays, nested pointers
- More reliable than regex

**Implementation**: `pycparser.c_parser.CParser` and `c_ast` module

---

### SWR_PARSER_00028 - AUTOSAR Macro Preprocessing
**Purpose**: Convert AUTOSAR macros to standard C before parsing

**Conversions**:
- `FUNC(return_type, class)` → `return_type`
- `FUNC_P2VAR(...)` → `return_type*`
- `VAR(type, class)` → `type`
- `P2VAR(type, ...)` → `type*`
- etc.

**Method**: `_preprocess_content(content)`

**Implementation**: Regex substitution before pycparser parsing

---

### SWR_PARSER_00029 - AST Visitor Pattern
**Purpose**: Extract functions from pycparser AST

**Implementation**: `FunctionVisitor` class extends `c_ast.NodeVisitor`

**Methods**:
- `visit_FuncDef`: Extract function definitions
- Extract parameters from AST nodes

---

### SWR_PARSER_00030 - Return Type Extraction from AST
**Purpose**: Extract return type from function AST node

**Handles**:
- Standard types (`TypeDecl`)
- Pointer types (`PtrDecl`)
- Array types (`ArrayDecl`)
- Function pointer types (`FuncDecl`)

**Method**: `_extract_return_type(node)`

---

### SWR_PARSER_00031 - Parameter Extraction from AST
**Purpose**: Extract parameters from function parameter list

**Implementation**: Traverse parameter list in `FuncDecl`

**Data**: Extract name, type, pointer status

---

### SWR_PARSER_00032 - Function Call Extraction via AST
**Purpose**: Extract function calls from function body AST

**Implementation**: AST traversal to find `FuncCall` nodes

**Filtering**: Skip C keywords, AUTOSAR types, AUTOSAR macros

**Fallback**: Regex-based extraction for AUTOSAR functions

---

### SWR_PARSER_00033 - Hybrid Parsing Strategy
**Purpose**: Handle both AUTOSAR and traditional C

**Process**:
1. Parse AUTOSAR functions using `AutosarParser`
2. Parse traditional C using pycparser
3. Merge results, avoiding duplicates

**Deduplication**: Track (name, line_number) tuples

---

### SWR_PARSER_00034 - Preprocessor Directive Handling
**Purpose**: Handle preprocessor directives correctly

**Directives**: Remove `#pragma`, `#line`, `#error`, `#warning`

**Implementation**: Regex in `_preprocess_content()`

---

### SWR_PARSER_00035 - Parse Error Graceful Handling
**Purpose**: Handle pycparser parse errors gracefully

**Behavior**:
- Catch parsing exceptions
- Fall back to regex parser on error
- Log warning in verbose mode

**Implementation**: Try-except in `parse_file()`

---

## Common Parser Requirements (SWR_PARSER_00036 - SWR_PARSER_00040)

### SWR_PARSER_00036 - FunctionInfo Creation
**Purpose**: Create FunctionInfo objects with all required fields

**Fields Populated**:
- Identity: name, return_type, file_path, line_number
- Type: function_type, is_static
- Relationships: parameters, calls

**Implementation**: Consistent across all parsers

---

### SWR_PARSER_00037 - Parameter Dataclass Creation
**Purpose**: Create Parameter objects for function parameters

**Fields**:
- name, param_type, is_pointer, is_const

**Implementation**: Consistent parameter parsing

---

### SWR_PARSER_00038 - FunctionCall Dataclass Creation
**Purpose**: Create FunctionCall objects for calls found

**Fields**:
- name, is_conditional, condition, is_loop, loop_condition

**Implementation**: Consistent call extraction

---

### SWR_PARSER_00039 - File Encoding Handling
**Purpose**: Handle various file encodings

**Behavior**: Use UTF-8 with error ignoring

**Implementation**: `read_text(encoding="utf-8", errors="ignore")`

---

### SWR_PARSER_00040 - Parser Selection Interface
**Purpose**: Common interface for all parsers

**Required Method**:
- `parse_file(file_path: Path) -> List[FunctionInfo]`

**Implementation**: Same signature across all parsers

---

## Summary

**Total Requirements**: 40
**Implementation Status**: ✅ All Implemented

**Package Structure**:
```
autosar_calltree.parsers/
├── autosar_parser.py       # SWR_PARSER_00001 - SWR_PARSER_00010 (AUTOSAR Parser)
├── c_parser.py              # SWR_PARSER_00011 - SWR_PARSER_00025 (Regex-Based C Parser)
└── c_parser_pycparser.py    # SWR_PARSER_00026 - SWR_PARSER_00035 (pycparser-Based C Parser)
                            # SWR_PARSER_00036 - SWR_PARSER_00040 (Common)
```

**Parser Selection**:
- `FunctionDatabase` auto-detects best available parser
- Tries pycparser first, falls back to regex
- All parsers handle AUTOSAR macros correctly
