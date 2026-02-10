# Test Documentation Index

This directory contains test case documentation for the AUTOSAR Call Tree Analyzer project. Each test document maps directly to its corresponding requirements document in `../requirements/`.

## Overview

| Module | Requirements | Test ID Range | Test Count | Status | Coverage |
|--------|-------------|---------------|------------|--------|----------|
| Models | SWR_MODEL_00001-00028 | SWUT_MODEL_00001-00028 | 28 | ✅ Pass | 100% |
| AUTOSAR Parser | SWR_PARSER_AUTOSAR_00001-00015 | SWUT_PARSER_AUTOSAR_00001-00015 | 15 | ✅ Pass | 97% |
| C Parser | SWR_PARSER_C_00001-00023 | SWUT_PARSER_C_00001-00028 | 28 | ✅ Pass | 87% |
| Database | SWR_DB_00001-00025 | SWUT_DB_00001-00021 | 21 | ✅ Pass | 80% |
| Analyzers | SWR_ANALYZER_00001-00020 | SWUT_ANALYZER_00001-00020 | 20 | ✅ Pass | 94% |
| Config | SWR_CONFIG_00001-00010 | SWUT_CONFIG_00001-00025 | 25 | ✅ Pass | 97% |
| Generators (Mermaid) | SWR_GENERATOR_00001-00031, SWR_MERMAID_00001-00005 | SWUT_GENERATOR_00001-00041 | 41 | ✅ Pass | 89% |
| XMI Generator | SWR_XMI_00001-00003 | SWUT_XMI_00001-00003 | 3 | ✅ Pass | 70% |
| CLI | SWR_CLI_00001-00014 | SWUT_CLI_00001-00014 | 14 | ✅ Pass | ~90% |
| E2E | SWR_E2E_00001-00018 | SWUT_E2E_00001-00018 | 18 | ✅ Pass | integration |
| **Total** | **173** | | **213** | **✅ 100% Passing** | **89%** |

## Test Documents by Module

### Data Model Tests

**Requirements Document**: [models.md](../requirements/models.md)

**Test Document**: [models.md](models.md)

- **Requirement IDs**: SWR_MODEL_00001 - SWR_MODEL_00028 (28 requirements)
- **Test IDs**: SWUT_MODEL_00001 - SWUT_MODEL_00028 (28 tests)
- **Coverage**: 100%
- **Key Areas**:
  - FunctionType enum values and validation
  - Parameter dataclass fields and string representation
  - FunctionInfo attributes, equality, hashing, and disambiguation
  - CallTreeNode structure, manipulation, and depth tracking
  - CircularDependency representation
  - AnalysisStatistics and AnalysisResult containers
  - FunctionCall conditional tracking

### AUTOSAR Parser Tests

**Requirements Document**: [autosar_parser.md](../requirements/autosar_parser.md)

**Test Document**: [autosar_parser.md](autosar_parser.md)

- **Requirement IDs**: SWR_PARSER_AUTOSAR_00001 - SWR_PARSER_AUTOSAR_00015 (15 requirements)
- **Test IDs**: SWUT_PARSER_AUTOSAR_00001 - SWUT_PARSER_AUTOSAR_00015 (15 tests)
- **Coverage**: 97%
- **Key Areas**:
  - FUNC, FUNC_P2VAR, FUNC_P2CONST macro pattern recognition
  - Parameter string extraction (VAR, P2VAR, P2CONST, CONST)
  - Function declaration parsing
  - AUTOSAR function detection
  - Empty parameter list handling
  - Whitespace tolerance

### C Parser Tests

**Requirements Document**: [c_parser.md](../requirements/c_parser.md)

**Test Document**: [c_parser.md](c_parser.md)

