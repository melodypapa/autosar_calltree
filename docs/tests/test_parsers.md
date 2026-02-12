# Parsers Package Test Cases

## Overview

This document describes test cases for the Parsers package, organized by requirement structure.

**Requirements Document**: [requirements_parsers.md](../requirements/requirements_parsers.md)

**Package**: `autosar_calltree.parsers`
**Source Files**: `autosar_parser.py`, `c_parser.py`, `c_parser_pycparser.py`
**Requirement IDs**: SWR_PARSER_00001 - SWR_PARSER_00040
**Coverage**: 92%

---

## AUTOSAR Parser Tests

### SWUT_PARSER_00001 - AUTOSAR Macro Recognition

**Requirement**: SWR_PARSER_00001
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that the AutosarParser recognizes and parses AUTOSAR function macros correctly.

**Test Approach**
The test verifies that:
1. All supported AUTOSAR function macros are matched (FUNC, FUNC_P2VAR, FUNC_P2CONST)
2. STATIC variants are recognized
3. Macro parameters are extracted correctly
4. Function name and return type are parsed accurately

**Expected Behavior**
The parser correctly identifies AUTOSAR function declarations and extracts their components (return type, memory class, function name, parameters).

**Edge Cases**
- Whitespace variations
- Nested parentheses in parameters
- Mixed static and non-static declarations

---

### SWUT_PARSER_00002 - AUTOSAR Parameter Macros

**Requirement**: SWR_PARSER_00002
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that AUTOSAR parameter macros (VAR, P2VAR, P2CONST, CONST) are parsed correctly.

**Test Approach**
The test verifies that:
1. VAR(type, memory_class) name patterns are matched
2. P2VAR(type, ptr_class, mem_class) name patterns are matched
3. P2CONST(type, ptr_class, mem_class) name patterns are matched
4. CONST(type, mem_class) name patterns are matched
5. Parameter type, name, and flags are extracted correctly

**Expected Behavior**
AUTOSAR parameter declarations are parsed with correct type information, pointer/const flags, and memory class.

**Edge Cases**
- Complex type names
- Whitespace variations
- Multiple parameters in sequence

---

### SWUT_PARSER_00003 - Parameter String Extraction

**Requirement**: SWR_PARSER_00003
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates extraction of parameter lists from function declarations with nested parentheses.

**Test Approach**
The test verifies that:
1. Simple parameter lists are extracted: `(void)`
2. Multiple parameters are split correctly: `(int a, float b)`
3. Nested parentheses are handled: `(void (*)(int))`
4. Function pointers with parameters work

**Expected Behavior**
Parameter strings are extracted by counting balanced parentheses, handling nested constructs correctly.

**Edge Cases**
- Empty parameter lists
- Function pointer parameters
- Array parameters with brackets

---

### SWUT_PARSER_00004 - Parameter List Splitting

**Requirement**: SWR_PARSER_00004
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures parameters are split by comma while respecting nested parentheses.

**Test Approach**
The test verifies that:
1. Simple parameters are split: `a, b, c`
2. Parameters with nested parentheses stay together: `int (*func)(int), float b`
3. Template-like parameters are handled correctly
4. Trailing/leading whitespace is trimmed

**Expected Behavior**
Parameter splitting uses depth-aware comma detection to avoid splitting on commas inside nested parentheses.

**Edge Cases**
- Function pointer parameters
- Function types as parameters
- Default argument values

---

### SWUT_PARSER_00005 - Function Declaration Parsing

**Requirement**: SWR_PARSER_00005
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that AUTOSAR function declarations are parsed into FunctionInfo objects with all required fields.

**Test Approach**
The test verifies that:
1. parse_function_declaration() creates FunctionInfo with correct fields
2. Return type is extracted from macro
3. Function name is identified correctly
4. Parameters are parsed and converted to Parameter objects
5. File path and line number are recorded

**Expected Behavior**
AUTOSAR function declarations produce complete FunctionInfo objects with identity, type, and parameter information.

**Edge Cases**
- Static function declarations
- Functions with many parameters
- Complex return types

---

### SWUT_PARSER_00006 - Return Type Conversion

**Requirement**: SWR_PARSER_00006
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Ensures that AUTOSAR macros are converted to correct C return types.

**Test Approach**
The test verifies that:
1. FUNC(type, class) → `type`
2. FUNC_P2VAR(type, ...) → `type*`
3. FUNC_P2CONST(type, ...) → `const type*`
4. Memory class is not included in return type

