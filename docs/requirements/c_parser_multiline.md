# C Parser Multi-line Support Requirements

## Overview
The C parser module shall support multi-line function prototypes and multi-line if statement condition extraction to handle real-world code formatting styles commonly used in AUTOSAR codebases.

## Requirements

### SWR_PARSER_C_00021: Multi-line Function Prototype Recognition

**Priority:** High
**Status:** Proposed
**Maturity:** draft

**Description:**
The C parser shall recognize function prototypes that span multiple lines, where the return type, function name, and parameters may be on different lines.

**Rationale:**
Many AUTOSAR codebases use multi-line function declarations for readability, especially with long parameter lists or complex return types. For example:

```c
Std_ReturnType
COM_SendMessage(uint32 messageId,
                uint8* data,
                uint16 length)
```

Currently, the parser only matches functions where the entire declaration is on a single line, causing these functions to be missed.

**Acceptance Criteria:**
- [ ] Detects function prototypes spanning 2 or more lines
- [ ] Handles return type on separate line from function name
- [ ] Handles function name on separate line from opening parenthesis
- [ ] Handles parameters spanning multiple lines
- [ ] Extracts correct line number (line where function name appears)
- [ ] Extracts correct return type, function name, and parameters
- [ ] Maintains performance with line-by-line processing
- [ ] Works with both traditional C and AUTOSAR functions

**Related Requirements:** SWR_PARSER_C_00001, SWR_PARSER_C_00004

---

### SWR_PARSER_C_00022: Multi-line If Condition Extraction

**Priority:** High
**Status:** Proposed
**Maturity:** draft

**Description:**
The C parser shall extract complete condition text from if/else if statements that span multiple lines.

**Rationale:**
Complex conditions are often written across multiple lines for readability. Currently, the parser only extracts conditions that are on the same line as the `if` keyword. For example:

```c
if (update_mode == 0x05 &&
    data_length > 10) {
    COM_SendMessage(msgId, data);
}
```

Currently only extracts `"update_mode == 0x05 &&"` instead of the full condition.

**Acceptance Criteria:**
- [ ] Extracts complete condition spanning multiple lines
- [ ] Tracks condition parentheses to find closing `)`
- [ ] Handles line continuations with backslash
- [ ] Handles conditions with logical operators (&&, ||)
- [ ] Handles nested parentheses in conditions
- [ ] Preserves exact condition text (whitespace included)
- [ ] Works with `if`, `else if`, and `else` statements
- [ ] Falls back to single-line extraction if closing paren not found

**Related Requirements:** SWR_PARSER_C_00009

---

## Traceability

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_PARSER_C_00021 | SWUT_PARSER_C_00021 | test_SWUT_PARSER_C_00021_multiline_function_prototype | ⏳ Pending |
| SWR_PARSER_C_00022 | SWUT_PARSER_C_00022 | test_SWUT_PARSER_C_00022_multiline_if_condition | ⏳ Pending |

## Revision History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-02-09 | 1.0 | iFlow CLI | Initial version - Requirements for multi-line support |