- **Requirement IDs**: SWR_PARSER_C_00001 - SWR_PARSER_C_00023 (23 requirements)
- **Test IDs**: SWUT_PARSER_C_00001 - SWUT_PARSER_C_00028 (28 tests)
- **Coverage**: 87%
- **Key Areas**:
  - Traditional C function pattern recognition
  - C keyword and AUTOSAR type filtering
  - File-level parsing and comment removal
  - Parameter string parsing and smart splitting
  - Function body and call extraction
  - Static function detection and line number calculation
  - Progressive enhancement strategy
  - Loop detection (SWR_PARSER_C_00021)
  - Multi-line if condition extraction (SWR_PARSER_C_00022)
  - Multi-line function call extraction (SWR_PARSER_C_00023)

### Function Database Tests

**Requirements Document**: [function_database.md](../requirements/function_database.md)

**Test Document**: [function_database.md](function_database.md)

- **Requirement IDs**: SWR_DB_00001 - SWR_DB_00025 (25 requirements)
- **Test IDs**: SWUT_DB_00001 - SWUT_DB_00021 (21 tests)
- **Coverage**: 80%
- **Key Areas**:
  - Database initialization and cache directory creation
  - Three-index structure (functions, qualified_functions, functions_by_file)
  - Source file discovery (.c files only)
  - Smart function lookup strategy (4-level selection)
  - Module configuration integration and statistics
  - Cache metadata validation, save/load, error handling
  - Cache loading progress reporting (file-by-file)
  - Function lookup methods (by name, qualified, search)
  - Parse error collection and database statistics

### Call Tree Analyzer Tests

**Requirements Document**: [call_tree_builder.md](../requirements/call_tree_builder.md)

**Test Document**: [call_tree_builder.md](call_tree_builder.md)

- **Requirement IDs**: SWR_ANALYZER_00001 - SWR_ANALYZER_00020 (20 requirements)
- **Test IDs**: SWUT_ANALYZER_00001 - SWUT_ANALYZER_00020 (20 tests)
- **Coverage**: 94%
- **Key Areas**:
  - Builder initialization and state reset
  - Start function lookup and multiple definition warnings
  - Depth-first traversal algorithm
  - Cycle detection and handling in tree
  - Max depth enforcement and node depth tracking
  - Missing function handling
  - Statistics collection and unique function tracking
  - Qualified name generation
  - Result object creation (success and error cases)
  - Helper methods and text tree generation
  - Verbose progress logging

### Module Configuration Tests

**Requirements Document**: [requirements_module_config.md](../requirements/requirements_module_config.md)

**Test Document**: [module_config.md](module_config.md)

- **Requirement IDs**: SWR_CONFIG_00001 - SWR_CONFIG_00010 (10 requirements)
- **Test IDs**: SWUT_CONFIG_00001 - SWUT_CONFIG_00025 (25 tests)
- **Coverage**: 97%
- **Key Areas**:
  - Configuration loading (valid and missing files)
  - Version validation (missing, wrong type, unsupported)
  - File mappings validation
  - Pattern mappings validation
  - Default module validation
  - Specific file and pattern lookup
  - Lookup caching
  - Statistics calculation
  - Empty configuration initialization

### Mermaid Generator Tests

**Requirements Documents**:
- [requirements_mermaid_modules.md](../requirements/requirements_mermaid_modules.md)
- [requirements_mermaid_opt_blocks.md](../requirements/requirements_mermaid_opt_blocks.md)

**Test Document**: [mermaid_generator.md](mermaid_generator.md)

- **Requirement IDs**: SWR_GENERATOR_00001-00031, SWR_MERMAID_00001-00005 (36 requirements)
- **Test IDs**: SWUT_GENERATOR_00001 - SWUT_GENERATOR_00041 (41 tests)
- **Coverage**: 89%
- **Key Areas**:
  - Initialization (with and without module names)
  - Mermaid diagram header generation
  - Participant collection (function mode, module mode)
  - Module fallback to filename when not mapped
  - RTE abbreviation (enabled and disabled)
  - Sequence calls generation (function mode, module mode, recursive)
  - Parameters on arrows (single, multiple, empty)
  - Return statements in sequence (enabled and disabled)
  - Function table format (with and without modules)
  - Parameter formatting (in table, in diagram)
  - Text tree generation
  - Circular dependencies section
  - Metadata generation
  - File and string output
  - Empty call tree error handling
  - Optional sections control
  - Opt block generation (SWR_MERMAID_00004)
  - Loop block generation (SWR_MERMAID_00005)

