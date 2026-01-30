# AUTOSAR Parser Requirements

## Overview
The AUTOSAR parser module provides specialized parsing capabilities for AUTOSAR macro-based function declarations. Traditional C parsers cannot handle AUTOSAR's proprietary macro syntax (FUNC, FUNC_P2VAR, FUNC_P2CONST, VAR, P2VAR, P2CONST, CONST). This parser uses regex patterns to extract function signatures, parameters, return types, and memory classes from AUTOSAR source code.

## Requirements

### SWR_PARSER_AUTOSAR_00001: FUNC Macro Pattern Recognition

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The AUTOSAR parser shall recognize and parse FUNC macro declarations in the format `FUNC(return_type, memory_class) function_name(parameters)`.

**Rationale:**
FUNC is the most common AUTOSAR macro for function declarations. It specifies return type and memory class (e.g., RTE_CODE, AUTOMATIC) which are critical for accurate function signatures. Traditional C parsers misinterpret these macros as preprocessor directives.

**Acceptance Criteria:**
- [ ] Pattern matches `FUNC(void, RTE_CODE) Demo_Init(void)`
- [ ] Pattern matches `FUNC(uint32, AUTOMATIC) HW_ReadSensor(VAR(uint32, AUTOMATIC) sensor_id)`
- [ ] Pattern matches `STATIC FUNC(uint8, CODE) Internal_Function(void)`
- [ ] Extracts return_type from first macro parameter
- [ ] Extracts memory_class from second macro parameter
- [ ] Extracts function_name after closing parenthesis
- [ ] Detects optional STATIC keyword prefix

**Related Requirements:** SWR_PARSER_AUTOSAR_00004, SWR_PARSER_AUTOSAR_00005

---

### SWR_PARSER_AUTOSAR_00002: FUNC_P2VAR Macro Pattern Recognition

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The AUTOSAR parser shall recognize and parse FUNC_P2VAR macro declarations for functions returning non-const pointers.

**Rationale:**
FUNC_P2VAR indicates functions returning pointers to writable memory. The pointer class (second parameter) and memory class (third parameter) are essential for memory layout analysis. Return type must be formatted as "type*" in FunctionInfo.

**Acceptance Criteria:**
- [ ] Pattern matches `FUNC_P2VAR(uint8, AUTOMATIC, Demo_VAR) GetBuffer(void)`
- [ ] Extracts return_type from first macro parameter
- [ ] Extracts ptr_class from second macro parameter
- [ ] Extracts memory_class from third macro parameter
- [ ] Formats return_type as "{return_type}*" (e.g., "uint8*")
- [ ] Sets function_type to AUTOSAR_FUNC_P2VAR

**Related Requirements:** SWR_PARSER_AUTOSAR_00001

---

### SWR_PARSER_AUTOSAR_00003: FUNC_P2CONST Macro Pattern Recognition

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The AUTOSAR parser shall recognize and parse FUNC_P2CONST macro declarations for functions returning const pointers.

**Rationale:**
FUNC_P2CONST indicates functions returning pointers to read-only memory. The const qualifier is critical for API documentation and preventing accidental writes. Return type must be formatted as "const type*" in FunctionInfo.

**Acceptance Criteria:**
- [ ] Pattern matches `FUNC_P2CONST(ConfigType, AUTOMATIC, APPL_VAR) GetConfig(void)`
- [ ] Extracts return_type from first macro parameter
- [ ] Extracts ptr_class from second macro parameter
- [ ] Extracts memory_class from third macro parameter
- [ ] Formats return_type as "const {return_type}*" (e.g., "const ConfigType*")
- [ ] Sets function_type to AUTOSAR_FUNC_P2CONST

**Related Requirements:** SWR_PARSER_AUTOSAR_00001

---

### SWR_PARSER_AUTOSAR_00004: Parameter String Extraction

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The AUTOSAR parser shall extract parameter strings from function declarations, handling nested parentheses in complex parameter types.

**Rationale:**
Function parameters may contain function pointers or array types with nested parentheses. Simple string splitting would fail on `void (*callback)(int)` or `extern_func(int, uint32)`. Balanced parenthesis matching ensures correct extraction.

**Acceptance Criteria:**
- [ ] Locates opening parenthesis after function name
- [ ] Tracks parenthesis depth to find matching closing parenthesis
- [ ] Returns content inside parentheses (excluding outer parens)
- [ ] Handles empty parameter lists `void`
- [ ] Handles single parameter `VAR(uint32, AUTOMATIC) value`
- [ ] Handles multiple parameters with commas
- [ ] Handles nested parentheses in parameter types