**Expected Behavior**
AUTOSAR macro return types are converted to standard C pointer notation with const qualifiers.

**Edge Cases**
- Nested pointer types
- Const pointer returns
- Void return types

---

### SWUT_PARSER_00007 - Static Function Detection

**Requirement**: SWR_PARSER_00007
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that STATIC keyword is detected in AUTOSAR macros.

**Test Approach**
The test verifies that:
1. STATIC FUNC(...) is marked as static
2. STATIC FUNC_P2VAR(...) is marked as static
3. Functions without STATIC are not marked as static
4. The is_static flag is set correctly in FunctionInfo

**Expected Behavior**
AUTOSAR functions with STATIC prefix have is_static=True, others have is_static=False.

**Edge Cases**
- Mixed case variations
- Whitespace between STATIC and FUNC

---

### SWUT_PARSER_00008 - Whitespace Tolerance

**Requirement**: SWR_PARSER_00008
**Priority**: Low
**Status**: ✅ Pass

**Description**
Ensures that varying whitespace in AUTOSAR macros is handled correctly.

**Test Approach**
The test verifies that:
1. FUNC(void,RTE_CODE) works (no spaces)
2. FUNC( void , RTE_CODE ) works (extra spaces)
3. FUNC(void, RTE_CODE) works (normal spacing)
4. All produce same FunctionInfo result

**Expected Behavior**
AUTOSAR macros are parsed regardless of whitespace variations using flexible regex patterns.

**Edge Cases**
- Tabs vs spaces
- Multiple consecutive spaces
- Newlines in declarations

---

### SWUT_PARSER_00009 - Empty Parameter Handling

**Requirement**: SWR_PARSER_00009
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that void or empty parameter lists are handled correctly.

**Test Approach**
The test verifies that:
1. `void` parameter produces empty parameters list
2. Empty parentheses `()` produce empty parameters list
3. Functions with void parameters have 0 parameters

**Expected Behavior**
Empty parameter lists result in empty list, not a Parameter with name="void".

**Edge Cases**
- VOID in different cases
- Whitespace in empty parameter list

---

### SWUT_PARSER_00010 - FunctionType Classification

**Requirement**: SWR_PARSER_00010
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that AUTOSAR functions are classified into correct FunctionType enum values.

**Test Approach**
The test verifies that:
1. FUNC → FunctionType.AUTOSAR_FUNC
2. FUNC_P2VAR → FunctionType.AUTOSAR_FUNC_P2VAR
3. FUNC_P2CONST → FunctionType.AUTOSAR_FUNC_P2CONST
4. function_type field is set correctly in FunctionInfo

**Expected Behavior**
AUTOSAR macros are classified into appropriate FunctionType values for downstream processing.

**Edge Cases**
- Static variants of each type
- Mixed case macro names

---

## C Parser (Regex-Based) Tests

### SWUT_PARSER_00011 - Traditional C Function Pattern

**Requirement**: SWR_PARSER_00011
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that the regex-based C parser matches traditional C function declarations.

**Test Approach**
The test verifies that:
1. Pattern matches `return_type function_name(params)`
2. Static keyword is recognized
3. Inline keyword is recognized
4. Various return types work (int, void, uint8_t, etc.)

**Expected Behavior**
Traditional C function declarations are matched and parsed into FunctionInfo objects.

**Edge Cases**
- Pointer return types
- Function pointers
- Struct return types

---

### SWUT_PARSER_00012 - Keyword and Type Filtering

**Requirement**: SWR_PARSER_00012
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that C keywords and AUTOSAR types are excluded from function call detection.

**Test Approach**
The test verifies that:
1. C keywords (if, else, while, for, return, etc.) are not matched as function calls
2. AUTOSAR types (uint8, uint16, uint32, boolean) are excluded
3. AUTOSAR macros (INT32_C, UINT32_C) are excluded
4. Valid function names are still matched

**Expected Behavior**
Known keywords and types are filtered out to avoid false positive function call detection.

**Edge Cases**
- Function names that match keywords
- Custom types with similar names
- Case sensitivity

---

### SWUT_PARSER_00013 - File-Level Parsing

**Requirement**: SWR_PARSER_00013
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that entire C source files are parsed correctly.

**Test Approach**
The test verifies that:
1. All functions in file are found
2. Comment removal works correctly
3. Line-by-line processing prevents catastrophic backtracking
4. Function bodies are extracted for call analysis

