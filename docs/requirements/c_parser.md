# C Parser Requirements

## Overview
The C parser module provides parsing capabilities for traditional C function declarations and definitions. It implements a progressive enhancement strategy: first trying AUTOSAR macros (via AutosarParser integration), then falling back to traditional C parsing. The parser extracts function signatures, parameters, return types, function bodies, and called functions from C source code.

## Requirements

### SWR_PARSER_C_00001: Traditional C Function Pattern Recognition

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall recognize traditional C function declarations/definitions in the format `[static] [inline] return_type function_name(parameters)`.

**Rationale:**
Traditional C functions use standard syntax without AUTOSAR macros. The parser must match this pattern while excluding C keywords, control structures, and preprocessor directives. This enables fallback parsing when AUTOSAR patterns don't match.

**Acceptance Criteria:**
- [ ] Pattern matches `void Demo_Init(void)`
- [ ] Pattern matches `static uint8 Internal_Function(uint8 value)`
- [ ] Pattern matches `inline void FastFunction(void)`
- [ ] Pattern matches `__inline__ void CompilerSpecific(void)`
- [ ] Extracts optional static keyword
- [ ] Extracts optional inline keyword (inline, __inline, __inline__)
- [ ] Extracts return type (including pointers like `uint8*`)
- [ ] Extracts function name
- [ ] Extracts parameter string

**Related Requirements:** SWR_PARSER_C_00002, SWR_PARSER_C_00003

---

### SWR_PARSER_C_00002: C Keyword Filtering

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall exclude C language keywords from function detection to avoid false positives.

**Rationale:**
Control structures (if, for, while, switch) and type keywords (struct, enum, typedef) can match the function pattern if not filtered. The C_KEYWORDS set prevents these false matches.

**Acceptance Criteria:**
- [ ] Maintains C_KEYWORDS set with 40+ keywords
- [ ] Includes control flow keywords: if, else, for, while, do, switch, case, default
- [ ] Includes jump keywords: return, break, continue, goto
- [ ] Includes type keywords: sizeof, typedef, struct, union, enum
- [ ] Includes type qualifiers: const, volatile, static, extern, auto, register
- [ ] Includes inline variants: inline, __inline, __inline__
- [ ] Includes C11 keywords: restrict, _Bool, _Alignas, _Alignof, _Atomic, etc.
- [ ] Skips parsing if return_type or function_name is in C_KEYWORDS

**Related Requirements:** SWR_PARSER_C_00001

---

### SWR_PARSER_C_00003: AUTOSAR Type Filtering

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall exclude AUTOSAR types from function call extraction to avoid false positives.

**Rationale:**
AUTOSAR types (uint8, uint32, Std_ReturnType, etc.) may appear in function bodies as casts or type declarations. These should not be extracted as function calls. The AUTOSAR_TYPES set filters these out.

**Acceptance Criteria:**
- [ ] Maintains AUTOSAR_TYPES set with common AUTOSAR types
- [ ] Includes integer types: uint8, uint16, uint32, uint64
- [ ] Includes signed integer types: sint8, sint16, sint32, sint64
- [ ] Includes boolean types: boolean, Boolean
- [ ] Includes float types: float32, float64
- [ ] Includes return types: Std_ReturnType, StatusType
- [ ] Skips extracting function calls matching these types

**Related Requirements:** SWR_PARSER_C_00009

---

### SWR_PARSER_C_00004: File-Level Parsing

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall provide `parse_file` method that parses an entire C source file and extracts all function definitions.

**Rationale:**
This is the primary entry point for parsing C files. It must handle file I/O, comment removal, AUTOSAR parsing delegation, and traditional C parsing with deduplication.

**Acceptance Criteria:**
- [ ] Accepts Path object for file path
- [ ] Reads file with UTF-8 encoding and error ignoring
- [ ] Returns empty list on file read errors
- [ ] Removes comments before parsing
- [ ] Checks for FUNC macros before trying AUTOSAR parsing
- [ ] Delegates AUTOSAR parsing to AutosarParser
- [ ] Parses traditional C functions after AUTOSAR
- [ ] Detects duplicates (same name and line number)
- [ ] Returns list of unique FunctionInfo objects