**Related Requirements:** SWR_PARSER_AUTOSAR_00001, SWR_PARSER_AUTOSAR_00005

---

### SWR_PARSER_AUTOSAR_00005: VAR Parameter Pattern Recognition

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The AUTOSAR parser shall recognize and parse VAR macro parameters in the format `VAR(type, memory_class) name`.

**Rationale:**
VAR is the standard AUTOSAR macro for value parameters. It specifies type and memory class (AUTOMATIC, APPL_DATA, etc.) which are important for memory allocation analysis. Parameters must be extracted with is_pointer=False, is_const=False.

**Acceptance Criteria:**
- [ ] Pattern matches `VAR(uint32, AUTOMATIC) config_mode`
- [ ] Pattern matches `VAR(uint8, APPL_DATA) value`
- [ ] Extracts parameter type (e.g., "uint32")
- [ ] Extracts memory class (e.g., "AUTOMATIC")
- [ ] Extracts parameter name
- [ ] Creates Parameter with is_pointer=False, is_const=False
- [ ] Stores memory_class in Parameter object

**Related Requirements:** SWR_MODEL_00002

---

### SWR_PARSER_AUTOSAR_00006: P2VAR Parameter Pattern Recognition

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The AUTOSAR parser shall recognize and parse P2VAR macro parameters for non-const pointer parameters.

**Rationale:**
P2VAR indicates pointer parameters to writable memory. The pointer class and memory class are essential for understanding data flow and potential side effects. Parameters must be extracted with is_pointer=True, is_const=False.

**Acceptance Criteria:**
- [ ] Pattern matches `P2VAR(uint8, AUTOMATIC, APPL_DATA) buffer`
- [ ] Pattern matches `P2VAR(ConfigType, RTE_VAR, APPL_DATA) config`
- [ ] Extracts parameter type (e.g., "uint8")
- [ ] Extracts pointer class (second parameter)
- [ ] Extracts memory class (third parameter)
- [ ] Extracts parameter name
- [ ] Creates Parameter with is_pointer=True, is_const=False
- [ ] Stores memory_class in Parameter object

**Related Requirements:** SWR_MODEL_00002

---

### SWR_PARSER_AUTOSAR_00007: P2CONST Parameter Pattern Recognition

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The AUTOSAR parser shall recognize and parse P2CONST macro parameters for const pointer parameters.

**Rationale:**
P2CONST indicates pointer parameters to read-only memory. This is critical for API contracts and preventing buffer overwrites. Parameters must be extracted with is_pointer=True, is_const=True.

**Acceptance Criteria:**
- [ ] Pattern matches `P2CONST(uint8, AUTOMATIC, APPL_CONST) data`
- [ ] Pattern matches `P2CONST(ConfigType, RTE_CONST, APPL_DATA) config`
- [ ] Extracts parameter type (e.g., "uint8")
- [ ] Extracts pointer class (second parameter)
- [ ] Extracts memory class (third parameter)
- [ ] Extracts parameter name
- [ ] Creates Parameter with is_pointer=True, is_const=True
- [ ] Stores memory_class in Parameter object

**Related Requirements:** SWR_MODEL_00002

---

### SWR_PARSER_AUTOSAR_00008: CONST Parameter Pattern Recognition

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The AUTOSAR parser shall recognize and parse CONST macro parameters for const value parameters.

**Rationale:**
CONST indicates const value parameters (not pointers). These are pass-by-value with read-only semantics. Parameters must be extracted with is_pointer=False, is_const=True.

**Acceptance Criteria:**
- [ ] Pattern matches `CONST(uint32, AUTOMATIC) timeout`
- [ ] Pattern matches `CONST(uint16, RTE_CONST) max_retries`
- [ ] Extracts parameter type (e.g., "uint32")
- [ ] Extracts memory class (e.g., "AUTOMATIC")
- [ ] Extracts parameter name
- [ ] Creates Parameter with is_pointer=False, is_const=True
- [ ] Stores memory_class in Parameter object

**Related Requirements:** SWR_MODEL_00002

---

### SWR_PARSER_AUTOSAR_00009: Traditional C Parameter Fallback

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
When AUTOSAR macro patterns don't match, the parser shall fall back to traditional C parameter parsing for mixed declarations.

