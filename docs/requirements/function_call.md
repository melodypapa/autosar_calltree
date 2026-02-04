# FunctionCall Model Requirements

## SWR_MODEL_00026: FunctionCall Dataclass - Conditional Tracking

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description**:
The system shall provide a FunctionCall dataclass to represent function calls with conditional status tracking for opt block generation.

**Rationale**:
Function calls inside `if`/`else` statements represent conditional execution paths that should be displayed in Mermaid `opt` blocks. The FunctionCall class tracks both the function name and whether it's conditional, enabling automatic opt block generation without manual configuration.

**Acceptance Criteria**:
- [ ] Has field `name: str` for the called function name
- [ ] Has field `is_conditional: bool` defaulting to False
- [ ] Has field `condition: Optional[str]` defaulting to None for the if/else condition text
- [ ] Provides `__str__` method for readable representation

**Related Requirements:** SWR_MERMAID_00004

---

## SWR_MODEL_00027: FunctionCall Dataclass - String Representation

**Priority:** Low
**Status:** Implemented
**Maturity:** accept

**Description**:
The FunctionCall dataclass shall provide `__str__` method for human-readable display.

**Rationale**:
Debugging and logging require readable string representation of function calls. The method indicates conditional status in the output.

**Acceptance Criteria**:
- [ ] Returns format "{name}" for non-conditional calls
- [ ] Returns format "{name} [conditional]" for conditional calls

**Related Requirements:** SWR_MODEL_00026

---

## SWR_MODEL_00028: CallTreeNode Dataclass - Optional Call Tracking

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description**:
The CallTreeNode dataclass shall include fields for tracking optional calls and their conditions.

**Rationale**:
Opt block generation requires knowing which calls are conditional and what condition text to display. These fields enable the MermaidGenerator to automatically generate meaningful opt blocks.

**Acceptance Criteria**:
- [ ] Has field `is_optional: bool` defaulting to False for opt block generation
- [ ] Has field `condition: Optional[str]` defaulting to None for opt block label

**Related Requirements:** SWR_MERMAID_00004, SWR_MODEL_00026

---

## Traceability

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_MODEL_00026 | SWUT_MODEL_00026 | test_SWUT_MODEL_00026_function_call_conditional_tracking | ✅ Implemented |
| SWR_MODEL_00027 | SWUT_MODEL_00027 | test_SWUT_MODEL_00027_function_call_string_representation | ✅ Implemented |
| SWR_MODEL_00028 | SWUT_MODEL_00028 | test_SWUT_MODEL_00028_call_tree_node_optional_tracking | ✅ Implemented |

## Revision History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-02-04 | 1.0 | Claude | Initial version - FunctionCall model for conditional call tracking |