**Related Requirements:** SWR_PARSER_AUTOSAR_00011, SWR_PARSER_C_00005

---

### SWR_PARSER_C_00005: Comment Removal

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall remove both single-line (//) and multi-line (/* */) comments before parsing.

**Rationale:**
Comments can contain code-like text that causes false positives in pattern matching. Removing comments first improves parsing accuracy.

**Acceptance Criteria:**
- [ ] Removes multi-line comments `/* ... */` using regex with DOTALL flag
- [ ] Removes single-line comments `// ...` using regex with MULTILINE flag
- [ ] Handles comments with code inside: `/* void fake_func(void); */`
- [ ] Preserves code structure (only removes comments)
- [ ] Returns cleaned content string

**Related Requirements:** SWR_PARSER_C_00004

---

### SWR_PARSER_C_00006: Parameter String Parsing

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall parse function parameters from traditional C parameter strings.

**Rationale:**
Traditional C parameters use different syntax than AUTOSAR macros (e.g., `uint8 value` instead of `VAR(uint8, AUTOMATIC) value`). Parameters must be split by comma, handling arrays and nested types.

**Acceptance Criteria:**
- [ ] Handles `void` as empty parameter list
- [ ] Handles empty string as empty parameter list
- [ ] Splits parameters by comma with smart_split (respects brackets)
- [ ] Parses parameter type and name using regex
- [ ] Detects pointer asterisk in type
- [ ] Handles array notation `[size]` (detects but doesn't store)
- [ ] Handles parameters with no name (type-only)
- [ ] Creates Parameter objects with correct fields

**Related Requirements:** SWR_MODEL_00002, SWR_PARSER_C_00007

---

### SWR_PARSER_C_00007: Smart Split for Parameters

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall provide `_smart_split` method to split text by delimiter while respecting nested parentheses, brackets, and braces.

**Rationale:**
Function parameters may contain function pointers `void (*callback)(int)` or array types `int arr[10]`. Simple splitting would incorrectly break these at the commas. Depth tracking ensures correct splitting.

**Acceptance Criteria:**
- [ ] Tracks depth for opening delimiters: `([{`
- [ ] Tracks depth for closing delimiters: `)]}`
- [ ] Only splits on delimiters at depth 0
- [ ] Handles nested parentheses in function pointers
- [ ] Handles array brackets in parameter types
- [ ] Returns list of split parts
- [ ] Preserves structure of nested types

**Related Requirements:** SWR_PARSER_C_00006

---

### SWR_PARSER_C_00008: Function Body Extraction

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall extract function bodies starting from a given position in the file content.

**Rationale:**
Function calls are extracted from function bodies. The parser must find the opening brace, match balanced braces, and extract the complete body including nested scopes.

**Acceptance Criteria:**
- [ ] Skips leading whitespace to find opening brace
- [ ] Returns None if no opening brace found
- [ ] Tracks brace depth to find matching closing brace
- [ ] Handles nested braces (inner scopes, if statements, loops)
- [ ] Returns body string including outer braces
- [ ] Handles missing closing braces (returns None)

**Related Requirements:** SWR_PARSER_C_00009

---

### SWR_PARSER_C_00009: Function Call Extraction

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall extract all function calls from a function body.

**Rationale:**
Call tree construction requires knowing which functions each function calls. The parser finds all identifiers followed by opening parentheses, filtering out C keywords and AUTOSAR types.

**Acceptance Criteria:**
- [ ] Uses regex pattern `identifier(` to find potential calls
- [ ] Extracts function name from each match
- [ ] Filters out C keywords (using C_KEYWORDS set)
- [ ] Filters out AUTOSAR types (using AUTOSAR_TYPES set)
- [ ] Deduplicates using set data structure
- [ ] Returns sorted list of unique function names
- [ ] Explicitly extracts RTE calls using `Rte_*` pattern

**Related Requirements:** SWR_PARSER_C_00002, SWR_PARSER_C_00003

---

### SWR_PARSER_C_00010: Function Match Parsing

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall provide `_parse_function_match` method to convert regex matches into FunctionInfo objects.

**Rationale:**
This method encapsulates the conversion from regex match groups to FunctionInfo fields. It performs validation, parses parameters, extracts bodies, and determines line numbers.

**Acceptance Criteria:**
- [ ] Extracts static, inline, return_type, function_name, params groups
- [ ] Returns None if return_type starts with # (preprocessor directive)
- [ ] Returns None if return_type or function_name in C_KEYWORDS
- [ ] Sets function_type to TRADITIONAL_C
- [ ] Calls _parse_parameters to parse parameter string
- [ ] Calls _extract_function_body to get function body
- [ ] Calls _extract_function_calls to get called functions
- [ ] Calculates line_number from newlines before match start
- [ ] Creates FunctionInfo with all fields populated
- [ ] Sets is_static from static keyword presence

**Related Requirements:** SWR_MODEL_00004, SWR_PARSER_C_00001, SWR_PARSER_C_00006, SWR_PARSER_C_00008, SWR_PARSER_C_00009

---

### SWR_PARSER_C_00011: Static Function Detection

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall detect the `static` keyword in function declarations and set the is_static flag accordingly.

**Rationale:**
Static functions have file-local scope and cannot be called from other files. This information is critical for the smart function lookup strategy when resolving multiple definitions.

**Acceptance Criteria:**
- [ ] Detects `static` keyword in function pattern
- [ ] Sets is_static=True when static keyword present
- [ ] Sets is_static=False when static keyword absent
- [ ] Stores is_static in FunctionInfo object

**Related Requirements:** SWR_MODEL_00004

---

### SWR_PARSER_C_00012: Line Number Calculation

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall calculate the line number of function declarations by counting newlines before the match position.

**Rationale:**
Line numbers are essential for error reporting, code navigation, and unique identification of static functions. The parser counts newline characters from file start to match position.

**Acceptance Criteria:**
- [ ] Counts newlines in content before match.start()
- [ ] Adds 1 to convert from 0-indexed to 1-indexed line numbers
- [ ] Returns accurate line number for FunctionInfo

**Related Requirements:** SWR_MODEL_00004

---

### SWR_PARSER_C_00013: Progressive Enhancement Strategy

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall implement progressive enhancement by trying AUTOSAR parsing first, then falling back to traditional C parsing.

**Rationale:**
AUTOSAR codebases contain both AUTOSAR macro declarations and traditional C functions. Trying AUTOSAR first ensures complex macros are parsed correctly. Traditional C fallback handles remaining functions. Deduplication prevents double-counting.

**Acceptance Criteria:**
- [ ] Checks for FUNC macros in file content
- [ ] Only runs AUTOSAR parser if FUNC macros present (optimization)
- [ ] Parses AUTOSAR functions line by line
- [ ] Extracts function bodies and calls for AUTOSAR functions too
- [ ] Parses traditional C functions from entire file
- [ ] Detects duplicates by name and line_number
- [ ] Returns combined list of unique functions

**Related Requirements:** SWR_PARSER_AUTOSAR_00011, SWR_PARSER_C_00004

---

### SWR_PARSER_C_00014: AUTOSAR Parser Integration

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall instantiate and use AutosarParser for AUTOSAR macro handling.

**Rationale:**
AUTOSAR parsing logic is encapsulated in AutosarParser. The C parser delegates to it rather than duplicating code. This separation of concerns maintains modularity.

**Acceptance Criteria:**
- [ ] Instantiates AutosarParser in __init__
- [ ] Delegates to autosar_parser.parse_function_declaration for AUTOSAR functions
- [ ] Extracts function bodies for AUTOSAR functions using _extract_function_body
- [ ] Extracts function calls for AUTOSAR functions using _extract_function_calls
- [ ] Sets calls field on AUTOSAR FunctionInfo objects

**Related Requirements:** SWR_PARSER_AUTOSAR_00011, SWR_PARSER_C_00004

---

### SWR_PARSER_C_00015: Single Declaration Parsing

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall provide `parse_function_declaration` method to parse a single function declaration string.

**Rationale:**
This method enables testing and manual parsing of individual declarations without requiring a full file. It's a convenience wrapper around the main parsing logic.

**Acceptance Criteria:**
- [ ] Accepts declaration string parameter
- [ ] Searches for function pattern in declaration
- [ ] Returns None if pattern doesn't match
- [ ] Calls _parse_function_match with found match
- [ ] Uses "unknown" as file_path (since no file provided)
- [ ] Returns FunctionInfo object or None

**Related Requirements:** SWR_PARSER_C_00001, SWR_PARSER_C_00010

---

### SWR_PARSER_C_00016: Preprocessor Directive Filtering

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall skip preprocessor directives that may match the function pattern.

**Rationale:**
Preprocessor directives like `#define FUNC(x) ...` can match the function pattern. These must be filtered out to avoid false positives.

**Acceptance Criteria:**
- [ ] Checks if return_type starts with "#"
- [ ] Returns None from _parse_function_match if preprocessor detected
- [ ] Prevents parsing of #define, #ifdef, #ifndef, #include, etc.

**Related Requirements:** SWR_PARSER_C_00001, SWR_PARSER_C_00010

---

### SWR_PARSER_C_00017: Pointer Parameter Detection

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall detect pointer parameters in traditional C parameter declarations.

**Rationale:**
Pointer parameters are indicated by asterisk in the type (e.g., `uint8* buffer`). The is_pointer flag is used for signature generation and API documentation.

**Acceptance Criteria:**
- [ ] Detects asterisk character in parameter type string
- [ ] Sets is_pointer=True in Parameter when asterisk present
- [ ] Sets is_pointer=False when asterisk absent
- [ ] Strips trailing asterisk from type before storing

**Related Requirements:** SWR_MODEL_00002, SWR_PARSER_C_00006

---

### SWR_PARSER_C_00018: FunctionInfo Creation for C Functions

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall create properly populated FunctionInfo objects for traditional C functions.

**Rationale:**
FunctionInfo objects must be consistent regardless of parsing method. Traditional C functions have specific field values (function_type=TRADITIONAL_C, no memory_class, no macro_type).

**Acceptance Criteria:**
- [ ] Sets name from extracted function name
- [ ] Sets return_type (without pointer asterisk cleanup)
- [ ] Sets file_path from parameter
- [ ] Sets line_number from calculation
- [ ] Sets is_static from static keyword detection
- [ ] Sets function_type to TRADITIONAL_C
- [ ] Sets memory_class to None (not applicable for C functions)
- [ ] Sets macro_type to None (not applicable for C functions)
- [ ] Sets parameters from _parse_parameters result
- [ ] Sets calls from _extract_function_calls result

**Related Requirements:** SWR_MODEL_00004, SWR_MODEL_00005, SWR_MODEL_00006

---

### SWR_PARSER_C_00019: Line-by-Line Processing

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall process file content line-by-line to avoid catastrophic backtracking on large files.

**Rationale:**
Using `finditer()` on the entire file content can cause catastrophic backtracking when the regex matches long, complex lines. Processing line-by-line limits the matching scope and prevents performance issues with large files (1000+ functions).

**Acceptance Criteria:**
- [ ] Splits file content into lines before matching
- [ ] Tracks current position for accurate match offsets
- [ ] Creates AdjustedMatch wrapper to correct match positions
- [ ] Filters lines that don't look like function declarations (no parenthesis or has semicolon)
- [ ] Processes each line independently
- [ ] Adjusts match.start() and match.end() to account for cumulative offset
- [ ] Handles files with 1000+ functions without performance degradation

**Related Requirements:** SWR_PARSER_C_00001, SWR_PARSER_C_00013

---

### SWR_PARSER_C_00020: Regex Optimization with Length Limits

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall use regex patterns with explicit length limits to prevent catastrophic backtracking and ReDoS (Regular Expression Denial of Service).

**Rationale:**
Unbounded regex patterns like `[\w\s\*]+` can cause exponential backtracking on malicious or complex input. Adding quantifier limits (e.g., `{1,100}`) bounds the matching time and prevents performance issues.

**Acceptance Criteria:**
- [ ] Return type pattern limited to 1-100 characters
- [ ] Function name pattern limited to 1-50 characters
- [ ] Parameter pattern limited to 0-500 characters (excluding nested parentheses)
- [ ] Nested parentheses in parameters limited to 0-100 characters each
- [ ] Patterns still match all valid traditional C function declarations
- [ ] Patterns reject extremely long identifiers that would be invalid in C
- [ ] No catastrophic backtracking on large files

**Related Requirements:** SWR_PARSER_C_00001, SWR_PARSER_C_00019

---

### SWR_PARSER_C_00021: Loop Detection

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall detect for and while loops in function bodies and mark function calls inside loops as loop calls.

**Rationale:**
Loops are common control structures in C code where the same function is called repeatedly. Distinguishing loop calls from regular calls allows for better visualization in sequence diagrams using loop blocks.

**Acceptance Criteria:**
- [ ] Detects `for` loops with syntax `for (init; condition; increment)`
- [ ] Detects `while` loops with syntax `while (condition)`
- [ ] Extracts loop condition from for statements (middle part between semicolons)
- [ ] Extracts loop condition from while statements (content inside parentheses)
- [ ] Sets `is_loop=True` on FunctionCall objects for calls inside loops
- [ ] Stores loop condition in `loop_condition` field
- [ ] Tracks loop context using brace depth to handle nested blocks
- [ ] Resets loop context when exiting the loop block

**Related Requirements:** SWR_MODEL_00026, SWR_PARSER_C_00022

---

### SWR_PARSER_C_00022: Multi-line If Condition Extraction

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall extract complete conditions from multi-line if/else statements.

**Rationale:**
AUTOSAR code often uses multi-line conditions with logical operators (&&, ||) and nested parentheses. The parser must capture the complete condition across multiple lines for accurate opt block generation.

**Acceptance Criteria:**
- [ ] Detects incomplete regex matches (unbalanced parentheses) in if conditions
- [ ] Falls back to multi-line condition collection when regex match is incomplete
- [ ] Tracks parenthesis depth to find matching closing parenthesis
- [ ] Extracts complete condition including nested parentheses
- [ ] Handles multi-line conditions with && and || operators
- [ ] Handles multi-line conditions with complex nested parentheses
- [ ] Stores complete condition string in `condition` field

**Related Requirements:** SWR_MODEL_00026, SWR_PARSER_C_00021

---

### SWR_PARSER_C_00023: Multi-line Function Call Extraction

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The C parser shall extract function calls that span multiple lines within function bodies.

**Rationale:**
AUTOSAR codebases often use multi-line function calls for readability, especially with long parameter lists or complex expressions. For example:

```c
void ExampleFunction(void) {
    // Multi-line call with multiple parameters
    VeryLongFunctionName(
        parameter1,
        parameter2,
        parameter3
    );

    // Multi-line call in conditional
    if (status == OK) {
        ProcessData(
            buffer,
            length,
            flags
        );
    }
}
```

The regex-based pattern matching (`identifier(`) naturally finds function calls regardless of line breaks, ensuring these calls are correctly extracted.

**Acceptance Criteria:**
- [ ] Detects function calls where opening parenthesis is on one line
- [ ] Detects function calls where parameters span multiple lines
- [ ] Detects function calls where closing parenthesis is on a different line
- [ ] Handles multi-line calls with nested function calls as parameters
- [ ] Handles multi-line calls within if/else blocks
- [ ] Handles multi-line calls within for/while loops
- [ ] Extracts only the function name (not parameters)
- [ ] Deduplicates function calls across multiple lines

**Related Requirements:** SWR_PARSER_C_00009

---

## Traceability

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_PARSER_C_00001 | SWUT_PARSER_C_00001 | test_SWUT_PARSER_C_00001_traditional_c_function_pattern | ⏳ Pending |
| SWR_PARSER_C_00002 | SWUT_PARSER_C_00002 | test_SWUT_PARSER_C_00002_c_keyword_filtering | ⏳ Pending |
| SWR_PARSER_C_00003 | SWUT_PARSER_C_00003 | test_SWUT_PARSER_C_00003_autosar_type_filtering | ⏳ Pending |
| SWR_PARSER_C_00004 | SWUT_PARSER_C_00004 | test_SWUT_PARSER_C_00004_file_level_parsing | ⏳ Pending |
| SWR_PARSER_C_00005 | SWUT_PARSER_C_00005 | test_SWUT_PARSER_C_00005_comment_removal | ⏳ Pending |
| SWR_PARSER_C_00006 | SWUT_PARSER_C_00006 | test_SWUT_PARSER_C_00006_parameter_string_parsing | ⏳ Pending |
| SWR_PARSER_C_00007 | SWUT_PARSER_C_00007 | test_SWUT_PARSER_C_00007_smart_split_parameters | ⏳ Pending |
| SWR_PARSER_C_00008 | SWUT_PARSER_C_00008 | test_SWUT_PARSER_C_00008_function_body_extraction | ⏳ Pending |
| SWR_PARSER_C_00009 | SWUT_PARSER_C_00009 | test_SWUT_PARSER_C_00009_function_call_extraction | ⏳ Pending |
| SWR_PARSER_C_00010 | SWUT_PARSER_C_00010 | test_SWUT_PARSER_C_00010_function_match_parsing | ⏳ Pending |
| SWR_PARSER_C_00011 | SWUT_PARSER_C_00011 | test_SWUT_PARSER_C_00011_static_function_detection | ⏳ Pending |
| SWR_PARSER_C_00012 | SWUT_PARSER_C_00012 | test_SWUT_PARSER_C_00012_line_number_calculation | ⏳ Pending |
| SWR_PARSER_C_00013 | SWUT_PARSER_C_00013 | test_SWUT_PARSER_C_00013_progressive_enhancement_strategy | ⏳ Pending |
| SWR_PARSER_C_00014 | SWUT_PARSER_C_00014 | test_SWUT_PARSER_C_00014_autosar_parser_integration | ⏳ Pending |
| SWR_PARSER_C_00015 | SWUT_PARSER_C_00015 | test_SWUT_PARSER_C_00015_single_declaration_parsing | ⏳ Pending |
| SWR_PARSER_C_00016 | SWUT_PARSER_C_00016 | test_SWUT_PARSER_C_00016_preprocessor_directive_filtering | ⏳ Pending |
| SWR_PARSER_C_00017 | SWUT_PARSER_C_00017 | test_SWUT_PARSER_C_00017_pointer_parameter_detection | ⏳ Pending |
| SWR_PARSER_C_00018 | SWUT_PARSER_C_00018 | test_SWUT_PARSER_C_00018_functioninfo_creation_c_functions | ⏳ Pending |
| SWR_PARSER_C_00019 | SWUT_PARSER_C_00019 | test_SWUT_PARSER_C_00019_line_by_line_processing | ⏳ Pending |
| SWR_PARSER_C_00020 | SWUT_PARSER_C_00020 | test_SWUT_PARSER_C_00020_regex_optimization_length_limits | ⏳ Pending |
| SWR_PARSER_C_00021 | SWUT_PARSER_C_00023 | test_loop_detection_for | ✅ Pass |
| SWR_PARSER_C_00021 | SWUT_PARSER_C_00024 | test_loop_detection_while | ✅ Pass |
| SWR_PARSER_C_00021 | SWUT_PARSER_C_00025 | test_loop_multiple_calls | ✅ Pass |
| SWR_PARSER_C_00021 | SWUT_PARSER_C_00026 | test_loop_with_condition | ✅ Pass |
| SWR_PARSER_C_00022 | SWUT_PARSER_C_00021 | test_SWUT_PARSER_C_00021_multiline_function_prototype | ✅ Pass |
| SWR_PARSER_C_00022 | SWUT_PARSER_C_00022 | test_SWUT_PARSER_C_00022_multiline_if_condition | ✅ Pass |
| SWR_PARSER_C_00023 | SWUT_PARSER_C_00028 | test_multiline_function_call_extraction | ✅ Pass |

## Revision History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-01-30 | 1.0 | Claude | Initial version - 18 requirements covering C parser functionality |
| 2026-01-30 | 1.1 | Claude | Added requirements for line-by-line processing (SWR_PARSER_C_00019) and regex optimization (SWR_PARSER_C_00020) to prevent catastrophic backtracking on large files |
| 2026-02-09 | 1.2 | Claude | Added requirements for multi-line function prototypes (SWR_PARSER_C_00021) and multi-line if condition extraction (SWR_PARSER_C_00022) |
| 2026-02-09 | 1.3 | Claude | Added requirement for loop detection (SWR_PARSER_C_00021) with 4 tests |
| 2026-02-10 | 1.4 | Claude | Added requirement for multi-line function call extraction (SWR_PARSER_C_00023) |
