# Test Documentation Index

This directory contains test case documentation for the AUTOSAR Call Tree Analyzer project.

## Overview

| Module | Test ID Range | Count | Status | Coverage |
|--------|---------------|-------|--------|----------|
| Models | SWUT_MODEL_00001-00025 | 25 | ✅ Pass | 100% |
| AUTOSAR Parser | SWUT_PARSER_AUTOSAR_00001-00015 | 15 | ✅ Pass | 97% |
| C Parser | SWUT_PARSER_C_00001-00018 | 18 | ✅ Pass | 86% |
| Database | SWUT_DB_00001-00020 | 20 | ✅ Pass | 80% |
| Analyzers | SWUT_ANALYZER_00001-00020 | 20 | ✅ Pass | 94% |
| Config | SWUT_CONFIG_00001-00025 | 25 | ✅ Pass | 97% |
| Generators | SWUT_GENERATOR_00001-00031 | 31 | ✅ Pass | 96% |
| CLI | SWUT_CLI_00001-00014 | 14 | ✅ Pass | ~90% |
| End-to-End | SWUT_E2E_00001-00025 | 110 | ✅ Pass | ~90% |
| **Total** | | **278** | **✅ 100% Passing** | **94%** |

## Test Documents

### Core Tests

- **[models.md](models.md)** - Data model tests (25 tests)
  - Test function type enum values
  - Test parameter dataclass fields and string representation
  - Test function info attributes, equality, hashing
  - Test call tree node structure and manipulation
  - Test circular dependency representation
  - Test analysis statistics and result containers

### Parser Tests

Parser tests are documented within the requirements documents:
- See [autosar_parser.md](../requirements/autosar_parser.md) for AUTOSAR parser test cases
- See [c_parser.md](../requirements/c_parser.md) for C parser test cases

### Database Tests

- **[test_function_database.md](test_function_database.md)** - Function database tests (20 tests)
  - Database initialization and cache directory creation
  - Three-index structure (functions, qualified_functions, functions_by_file)
  - Source file discovery (.c files only)
  - Smart function lookup strategy (4-level selection)
  - Module configuration integration and statistics
  - Cache metadata validation, save/load, error handling
  - Cache loading progress reporting (file-by-file)
  - Function lookup methods (by name, qualified, search)
  - Parse error collection and database statistics

### Analyzer Tests

- **[test_call_tree_builder.md](test_call_tree_builder.md)** - Call tree builder tests (20 tests)
  - Builder initialization and state reset
  - Start function lookup and multiple definition warnings
  - Depth-first traversal algorithm
  - Cycle detection and handling in tree
  - Max depth enforcement and node depth tracking
  - Missing function handling
  - Statistics collection and unique function tracking
  - Qualified name generation
  - Result object creation (success and error cases)
  - Helper methods: get_all_functions_in_tree, get_tree_depth, get_leaf_nodes
  - Text tree generation
  - Verbose progress logging

### Configuration Tests

- **[test_module_config.md](test_module_config.md)** - Module configuration tests (25 tests)
  - Configuration loading (valid and missing files)
  - Version validation (missing, wrong type, unsupported)
  - File mappings validation (wrong type, empty filename, empty module)
  - Pattern mappings validation (wrong type, invalid pattern, empty pattern)
  - Default module validation (wrong type, empty)
  - Specific file lookup (exact match, no match, cached)
  - Specific overrides pattern (pattern match, exact match precedence)
  - Pattern lookup (match, no match, match order, compiled patterns)
  - Default module fallback (no mapping, default returns)
  - Lookup caching (caching mechanism, None values)
  - Statistics calculation (file counts, pattern counts)
  - Empty configuration initialization

### Generator Tests

- **[test_mermaid_generator.md](test_mermaid_generator.md)** - Mermaid generator tests (31 tests)
  - Initialization (with and without module names)
  - Mermaid diagram header generation
  - Participant collection (function mode, module mode, unique, order)
  - Module fallback to filename when not mapped
  - RTE abbreviation (enabled and disabled)
  - Sequence calls generation (function mode, module mode, recursive)
  - Parameters on arrows (single, multiple, empty)
  - Return statements in sequence (enabled and disabled)
  - Function table format (with and without modules, NA for unmapped)
  - Parameter formatting (in table, in diagram)
  - Text tree generation
  - Circular dependencies section
  - Metadata generation
  - File and string output
  - Empty call tree error handling
  - Optional sections control

### CLI Tests

CLI tests are documented in the requirements document:
- See [cli.md](../requirements/cli.md) for CLI test cases (14 tests)

### Integration Tests

Integration and end-to-end tests are documented separately and cover:
- Basic workflow (analysis, cache, statistics)
- Advanced features (module names, parameters, qualified names)
- Error conditions and edge cases
- Performance and usability

## Test Coverage

The project achieves **94% code coverage** across all modules:

### Coverage Breakdown

```
src/autosar_calltree/database/models.py          100%
src/autosar_calltree/parsers/autosar_parser.py    97%
src/autosar_calltree/parsers/c_parser.py          86%
src/autosar_calltree/database/function_db.py      80%
src/autosar_calltree/analyzers/call_tree.py       94%
src/autosar_calltree/config/module_config.py      97%
src/autosar_calltree/generators/mermaid_gen.py    96%
src/autosar_calltree/cli/*.py                     ~90%
--------------------------------------------------------
TOTAL                                             94%
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

## Test Format

Each test case follows the standard format:

```markdown
### SWUT_XXXXX_YYYYY - Test Case Title

**Requirement**: SWR_XXXXX_YYYYY
**Test Function**: `test_function_name`
**Status**: ✅ Pass / ❌ Fail / ⚠️ Skip

**Test Purpose**:
Description of what this test validates...

**Test Steps**:
1. Setup test data
2. Execute function under test
3. Verify expected behavior

**Expected Result**:
Clear description of expected outcome...

**Actual Result**:
Actual outcome (for failed tests)...
```

## Traceability

All tests are traced back to requirements in the [Traceability Matrix](../TRACEABILITY.md).

For detailed requirements documentation, see [requirements/README.md](../requirements/README.md).

## Change History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-01-30 | 1.0 | Claude | Initial test documentation index with all modules |
