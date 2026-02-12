# Test Documentation Index

This directory contains test case documentation for the AUTOSAR Call Tree Analyzer project. Each test document maps directly to its corresponding requirements document in `../requirements/`, organized by Python package structure.

## Overview

| Package | Requirements | Test ID Range | Test Count | Status | Coverage |
|----------|-------------|-----------------|-------------|----------|-----------|
| Database | SWR_DB_00001-00035 | SWUT_DB_00001-00036 | 36 | ✅ Pass | 80% |
| Parsers | SWR_PARSER_00001-00040 | SWUT_PARSER_00001-00040 | 40 | ✅ Pass | 92% |
| Analyzers | SWR_ANALYZER_00001-00015 | SWUT_ANALYZER_00001-00015 | 15 | ✅ Pass | 94% |
| Config | SWR_CONFIG_00001-00008 | SWUT_CONFIG_00001-00008 | 8 | ✅ Pass | 97% |
| Generators | SWR_GEN_00001-00025 | SWUT_GEN_00001-00025 | 25 | ✅ Pass | 89% |
| CLI | SWR_CLI_00001-00018 | SWUT_CLI_00001-00018 | 18 | ✅ Pass | ~90% |
| E2E | SWR_E2E_00001-00018 | SWUT_E2E_00001-00018 | 18 | ✅ Pass | integration |
| **Total** | **141** | | **160** | **✅ 100% Passing** | **89%** |

## Test Documents by Package

### Database Package Tests

**Requirements Document**: [requirements_database.md](../requirements/requirements_database.md)

**Test Document**: [test_database.md](test_database.md)

- **Requirement IDs**: SWR_DB_00001 - SWR_DB_00035 (35 requirements)
- **Test IDs**: SWUT_DB_00001 - SWUT_DB_00036 (36 tests)
- **Coverage**: 80%
- **Source Files**: `models.py`, `function_database.py`
- **Key Areas**:
  - Data models (FunctionType, Parameter, FunctionInfo, CallTreeNode, etc.)
  - Function database initialization and three-index structure
  - Source file discovery and database building
  - Module configuration integration
  - Smart function lookup (4-level selection strategy)
  - Cache management (save, load, validation, error handling)
  - Parser auto-detection and statistics

### Parsers Package Tests

**Requirements Document**: [requirements_parsers.md](../requirements/requirements_parsers.md)

**Test Document**: [test_parsers.md](test_parsers.md)

- **Requirement IDs**: SWR_PARSER_00001 - SWR_PARSER_00040 (40 requirements)
- **Test IDs**: SWUT_PARSER_00001 - SWUT_PARSER_00040 (40 tests)
- **Coverage**: 92%
- **Source Files**: `autosar_parser.py`, `c_parser.py`, `c_parser_pycparser.py`
- **Key Areas**:
  - AUTOSAR macro recognition and parsing
  - AUTOSAR parameter macro parsing
  - Parameter string extraction and splitting
  - Traditional C function pattern recognition
  - Keyword and type filtering
  - File-level parsing with comment removal
  - Line-by-line processing to prevent ReDoS
  - Multi-line function prototypes
  - Function body extraction
  - Function call extraction with conditional/loop context
  - Multi-line if condition extraction
  - Loop detection (for/while)
  - Condition text sanitization
  - Progressive enhancement (AUTOSAR first, then C)
  - pycparser-based AST parsing
  - AUTOSAR macro preprocessing for pycparser
  - AST visitor pattern
  - Return type and parameter extraction from AST
  - Hybrid parsing strategy and deduplication
  - Preprocessor directive handling
  - Parse error graceful handling
  - Common parser interface and file encoding handling

### Analyzers Package Tests

**Requirements Document**: [requirements_analyzers.md](../requirements/requirements_analyzers.md)

**Test Document**: [test_analyzers.md](test_analyzers.md)

- **Requirement IDs**: SWR_ANALYZER_00001 - SWR_ANALYZER_00015 (15 requirements)
- **Test IDs**: SWUT_ANALYZER_00001 - SWUT_ANALYZER_00015 (15 tests)
- **Coverage**: 94%
- **Source Files**: `call_tree_builder.py`
- **Key Areas**:
  - Builder initialization with database
  - State management between builds
  - Start function validation
  - Depth-first traversal algorithm
  - Cycle detection and handling
  - Max depth enforcement
  - Node depth tracking
  - AnalysisResult creation
  - Statistics collection
  - Unique function tracking
  - Missing function handling
  - RTE call filtering
  - Qualified name usage for cycles
  - Verbose logging

### Config Package Tests

**Requirements Document**: [requirements_config.md](../requirements/requirements_config.md)

**Test Document**: [test_config.md](test_config.md)

- **Requirement IDs**: SWR_CONFIG_00001 - SWR_CONFIG_00008 (8 requirements)
- **Test IDs**: SWUT_CONFIG_00001 - SWUT_CONFIG_00008 (8 tests)
- **Coverage**: 97%
- **Source Files**: `module_config.py`
- **Key Areas**:
  - YAML configuration file support
  - Configuration loading and validation
  - File mappings (exact filename to module)
  - Pattern mappings (glob-style wildcards)
  - Default module assignment
  - Configuration version tracking
  - Module lookup (priority: exact → pattern → default)
  - Lookup caching for performance

### Generators Package Tests

**Requirements Document**: [requirements_generators.md](../requirements/requirements_generators.md)