**Rationale:**
AUTOSAR code may mix AUTOSAR macros with traditional C syntax (e.g., `uint8* buffer` or `const ConfigType* config`). The fallback ensures all parameters are captured regardless of declaration style.

**Acceptance Criteria:**
- [ ] Detects const keyword in parameter string
- [ ] Detects asterisk for pointer types
- [ ] Splits type and name by rightmost space
- [ ] Handles `uint8* buffer` as pointer type
- [ ] Handles `const ConfigType* config` as const pointer
- [ ] Handles parameters with no name (type-only declarations)
- [ ] Creates Parameter with correct is_pointer and is_const flags

**Related Requirements:** SWR_MODEL_00002

---

### SWR_PARSER_AUTOSAR_00010: Parameter List Splitting

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The parser shall split parameter lists by comma while respecting nested parentheses in parameter types.

**Rationale:**
Parameters may contain function pointers or macro invocations with commas. Simple `split(',')` would incorrectly split `VAR(uint32, AUTOMATIC), VAR(uint8, AUTOMATIC)` into 4 parts instead of 2. Parenthesis depth tracking ensures correct splitting.

**Acceptance Criteria:**
- [ ] Splits `VAR(uint32, AUTOMATIC) value, VAR(uint8, AUTOMATIC) data` into 2 parameters
- [ ] Tracks parenthesis depth during splitting
- [ ] Only splits on commas at depth 0 (outside nested parens)
- [ ] Handles empty parameter strings
- [ ] Handles parameters with function pointers
- [ ] Handles parameters with nested macros

**Related Requirements:** SWR_PARSER_AUTOSAR_00005, SWR_PARSER_AUTOSAR_00006

---

### SWR_PARSER_AUTOSAR_00011: Function Declaration Parsing

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The parser shall provide `parse_function_declaration` method that attempts all AUTOSAR patterns and returns a FunctionInfo object.

**Rationale:**
This is the primary entry point for parsing individual function declarations. It must try FUNC, FUNC_P2VAR, and FUNC_P2CONST patterns in order, returning None if none match. This allows the progressive enhancement strategy (try AUTOSAR first, fall back to C parser).

**Acceptance Criteria:**
- [ ] Accepts line, file_path, and line_number parameters
- [ ] Tries FUNC pattern first
- [ ] Tries FUNC_P2VAR pattern if FUNC fails
- [ ] Tries FUNC_P2CONST pattern if FUNC_P2VAR fails
- [ ] Returns FunctionInfo with all fields populated
- [ ] Returns None if no patterns match
- [ ] Sets is_static=True if STATIC prefix detected
- [ ] Calls parse_parameters to extract parameter list
- [ ] Sets macro_type field ("FUNC", "FUNC_P2VAR", "FUNC_P2CONST")

**Related Requirements:** SWR_PARSER_AUTOSAR_00001, SWR_PARSER_AUTOSAR_00002, SWR_PARSER_AUTOSAR_00003

---

### SWR_PARSER_AUTOSAR_00012: AUTOSAR Function Detection

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The parser shall provide `is_autosar_function` method to quickly check if a line contains any AUTOSAR function macro.

**Rationale:**
This check enables efficient parsing strategies. Files without AUTOSAR macros can skip AUTOSAR parsing entirely, improving performance on traditional C code.

**Acceptance Criteria:**
- [ ] Returns True if FUNC pattern matches
- [ ] Returns True if FUNC_P2VAR pattern matches
- [ ] Returns True if FUNC_P2CONST pattern matches
- [ ] Returns False if no AUTOSAR patterns match
- [ ] Used for early exit in progressive enhancement

**Related Requirements:** SWR_PARSER_AUTOSAR_00001, SWR_PARSER_AUTOSAR_00002, SWR_PARSER_AUTOSAR_00003

---

### SWR_PARSER_AUTOSAR_00013: Empty Parameter List Handling

**Priority:** Low
**Status:** Implemented
**Maturity:** accept

**Description:**
The parser shall correctly handle functions with no parameters (void parameter list).

**Rationale:**
AUTOSAR functions with no parameters are declared as `FUNC(void, RTE_CODE) FunctionName(void)`. The parser must recognize this and return an empty parameter list, not a parameter with type "void" and no name.

**Acceptance Criteria:**
- [ ] Recognizes `void` as empty parameter list
- [ ] Recognizes empty string as empty parameter list
- [ ] Returns empty list ([]) for void parameters
- [ ] Does not create Parameter objects for void

**Related Requirements:** SWR_PARSER_AUTOSAR_00005

