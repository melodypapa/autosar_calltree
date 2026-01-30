# Sync Documentation

Synchronize requirements, test cases, and source code to ensure consistency across the codebase.

## Usage

```
/sync-docs
```

## Actions

When the user runs `/sync-docs`, perform the following steps:

### 1. Validate Documentation IDs
```bash
python scripts/validate_ids.py
```
- Check for duplicate requirement and test IDs
- Verify all IDs are unique and properly formatted
- If duplicates found, report them and offer to fix

### 2. Run Tests
```bash
python scripts/run_tests.py --unit
```
- Ensure all tests pass
- Check coverage meets ≥95% threshold
- Report any failures

### 3. Validate Test Coverage Per Module
Analyze coverage report to ensure:
- **CLI module**: Coverage can be < 100% (acceptable)
- **All other modules**: Must have 100% coverage
  - Models (src/autosar_pdf2txt/models/): 100% required
  - Parser (src/autosar_pdf2txt/parser/): 100% required
  - Writer (src/autosar_pdf2txt/writer/): 100% required

For modules with < 100% coverage:
- List uncovered line numbers
- Identify which requirements are not fully tested
- Suggest specific test cases to add for uncovered lines

### 4. Verify Requirement-to-Test Coverage
For each requirement in `docs/requirements/requirements.md`:
- Check if corresponding unit tests exist
- Verify tests adequately cover the requirement
- Report requirements without test coverage
- Suggest test cases to add for uncovered requirements

### 5. Run Quality Checks
```bash
python -m ruff check src/ tests/
python -m mypy src/autosar_pdf2txt/
```
- Verify linting passes
- Verify type checking passes
- Report any issues

### 6. Analyze and Report
After running validation and checks:
- Report on synchronization status
- Highlight any discrepancies found
- Report modules with < 100% coverage (except CLI)
- List requirements without test coverage
- Suggest updates to documentation if needed
- Suggest test cases to add for missing coverage
- Confirm all quality gates passed

### 7. Summary Report
Display a summary showing:
```
Component                 Status    Details
─────────────────────────────────────────────────
ID Validation            ✅ Pass    No duplicates
Tests                    ✅ Pass    265 passed, 90% coverage
Module Coverage:
  - Models               ⚠️  88%    Need tests for 12 lines
  - Parser               ⚠️  92%    Need tests for 33 lines
  - Writer               ⚠️  84%    Need tests for 27 lines
  - CLI                  ✅  75%    Acceptable (< 100% OK)
Requirements Coverage   ⚠️  3/65   Requirements without tests: SWR_XYZ
Linting (Ruff)           ✅ Pass    No errors
Type Checking (Mypy)     ✅ Pass    No issues
─────────────────────────────────────────────────
Documentation Synchronization: Complete with warnings ⚠️
```

## What This Command Does

This command analyzes the source code implementation and updates the requirements and test case documentation to match, ensuring traceability and accuracy.

## Detailed Steps (Reference)

### 1. Analyze Source Code
- Scan source files to identify:
  - Class attributes and their types
  - Method signatures
  - Constructor parameters
  - Inheritance relationships
- Extract actual implementation details

### 2. Compare with Documentation
- Read current requirements (`docs/requirements/requirements.md`)
- Read current unit test cases (`docs/test_cases/unit_tests.md`)
- Read current integration test cases (`docs/test_cases/integration_tests.md`)
- Identify discrepancies:
  - Missing or incorrect attributes in requirements
  - Outdated parameter lists
  - Incorrect inheritance hierarchies
  - Missing or stale unit test case descriptions
  - Missing or stale integration test case descriptions

### 3. Update Requirements
- Update requirement descriptions to match implementation
- Add missing attributes to requirement specifications
- Remove deprecated features from requirements
- Update attribute types and default values
- Ensure maturity levels match implementation status

### 4. Update Unit Test Cases
- Update test case descriptions to match current implementation
- Add missing test steps for new attributes
- Remove test steps for deprecated features
- Update expected results to match actual behavior
- Ensure test cases reference correct requirement IDs

### 5. Update Integration Test Cases
- Update integration test scenarios to match current implementation
- Add missing integration test steps for new features
- Remove test steps for deprecated features
- Update expected results to match actual behavior
- Ensure integration test cases reference correct requirement IDs
- Verify end-to-end workflows are documented correctly