**Test Document**: [test_generators.md](test_generators.md)

- **Requirement IDs**: SWR_GEN_00001 - SWR_GEN_00025 (25 requirements)
- **Test IDs**: SWUT_GEN_00001 - SWUT_GEN_00025 (25 tests)
- **Coverage**: 89%
- **Source Files**: `mermaid_generator.py`, `xmi_generator.py`
- **Key Areas**:
  - Mermaid sequence diagram generation
  - Participant management (function and module-based)
  - Function names with parameters on arrows
  - Parameter display
  - Opt/alt/loop block generation for conditional/loop calls
  - Function table generation with module column
  - Metadata section (timestamp, source dir, stats)
  - ASCII art text tree generation
  - Statistics display
  - Circular dependencies section
  - XMI 2.5 document generation
  - XMI namespaces and schema compliance
  - UML lifeline generation
  - UML message generation
  - XMI opt block support for conditionals
  - Module support in XMI
  - Recursive call handling
  - XMI metadata
  - XML formatting and escaping
  - File extensions (.md, .xmi)

### CLI Package Tests

**Requirements Document**: [requirements_cli.md](../requirements/requirements_cli.md)

**Test Document**: [test_cli.md](test_cli.md)

- **Requirement IDs**: SWR_CLI_00001 - SWR_CLI_00018 (18 requirements)
- **Test IDs**: SWUT_CLI_00001 - SWUT_CLI_00018 (18 tests)
- **Coverage**: ~90%
- **Source Files**: `main.py`
- **Key Areas**:
  - Click-based command structure
  - Start function option (--start-function)
  - Source directory option (--source-dir)
  - Output path option (--output)
  - Max depth option (--max-depth)
  - Output format option (--format: mermaid, xmi, both)
  - Cache options (--cache-dir, --no-cache, --rebuild-cache)
  - Multiple output files with format "both"
  - Verbose output (--verbose)
  - List functions command (--list-functions)
  - Search functions command (--search)
  - Rich console output (colors, tables, progress)
  - Module configuration options (--module-config, --use-module-names)
  - RTE abbreviation control (--no-abbreviate-rte)
  - Parameter display control
  - Exit codes (success, error, interrupt)
  - User-friendly error messages
  - Keyboard interrupt handling (Ctrl+C)

### Integration Tests

**Test Document**: [integration.md](integration.md)

- **Requirement IDs**: SWR_E2E_00001 - SWR_E2E_00018 (18 requirements)
- **Test IDs**: SWUT_E2E_00001 - SWUT_E2E_00018 (18 tests)
- **Type**: Integration / End-to-End Tests
- **Key Areas**:
  - Basic workflow (source scanning, parsing, analysis, output generation)
  - Cache functionality (creation, reuse, invalidation)
  - Module configuration integration
  - Parameters on diagram arrows
  - Error conditions and edge cases
  - Performance and usability

## Test Coverage

The project achieves **89% overall code coverage** across all modules:

### Coverage Breakdown

```
src/autosar_calltree/database/models.py          100%
src/autosar_calltree/database/function_database.py   80%
src/autosar_calltree/parsers/autosar_parser.py    97%
src/autosar_calltree/parsers/c_parser.py          87%
src/autosar_calltree/parsers/c_parser_pycparser.py    90%
src/autosar_calltree/analyzers/call_tree_builder.py  94%
src/autosar_calltree/config/module_config.py       97%
src/autosar_calltree/generators/mermaid_generator.py   89%
src/autosar_calltree/generators/xmi_generator.py      70%
src/autosar_calltree/cli/*.py                        ~90%
--------------------------------------------------------
TOTAL                                             89%
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/unit/test_models.py

# Run with coverage
pytest --cov=autosar_calltree --cov-report=html --cov-report=term

# Run specific test case
pytest tests/unit/test_models.py::TestFunctionType::test_function_type_enum_values

# Run with verbose output
pytest -vv -s tests/
```

## Test Case Format

Each test case follows the natural language format:

```markdown
### SWUT_XXXXX_YYYYY - Test Case Title

**Requirement**: SWR_XXXXX_YYYYY
**Priority**: High/Medium/Low
**Status**: ✅ Pass / ❌ Fail / ⚠️ Skip

**Description**
Natural language description of what this test validates and why it matters...

**Test Approach**
The test verifies that:
1. First test step or scenario
2. Second test step or scenario
3. Third test step or scenario

**Expected Behavior**
Clear description of what should happen when the test runs correctly...

**Edge Cases**
- Edge case 1
- Edge case 2
```

## Traceability

Each test document includes a **Requirements Traceability Matrix** at the end, showing:

| Requirement ID | Test ID | Status | Notes |
| --------------- | --------- | ------ | ----- |
| SWR_DB_00001 | SWUT_DB_00001 | ✅ Pass | FunctionType enum |

This ensures complete traceability from requirements through implementation to testing.

For detailed requirements documentation, see [requirements/README.md](../requirements/README.md).

## Change History

| Date       | Version | Author | Change Description |
| ---------- | ------- | ------ | ------------------- |
| 2026-02-11 | 3.0     | Reorganized to package structure matching requirements, removed Test Function labels, using natural language |
| 2026-02-10 | 2.0     | Restructured to align with requirements documents, added traceability matrices |
| 2026-01-30 | 1.0     | Initial test documentation index with all modules |