---

### SWR_PARSER_AUTOSAR_00014: Whitespace Tolerance

**Priority:** Low
**Status:** Implemented
**Maturity:** accept

**Description:**
The parser shall handle variable whitespace in AUTOSAR macro declarations.

**Rationale:**
Different code formatting styles may insert extra spaces in macros (e.g., `FUNC( void , RTE_CODE )` vs `FUNC(void, RTE_CODE)`). The parser must be robust to these variations.

**Acceptance Criteria:**
- [ ] Handles spaces after FUNC macro opening parenthesis
- [ ] Handles spaces before macro commas
- [ ] Handles spaces after macro commas
- [ ] Handles spaces before function name
- [ ] Strips whitespace from extracted values
- [ ] Works with both well-formatted and poorly-formatted code

**Related Requirements:** SWR_PARSER_AUTOSAR_00001

---

### SWR_PARSER_AUTOSAR_00015: FunctionInfo Object Creation

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The parser shall create properly populated FunctionInfo objects for all AUTOSAR function types.

**Rationale:**
FunctionInfo objects are the core data structure for all downstream analysis. All fields must be correctly populated to enable call tree construction, signature generation, and statistics tracking.

**Acceptance Criteria:**
- [ ] Sets name from extracted function name
- [ ] Sets return_type with pointer asterisk for P2VAR/P2CONST
- [ ] Sets file_path from parameter
- [ ] Sets line_number from parameter
- [ ] Sets is_static from STATIC prefix detection
- [ ] Sets function_type to appropriate AUTOSAR enum value
- [ ] Sets memory_class from macro parameter
- [ ] Sets macro_type to macro name ("FUNC", "FUNC_P2VAR", "FUNC_P2CONST")
- [ ] Sets parameters from parse_parameters result

**Related Requirements:** SWR_MODEL_00004, SWR_MODEL_00005, SWR_MODEL_00006

---

## Traceability

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_PARSER_AUTOSAR_00001 | SWUT_PARSER_AUTOSAR_00001 | test_SWUT_PARSER_AUTOSAR_00001_func_macro_pattern | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00002 | SWUT_PARSER_AUTOSAR_00002 | test_SWUT_PARSER_AUTOSAR_00002_func_p2var_macro_pattern | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00003 | SWUT_PARSER_AUTOSAR_00003 | test_SWUT_PARSER_AUTOSAR_00003_func_p2const_macro_pattern | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00004 | SWUT_PARSER_AUTOSAR_00004 | test_SWUT_PARSER_AUTOSAR_00004_parameter_string_extraction | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00005 | SWUT_PARSER_AUTOSAR_00005 | test_SWUT_PARSER_AUTOSAR_00005_var_parameter_pattern | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00006 | SWUT_PARSER_AUTOSAR_00006 | test_SWUT_PARSER_AUTOSAR_00006_p2var_parameter_pattern | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00007 | SWUT_PARSER_AUTOSAR_00007 | test_SWUT_PARSER_AUTOSAR_00007_p2const_parameter_pattern | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00008 | SWUT_PARSER_AUTOSAR_00008 | test_SWUT_PARSER_AUTOSAR_00008_const_parameter_pattern | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00009 | SWUT_PARSER_AUTOSAR_00009 | test_SWUT_PARSER_AUTOSAR_00009_traditional_c_parameter_fallback | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00010 | SWUT_PARSER_AUTOSAR_00010 | test_SWUT_PARSER_AUTOSAR_00010_parameter_list_splitting | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00011 | SWUT_PARSER_AUTOSAR_00011 | test_SWUT_PARSER_AUTOSAR_00011_function_declaration_parsing | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00012 | SWUT_PARSER_AUTOSAR_00012 | test_SWUT_PARSER_AUTOSAR_00012_autosar_function_detection | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00013 | SWUT_PARSER_AUTOSAR_00013 | test_SWUT_PARSER_AUTOSAR_00013_empty_parameter_list_handling | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00014 | SWUT_PARSER_AUTOSAR_00014 | test_SWUT_PARSER_AUTOSAR_00014_whitespace_tolerance | ⏳ Pending |
| SWR_PARSER_AUTOSAR_00015 | SWUT_PARSER_AUTOSAR_00015 | test_SWUT_PARSER_AUTOSAR_00015_functioninfo_object_creation | ⏳ Pending |

## Revision History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-01-30 | 1.0 | Claude | Initial version - 15 requirements covering AUTOSAR parser functionality |