**Expected Behavior**
parse_file() processes complete C files, extracting all functions and their call relationships.

**Edge Cases**
- Files with many functions
- Large files (>1000 lines)
- Files with only declarations

---

### SWUT_PARSER_00014 - Comment Removal

**Requirement**: SWR_PARSER_00014
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Ensures that C-style comments are removed before parsing.

**Test Approach**
The test verifies that:
1. Multi-line comments `/* ... */` are removed
2. Single-line comments `// ...` are removed
3. Nested comments are handled
4. Code outside comments is preserved

**Expected Behavior**
All C-style comments are stripped from source code before parsing to avoid interference.

**Edge Cases**
- Unterminated comments
- Comments in string literals
- Comment-like content in strings

---

### SWUT_PARSER_00015 - Line-by-Line Processing

**Requirement**: SWR_PARSER_00015
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that line-by-line processing is used to prevent catastrophic backtracking.

**Test Approach**
The test verifies that:
1. File is processed line-by-line, not with single regex
2. Each line is checked independently
3. Performance is O(n) not O(2^n) for pathological cases
4. Large files are processed efficiently

**Expected Behavior**
C parser processes files line-by-line to avoid regex catastrophic backtracking vulnerabilities.

**Edge Cases**
- Very long lines
- Files with many function declarations
- Pathological regex patterns

---

### SWUT_PARSER_00016 - Multi-Line Function Prototypes

**Requirement**: SWR_PARSER_00016
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Ensures that function prototypes spanning multiple lines are handled correctly.

**Test Approach**
The test verifies that:
1. Return type, name, and parameters on different lines work
2. Line continuation is detected
3. Parenthesis tracking collects complete signature
4. Proper function boundaries are identified

**Expected Behavior**
Multi-line function declarations are assembled correctly by tracking parentheses across lines.

**Edge Cases**
- Many-line declarations (5+ lines)
- Comments between declaration parts
- Preprocessor directives in declaration

---

### SWUT_PARSER_00017 - Parameter String Parsing

**Requirement**: SWR_PARSER_00017
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that C parameter syntax is parsed correctly.

**Test Approach**
The test verifies that:
1. `type name` format is parsed
2. `type* name` (pointer) is parsed
3. `const type* name` (const pointer) is parsed
4. `type name[]` (array) is parsed
5. Array dimensions are extracted

**Expected Behavior**
C parameter declarations are parsed into Parameter objects with correct type, name, and flags.

**Edge Cases**
- Multiple pointers (type** name)
- Const with pointer (const type* name)
- Multi-dimensional arrays
- Function pointer parameters

---

### SWUT_PARSER_00018 - Smart Split Parameters

**Requirement**: SWR_PARSER_00018
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that parameters are split by comma respecting nested parentheses.

**Test Approach**
The test verifies that:
1. Simple parameters split on commas: `int a, float b`
2. Function pointer parameters stay together: `void (*func)(int), int b`
3. Nested templates handled: `std::vector<int> a, int b`
4. _smart_split method works correctly

**Expected Behavior**
Parameter splitting uses depth tracking to avoid splitting on commas inside parentheses.

**Edge Cases**
- Complex template types
- Function types as parameters
- Default arguments with commas

---

### SWUT_PARSER_00019 - Function Body Extraction

**Requirement**: SWR_PARSER_00019
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that function bodies are extracted by finding balanced braces.

**Test Approach**
The test verifies that:
1. Opening brace after declaration is found
2. Matching closing brace is identified
3. Nested braces are tracked correctly
4. Body content is extracted completely

**Expected Behavior**
Function bodies are extracted by counting brace depth, finding the matching closing brace.

**Edge Cases**
- Nested structures (if/else, loops)
- Arrays with brace initialization
- Preprocessor directives in body

---

### SWUT_PARSER_00020 - Function Call Extraction

**Requirement**: SWR_PARSER_00020
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that function calls are extracted from function bodies.

**Test Approach**
The test verifies that:
1. Pattern `identifier(` matches function calls
2. C keywords are filtered out
3. AUTOSAR types are filtered out
4. Call list is populated correctly

**Expected Behavior**
All valid function calls in the function body are extracted for call tree building.

**Edge Cases**
- Control structures with parentheses
- Macro calls that look like functions
- Function pointers as calls

---

### SWUT_PARSER_00021 - Conditional Call Detection