### 6. Validate Documentation IDs
- Run ID validation script to check for duplicate requirement and test IDs
- Verify all IDs are unique and properly formatted
- Detect gaps in ID sequences
- Report any ID conflicts with line numbers
- Fix any duplicate or invalid IDs found

### 7. Verify Synchronization
- Run all tests to ensure documentation is accurate
- Run type checking to verify signatures match
- Check for orphaned requirements or tests
- Generate synchronization report

## Common Synchronization Tasks

### Attribute Changes
When attributes are moved/added/removed:
1. Update affected requirement specifications
2. Update unit test case steps that verify attributes
3. Update integration test scenarios that test attributes
4. Update examples in documentation
5. Update `__init__` signatures if needed

### Inheritance Changes
When inheritance hierarchies change:
1. Update base class requirements
2. Update derived class requirements
3. Update unit test inheritance verification steps
4. Update integration test scenarios that test inheritance
5. Update docstrings that reference inheritance

### Type Changes
When attribute types change:
1. Update requirement type specifications
2. Update unit test type checks
3. Update integration test type checks
4. Update examples with correct types
5. Update type hints in source if missing

### Integration Workflow Changes
When end-to-end workflows change:
1. Update integration test scenarios
2. Update test data and fixtures
3. Update expected results
4. Verify workflow documentation accuracy

## Files Modified

- `docs/requirements/requirements.md` - Requirements specifications
- `docs/test_cases/unit_tests.md` - Unit test case documentation
- `docs/test_cases/integration_tests.md` - Integration test case documentation

## Files Analyzed (Read-Only)

- `src/autosar_pdf2txt/models/*.py` - Model implementations
- `src/autosar_pdf2txt/parser/*.py` - Parser implementations
- `src/autosar_pdf2txt/writer/*.py` - Writer implementations
- `src/autosar_pdf2txt/cli/*.py` - CLI implementations
- `tests/**/*.py` - Test implementations

## Verification

After synchronization, run:
```bash
# 1. Validate documentation IDs
python scripts/validate_ids.py

# 2. Run tests
pytest tests/ --cache-clear

# 3. Check code quality
ruff check src/ tests/

# 4. Type check
mypy src/autosar_pdf2txt/
```

All checks must pass for synchronization to be complete.

## Examples

### When Coverage Gaps Are Detected
```
User: /sync-docs
System: [Step 1] Validating documentation IDs...
       [OK] No duplicate IDs found (65 unique IDs)

       [Step 2] Running tests...
       265 passed, 1 skipped, 90% coverage

       [Step 3] Validating test coverage per module...
       Module Coverage Analysis:
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       Module              Coverage    Missing Lines    Status
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       models/containers   88%         12 lines         ⚠️  NEED TESTS
       parser/pdf_parser   92%         33 lines         ⚠️  NEED TESTS
       writer/markdown_    84%         27 lines         ⚠️  NEED TESTS
       cli/autosar_cli     75%         23 lines         ✅  ACCEPTABLE
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

       Suggested test cases for missing coverage:

       models/containers (12 lines missing):
       - test_autosar_package_get_class_nested: Test get_class() with nested packages
       - test_autosar_package_add_subpackage_duplicate: Test duplicate subpackage detection
       - test_autosar_doc_init_empty_root_classes: Test AutosarDoc with empty root_classes list

       parser/pdf_parser (33 lines missing):
       - test_parse_pdf_with_malformed_class_definition: Test error handling for malformed class definitions
       - test_parse_pdf_duplicate_class_detection: Test detection of duplicate class names
       - test_parse_pdf_empty_package_handling: Test handling of packages with no classes

       writer/markdown_writer (27 lines missing):
       - test_write_class_hierarchy_no_all_classes: Test write_class_hierarchy() without all_classes parameter
       - test_write_packages_empty_packages_list: Test write_packages() with empty packages list
       - test_collect_classes_from_package_deeply_nested: Test _collect_classes_from_package() with deep nesting

       [Step 4] Verifying requirement-to-test coverage...
       Requirements without adequate test coverage:
       - SWR_MODEL_00013: AutosarPackage query methods
       - SWR_WRITER_00007: Class hierarchy output (partial coverage)

       Suggested test cases to cover requirements:
       - test_autosar_package_query_methods: Test get_class(), get_subpackage(), has_class(), has_subpackage()
       - test_write_class_hierarchy_root_classes_only: Test class hierarchy output with only root classes

       [Step 5] Running quality checks...
       All checks passed!

       Summary:
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       Component              Status    Details
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       ID Validation         ✅ Pass    No duplicates
       Tests                 ✅ Pass    265 passed, 90% coverage
       Module Coverage       ⚠️         3 modules need tests
       Requirements Coverage ⚠️         2 requirements partial
       Linting (Ruff)        ✅ Pass    No errors
       Type Checking (Mypy)  ✅ Pass    No issues
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

       ⚠️  Action required: Add suggested test cases to achieve 100% coverage
       for all modules except CLI.
```