### XMI Generator Tests

**Requirements Document**: [requirements_xmi.md](../requirements/requirements_xmi.md)

**Test Document**: [xmi_generator.md](xmi_generator.md)

- **Requirement IDs**: SWR_XMI_00001 - SWR_XMI_00003 (3 requirements)
- **Test IDs**: SWUT_XMI_00001 - SWUT_XMI_00003 (3 tests)
- **Coverage**: 70%
- **Key Areas**:
  - XMI namespace compliance
  - UML 2.5 sequence diagram representation
  - Opt block support for conditional calls

### CLI Tests

**Requirements Document**: [cli.md](../requirements/cli.md)

**Test Document**: [cli.md](cli.md)

- **Requirement IDs**: SWR_CLI_00001 - SWR_CLI_00014 (14 requirements)
- **Test IDs**: SWUT_CLI_00001 - SWUT_CLI_00014 (14 tests)
- **Coverage**: ~90%
- **Key Areas**:
  - Command-line argument parsing
  - Source directory handling
  - Output format selection (mermaid, xmi, both)
  - Start function validation and search
  - Function listing and searching
  - Module configuration integration
  - Cache management (rebuild, use_cache)
  - Progress reporting and error handling

### Integration Tests

**Test Document**: [integration.md](integration.md)

- **Requirement IDs**: SWR_E2E_00001 - SWR_E2E_00018 (18 requirements)
- **Test IDs**: SWUT_E2E_00001 - SWUT_E2E_00018 (18 tests)
- **Type**: Integration tests
- **Key Areas**:
  - Basic workflow (analysis, cache, statistics)
  - Advanced features (module names, parameters, qualified names)
  - Error conditions and edge cases
  - Performance and usability

## Test Coverage

The project achieves **89% overall code coverage** across all modules:

### Coverage Breakdown

```
src/autosar_calltree/database/models.py          100%
src/autosar_calltree/parsers/autosar_parser.py    97%
src/autosar_calltree/parsers/c_parser.py          87%
src/autosar_calltree/database/function_db.py      80%
src/autosar_calltree/analyzers/call_tree.py       94%
src/autosar_calltree/config/module_config.py      97%
src/autosar_calltree/generators/mermaid_gen.py    89%
src/autosar_calltree/generators/xmi_gen.py        70%
src/autosar_calltree/cli/*.py                     ~90%
--------------------------------------------------------
TOTAL                                             89%
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/test_models.py

# Run with coverage
pytest --cov=autosar_calltree --cov-report=html --cov-report=term

# Run specific test case
pytest tests/test_models.py::TestFunctionType::test_function_type_enum_values

# Run with verbose output
pytest -vv -s tests/
```

## Test Case Format

Each test case follows the standard format:

```markdown
### SWUT_XXXXX_YYYYY - Test Case Title

**Requirement:** SWR_XXXXX_YYYYY
**Priority:** High/Medium/Low
**Status:** ✅ Pass / ❌ Fail / ⚠️ Skip

**Test Purpose**:
Description of what this test validates...

**Test Function**: `test_function_name`

**Test Steps**:
1. Setup test data
2. Execute function under test
3. Verify expected behavior

**Expected Result**:
Clear description of expected outcome...

**Edge Cases Covered**:
- Edge case 1
- Edge case 2
```

## Traceability

Each test document includes a **Requirements Traceability Matrix** at the end, showing:

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_MODEL_00001 | SWUT_MODEL_00001 | test_SWUT_MODEL_00001_function_type_enum_values | ✅ Pass |

This ensures complete traceability from requirements through implementation to testing.

For detailed requirements documentation, see [requirements/README.md](../requirements/README.md).

## Change History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-02-10 | 2.0 | Claude | Restructured to align with requirements documents, added traceability matrices, removed reference to TRACEABILITY.md |
| 2026-01-30 | 1.0 | Claude | Initial test documentation index with all modules |