**Requirement**: SWR_PARSER_00021
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that function calls inside if/else blocks are detected with condition context.

**Test Approach**
The test verifies that:
1. Calls inside `if (condition) { }` are marked conditional
2. `else if` and `else` blocks are detected
3. Condition text is extracted and sanitized
4. Calls outside conditionals are not marked

**Expected Behavior**
Function calls in conditional blocks have is_conditional=True with condition text for opt block generation.

**Edge Cases**
- Nested conditionals
- Multi-line conditions
- Complex boolean expressions
- Ternary operators

---

### SWUT_PARSER_00022 - Multi-Line If Condition Extraction

**Requirement**: SWR_PARSER_00022
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Ensures that conditions spanning multiple lines are extracted correctly.

**Test Approach**
The test verifies that:
1. Conditions on multiple lines are collected
2. Balanced parentheses are tracked across lines
3. Complete condition text is captured
4. Condition sanitization handles multi-line input

**Expected Behavior**
Multi-line if conditions are completely extracted by tracking parentheses across line boundaries.

**Edge Cases**
- Deeply nested parentheses
- Line breaks in awkward positions
- Comments in conditions

---

### SWUT_PARSER_00023 - Loop Detection

**Requirement**: SWR_PARSER_00023
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that for/while loops in function bodies are detected.

**Test Approach**
The test verifies that:
1. `for (init; condition; increment) { }` loops are detected
2. `while (condition) { }` loops are detected
3. Loop condition text is extracted
4. Calls in loops have is_loop=True

**Expected Behavior**
Function calls inside loops are marked with loop context for loop block generation in diagrams.

**Edge Cases**
- Nested loops
- Do-while loops
- Infinite loops (while(1))
- Complex loop conditions

---

### SWUT_PARSER_00024 - Condition Text Sanitization

**Requirement**: SWR_PARSER_00024
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Ensures that condition text is sanitized for Mermaid output.