### After Refactoring
```
User: /sync-docs
System: Analyzing source code...
       Found 3 discrepancies in requirements
       Found 5 discrepancies in unit test cases
       Found 2 discrepancies in integration test cases
       Updating SWR_MODEL_00018...
       Updating SWUT_MODEL_00034...
       Updating SWIT_PARSER_00012...
       Validating documentation IDs...
       [INFO] Checking docs\requirements\requirements.md...
       [OK] No duplicate IDs found (62 unique IDs)
       [INFO] Checking docs\test_cases\unit_tests.md...
       [OK] No duplicate IDs found (125 unique IDs)
       [INFO] Checking docs\test_cases\integration_tests.md...
       [OK] No duplicate IDs found (4 unique IDs)
       [PASS] All IDs are unique!
       Verification: All tests pass ✅
       Synchronization complete
```

### After Adding New Attribute
```
User: /sync-docs
System: Detected new attribute 'package' in AbstractAutosarBase
       Updating requirements...
       Updating unit test cases...
       Updating integration test cases...
       Complete: 2 requirements updated, 3 unit tests updated, 1 integration test updated
```

### After Workflow Changes
```
User: /sync-docs
System: Detected changes in PDF parsing workflow
       Updating integration test scenarios...
       Updating end-to-end test steps...
       Complete: 2 integration test scenarios updated
```

### When Duplicate IDs Are Detected
```
User: /sync-docs
System: Analyzing source code...
       Documentation synchronized
       Validating documentation IDs...
       [INFO] Checking docs\requirements\requirements.md...
       [OK] No duplicate IDs found (62 unique IDs)
       [INFO] Checking docs\test_cases\unit_tests.md...
       [ERROR] Found 23 duplicate ID(s):
          SWUT_MODEL_00011: lines 214, 721
          SWUT_MODEL_00012: lines 235, 742
          SWUT_MODEL_00013: lines 255, 763
          ...
       [FAIL] Validation failed: Duplicate IDs found!

       Please fix duplicate IDs to ensure proper traceability.
       Remember: All requirement and test IDs must be unique.

System: Found duplicate test IDs that need to be renumbered.
       Renumbering duplicate test IDs to unique values...
       SWUT_MODEL_00011 → SWUT_MODEL_00036
       SWUT_MODEL_00012 → SWUT_MODEL_00037
       SWUT_MODEL_00013 → SWUT_MODEL_00038
       ...
       Complete: Fixed 23 duplicate test IDs
       Verification: All IDs are now unique ✅
```

## Notes

- Always run quality checks after synchronization
- Always validate documentation IDs for uniqueness before committing
- Document what changed and why
- If in doubt, ask user before making changes
- Never change stable requirement IDs
- Keep maturity levels accurate
- **CRITICAL**: All requirement and test IDs must be unique - duplicate IDs break traceability

## Test Coverage Requirements

**Module Coverage Standards:**
- **CLI module**: Coverage < 100% is acceptable (error handling paths may be hard to test)
- **All other modules**: MUST have 100% coverage
  - models/ (attributes, base, containers, enums, types)
  - parser/
  - writer/

**Requirement Coverage Standards:**
- Every requirement MUST have corresponding unit tests
- Tests must adequately cover all acceptance criteria
- If a requirement exists but lacks test coverage, new tests must be added

**When Coverage Gaps Are Found:**
- The command will suggest specific test cases to add
- Each suggestion includes:
  - Test name following naming conventions
  - Description of what scenario to test
  - Which requirement it covers
- Use these suggestions to guide test development

## Related Commands

- `/req` - Manage individual requirements
- `/test` - Run tests and coverage
- `/quality` - Run quality checks