**Test Approach**
The test verifies that:
1. Unbalanced parentheses are removed
2. Preprocessor directives (#ifdef, etc.) are removed
3. C code artifacts (braces, semicolons) are removed
4. Readable condition text remains

**Expected Behavior**
Condition text is cleaned to remove C syntax artifacts while preserving readable logic.

**Edge Cases**
- Complex nested parentheses
- Macro invocations in conditions
- String literals in conditions

---

### SWUT_PARSER_00025 - Progressive Enhancement

**Requirement**: SWR_PARSER_00025
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that AUTOSAR parser is tried first, falling back to C parser.

**Test Approach**
The test verifies that:
1. Files with "FUNC(" trigger AUTOSAR parser first
2. Remaining functions are parsed by C parser
3. Duplicate functions are avoided (deduplication)
4. Both result sets are merged correctly

**Expected Behavior**
Hybrid parsing strategy uses AUTOSAR parser for AUTOSAR functions and C parser for traditional C, merging results.

**Edge Cases**
- Files with both AUTOSAR and C functions
- Files with only C functions
- Files with only AUTOSAR functions

---

## C Parser (pycparser-Based) Tests

### SWUT_PARSER_00026 - Optional Dependency

**Requirement**: SWR_PARSER_00026
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that pycparser is treated as an optional dependency.

**Test Approach**
The test verifies that:
1. Parser works when pycparser is installed
2. Graceful fallback when pycparser is not available
3. PYCPARSER_AVAILABLE flag is set correctly
4. Import errors don't crash the application

**Expected Behavior**
pycparser is optional - parser falls back to regex-based implementation when not installed.

**Edge Cases**
- pycparser not installed
- pycparser import fails
- Version incompatibilities

---

### SWUT_PARSER_00027 - AST-Based Parsing

**Requirement**: SWR_PARSER_00027
**Priority**: High
**Status**: ✅ Pass

**Description**
Validates that pycparser AST is used for accurate C parsing.

**Test Approach**
The test verifies that:
1. pycparser CParser is used correctly
2. AST traversal finds all function definitions
3. Complex declarations are handled correctly
4. More reliable than regex-based approach

**Expected Behavior**
pycparser provides AST-based parsing with accurate handling of complex C declarations.

**Edge Cases**
- Function pointers
- Arrays of pointers
- Nested structures

---

### SWUT_PARSER_00028 - AUTOSAR Macro Preprocessing

**Requirement**: SWR_PARSER_00028
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that AUTOSAR macros are converted to standard C before pycparser parsing.

**Test Approach**
The test verifies that:
1. FUNC(return, class) → return_type
2. FUNC_P2VAR(...) → return_type*
3. VAR(type, class) → type
4. P2VAR/P2CONST macros converted correctly

**Expected Behavior**
AUTOSAR macros are preprocessed to standard C syntax before feeding to pycparser.

**Edge Cases**
- Complex AUTOSAR expressions
- Nested macros
- Mixed AUTOSAR and C code

---

### SWUT_PARSER_00029 - AST Visitor Pattern

**Requirement**: SWR_PARSER_00029
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Validates that AST visitor pattern extracts functions correctly.

**Test Approach**
The test verifies that:
1. FunctionVisitor extends c_ast.NodeVisitor
2. visit_FuncDef extracts function definitions
3. Parameters are extracted from AST nodes
4. Visitor pattern is implemented correctly

**Expected Behavior**
AST visitor pattern systematically walks the AST, extracting function information.

**Edge Cases**
- Deeply nested AST structures
- Many functions in file
- Complex function signatures

---

### SWUT_PARSER_00030 - Return Type Extraction from AST

**Requirement**: SWR_PARSER_00030
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that return types are extracted from function AST nodes correctly.

**Test Approach**
The test verifies that:
1. TypeDecl (standard types) are handled
2. PtrDecl (pointer types) are handled
3. ArrayDecl (array types) are handled
4. FuncDecl (function pointer types) are handled

**Expected Behavior**
Return type is correctly extracted from AST regardless of type complexity.

**Edge Cases**
- Multiple levels of pointers
- Complex function pointer returns
- Qualified types (const, volatile)

---

### SWUT_PARSER_00031 - Parameter Extraction from AST

**Requirement**: SWR_PARSER_00031
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that parameters are extracted from function parameter list in AST.

**Test Approach**
The test verifies that:
1. Parameter list from FuncDecl is traversed
2. Parameter name and type are extracted
3. Pointer status is detected
4. Const qualification is preserved

**Expected Behavior**
All function parameters are extracted from AST with complete type information.

**Edge Cases**
- Functions with many parameters
- Variadic functions (...)
- Untyped parameters (legacy K&R)

---

### SWUT_PARSER_00032 - Function Call Extraction via AST

**Requirement**: SWR_PARSER_00032
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that function calls are extracted from function body AST.

**Test Approach**
The test verifies that:
1. AST traversal finds FuncCall nodes
2. C keywords are filtered from calls
3. AUTOSAR types are filtered
4. Fallback regex extraction works for AUTOSAR functions

**Expected Behavior**
Function calls are identified from AST, with fallback to regex for AUTOSAR-specific constructs.

**Edge Cases**
- Calls through function pointers
- Macro invocations
- Recursive calls

---

### SWUT_PARSER_00033 - Hybrid Parsing Strategy

**Requirement**: SWR_PARSER_00033
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that both AUTOSAR and traditional C parsing work together.

**Test Approach**
The test verifies that:
1. AUTOSAR functions are parsed using AutosarParser
2. Traditional C functions are parsed using pycparser
3. Results are merged without duplicates
4. Deduplication uses (name, line_number) tuples

**Expected Behavior**
Hybrid parsing handles mixed AUTOSAR and C code, merging results intelligently.

**Edge Cases**
- Files with both types of functions
- Same function name from different parsers
- Files with only one type

---

### SWUT_PARSER_00034 - Preprocessor Directive Handling

**Requirement**: SWR_PARSER_00034
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Ensures that preprocessor directives are handled correctly.

**Test Approach**
The test verifies that:
1. #pragma directives are removed
2. #line directives are removed
3. #error directives are removed
4. #warning directives are removed
5. Other preprocessor directives don't cause parse errors

**Expected Behavior**
Problematic preprocessor directives are removed before pycparser parsing to avoid errors.

**Edge Cases**
- Pragmas in middle of function
- Line directives with arbitrary arguments
- Custom preprocessor directives

---

### SWUT_PARSER_00035 - Parse Error Graceful Handling

**Requirement**: SWR_PARSER_00035
**Priority**: Medium
**Status**: ✅ Pass

**Description**
Ensures that pycparser parse errors are handled gracefully.

**Test Approach**
The test verifies that:
1. Parse exceptions are caught
2. Fallback to regex parser occurs on error
3. Warning is logged in verbose mode
4. Partial results are returned if possible

**Expected Behavior**
pycparser errors trigger graceful fallback to regex parser, maintaining functionality.

**Edge Cases**
- Syntax errors in source
- pycparser limitations
- Files pycparser can't parse

---

## Common Parser Requirements Tests

### SWUT_PARSER_00036 - FunctionInfo Creation

**Requirement**: SWR_PARSER_00036
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that FunctionInfo objects are created with all required fields.

**Test Approach**
The test verifies that:
1. Identity fields are populated (name, return_type, file_path, line_number)
2. Type fields are set (function_type, is_static)
3. Relationships are initialized (parameters, calls)
4. All fields have correct values

**Expected Behavior**
All parsers create consistent FunctionInfo objects with complete information.

**Edge Cases**
- Functions without parameters
- Functions without calls
- Static vs non-static

---

### SWUT_PARSER_00037 - Parameter Dataclass Creation

**Requirement**: SWR_PARSER_00037
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that Parameter objects are created for function parameters.

**Test Approach**
The test verifies that:
1. Parameter name is extracted correctly
2. Parameter type is preserved
3. is_pointer flag is set correctly
4. is_const flag is set correctly

**Expected Behavior**
Parameter objects are created consistently across all parsers with complete information.

**Edge Cases**
- Pointer parameters
- Const parameters
- Const pointer parameters

---

### SWUT_PARSER_00038 - FunctionCall Dataclass Creation

**Requirement**: SWR_PARSER_00038
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that FunctionCall objects are created for calls found in function bodies.

**Test Approach**
The test verifies that:
1. Function name is captured
2. is_conditional and condition are set when applicable
3. is_loop and loop_condition are set when applicable
4. Fields default to False/None for regular calls

**Expected Behavior**
FunctionCall objects track calls with conditional and loop context for diagram generation.

**Edge Cases**
- Calls in conditionals
- Calls in loops
- Calls in both
- Regular calls

---

### SWUT_PARSER_00039 - File Encoding Handling

**Requirement**: SWR_PARSER_00039
**Priority**: Low
**Status**: ✅ Pass

**Description**
Ensures that various file encodings are handled correctly.

**Test Approach**
The test verifies that:
1. UTF-8 files are read correctly
2. Encoding errors are ignored gracefully
3. read_text with encoding="utf-8" is used
4. Files with BOM are handled

**Expected Behavior**
Source files are read with UTF-8 encoding, ignoring encoding errors to allow parsing.

**Edge Cases**
- Files with non-ASCII characters
- Invalid UTF-8 sequences
- Mixed encoding files
- Files with BOM markers

---

### SWUT_PARSER_00040 - Parser Selection Interface

**Requirement**: SWR_PARSER_00040
**Priority**: High
**Status**: ✅ Pass

**Description**
Ensures that all parsers implement a common interface.

**Test Approach**
The test verifies that:
1. All parsers have parse_file(file_path) method
2. Method returns List[FunctionInfo]
3. Method signature is consistent
4. Return type is compatible across parsers

**Expected Behavior**
All parsers implement the same interface, allowing them to be used interchangeably.

**Edge Cases**
- Different parser implementations
- Parser switching at runtime
- Empty parse results

---

## Requirements Traceability Matrix

| Requirement ID | Test ID | Status | Notes |
|---------------|-----------|---------|--------|
| SWR_PARSER_00001 | SWUT_PARSER_00001 | ✅ Pass | AUTOSAR macro recognition |
| SWR_PARSER_00002 | SWUT_PARSER_00002 | ✅ Pass | AUTOSAR parameter macros |
| SWR_PARSER_00003 | SWUT_PARSER_00003 | ✅ Pass | Parameter string extraction |
| SWR_PARSER_00004 | SWUT_PARSER_00004 | ✅ Pass | Parameter list splitting |
| SWR_PARSER_00005 | SWUT_PARSER_00005 | ✅ Pass | Function declaration parsing |
| SWR_PARSER_00006 | SWUT_PARSER_00006 | ✅ Pass | Return type conversion |
| SWR_PARSER_00007 | SWUT_PARSER_00007 | ✅ Pass | Static function detection |
| SWR_PARSER_00008 | SWUT_PARSER_00008 | ✅ Pass | Whitespace tolerance |
| SWR_PARSER_00009 | SWUT_PARSER_00009 | ✅ Pass | Empty parameter handling |
| SWR_PARSER_00010 | SWUT_PARSER_00010 | ✅ Pass | FunctionType classification |
| SWR_PARSER_00011 | SWUT_PARSER_00011 | ✅ Pass | Traditional C function pattern |
| SWR_PARSER_00012 | SWUT_PARSER_00012 | ✅ Pass | Keyword and type filtering |
| SWR_PARSER_00013 | SWUT_PARSER_00013 | ✅ Pass | File-level parsing |
| SWR_PARSER_00014 | SWUT_PARSER_00014 | ✅ Pass | Comment removal |
| SWR_PARSER_00015 | SWUT_PARSER_00015 | ✅ Pass | Line-by-line processing |
| SWR_PARSER_00016 | SWUT_PARSER_00016 | ✅ Pass | Multi-line prototypes |
| SWR_PARSER_00017 | SWUT_PARSER_00017 | ✅ Pass | Parameter string parsing |
| SWR_PARSER_00018 | SWUT_PARSER_00018 | ✅ Pass | Smart split parameters |
| SWR_PARSER_00019 | SWUT_PARSER_00019 | ✅ Pass | Function body extraction |
| SWR_PARSER_00020 | SWUT_PARSER_00020 | ✅ Pass | Function call extraction |
| SWR_PARSER_00021 | SWUT_PARSER_00021 | ✅ Pass | Conditional call detection |
| SWR_PARSER_00022 | SWUT_PARSER_00022 | ✅ Pass | Multi-line if condition |
| SWR_PARSER_00023 | SWUT_PARSER_00023 | ✅ Pass | Loop detection |
| SWR_PARSER_00024 | SWUT_PARSER_00024 | ✅ Pass | Condition sanitization |
| SWR_PARSER_00025 | SWUT_PARSER_00025 | ✅ Pass | Progressive enhancement |
| SWR_PARSER_00026 | SWUT_PARSER_00026 | ✅ Pass | Optional dependency |
| SWR_PARSER_00027 | SWUT_PARSER_00027 | ✅ Pass | AST-based parsing |
| SWR_PARSER_00028 | SWUT_PARSER_00028 | ✅ Pass | AUTOSAR preprocessing |
| SWR_PARSER_00029 | SWUT_PARSER_00029 | ✅ Pass | AST visitor pattern |
| SWR_PARSER_00030 | SWUT_PARSER_00030 | ✅ Pass | Return type extraction |
| SWR_PARSER_00031 | SWUT_PARSER_00031 | ✅ Pass | Parameter extraction |
| SWR_PARSER_00032 | SWUT_PARSER_00032 | ✅ Pass | Function call extraction |
| SWR_PARSER_00033 | SWUT_PARSER_00033 | ✅ Pass | Hybrid parsing strategy |
| SWR_PARSER_00034 | SWUT_PARSER_00034 | ✅ Pass | Preprocessor handling |
| SWR_PARSER_00035 | SWUT_PARSER_00035 | ✅ Pass | Parse error handling |
| SWR_PARSER_00036 | SWUT_PARSER_00036 | ✅ Pass | FunctionInfo creation |
| SWR_PARSER_00037 | SWUT_PARSER_00037 | ✅ Pass | Parameter creation |
| SWR_PARSER_00038 | SWUT_PARSER_00038 | ✅ Pass | FunctionCall creation |
| SWR_PARSER_00039 | SWUT_PARSER_00039 | ✅ Pass | File encoding handling |
| SWR_PARSER_00040 | SWUT_PARSER_00040 | ✅ Pass | Parser selection interface |

## Coverage Summary

- **Total Requirements**: 40
- **Total Tests**: 40
- **Tests Passing**: 40/40 (100%)
- **Code Coverage**: 92%

## Running Tests

```bash
# Run all parser tests
pytest tests/unit/test_autosar_parser.py
pytest tests/unit/test_c_parser.py

# Run specific test
pytest tests/unit/test_autosar_parser.py::TestClass::test_SWUT_PARSER_00001

# Run with coverage
pytest tests/unit/test_autosar_parser.py tests/unit/test_c_parser.py --cov=autosar_calltree/parsers --cov-report=term-missing
```

## Change History

| Date | Version | Author | Change Description |
|-------|---------|---------|-------------------|
| 2026-02-11 | 2.0 | Reorganized by requirement structure, removed Test Function labels, using natural language |
| 2026-02-10 | 1.0 | Initial test documentation |
