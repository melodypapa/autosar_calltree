# Testing and CI/CD Infrastructure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build comprehensive testing infrastructure with ≥95% coverage, GitHub Actions CI/CD pipeline, requirements documentation, and traceability for the AUTOSAR Call Tree Analyzer.

**Architecture:** Iterative module-by-module approach with immediate CI feedback. Start with foundation (CI skeleton, test structure, scripts), then implement tests wave-by-wave (models → parsers → database → analyzers → generators → CLI). Each module follows TDD: analyze requirements, document, write failing test, implement, verify in CI, update traceability.

**Tech Stack:** pytest, pytest-cov, GitHub Actions, Python 3.8-3.12, mypy (strict mode), black, isort, flake8

---

## Phase 1: Foundation Setup

### Task 1.1: Create GitHub Actions CI Workflow

**Files:**
- Create: `.github/workflows/ci.yml`

**Step 1: Create the CI workflow file**

```yaml
name: CI

on:
  push:
    branches: ['**']
  pull_request:
    branches: [main, develop]

jobs:
  quality-check:
    name: Quality Checks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Check formatting with Black
        run: black --check src/ tests/

      - name: Check import sorting with isort
        run: isort --check-only src/ tests/

      - name: Lint with flake8
        run: flake8 src/ tests/

      - name: Type check with mypy
        run: mypy src/autosar_calltree/

  test:
    name: Tests (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    needs: quality-check
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests with coverage
        run: |
          pytest tests/ -v \
            --cov=autosar_calltree \
            --cov-report=xml \
            --cov-report=term \
            --cov-report=html

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

  requirements-check:
    name: Requirements Traceability
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Check requirements traceability
        run: python scripts/check_traceability.py
```

**Step 2: Commit the workflow**

```bash
git add .github/workflows/ci.yml
git commit -m "feat: add GitHub Actions CI workflow

- Quality checks (black, isort, flake8, mypy)
- Test matrix for Python 3.8-3.12
- Coverage reporting
- Requirements traceability validation
"
```

---

### Task 1.2: Create Test Directory Structure

**Files:**
- Create: `tests/fixtures/autosar_code/.gitkeep`
- Create: `tests/fixtures/traditional_c/.gitkeep`
- Create: `tests/fixtures/configs/.gitkeep`
- Create: `tests/unit/.gitkeep`
- Create: `tests/integration/.gitkeep`
- Create: `tests/__init__.py`

**Step 1: Create directory structure**

```bash
mkdir -p tests/fixtures/{autosar_code,traditional_c,configs}
mkdir -p tests/{unit,integration}
touch tests/fixtures/autosar_code/.gitkeep
touch tests/fixtures/traditional_c/.gitkeep
touch tests/fixtures/configs/.gitkeep
touch tests/unit/.gitkeep
touch tests/integration/.gitkeep
```

**Step 2: Create test package init**

```python
# tests/__init__.py
"""Test suite for AUTOSAR Call Tree Analyzer."""
```

**Step 3: Commit**

```bash
git add tests/
git commit -m "feat: create test directory structure

- fixtures/ for test data (AUTOSAR, traditional C, configs)
- unit/ for unit tests
- integration/ for end-to-end tests
"
```

---

### Task 1.3: Create Quality Check Script

**Files:**
- Create: `scripts/run_quality.sh`

**Step 1: Create the quality script**

```bash
#!/bin/bash
# Run all quality checks

set -e

echo "=== Checking formatting with Black ==="
black --check src/ tests/

echo "=== Checking import sorting with isort ==="
isort --check-only src/ tests/

echo "=== Linting with flake8 ==="
flake8 src/ tests/

echo "=== Type checking with mypy ==="
mypy src/autosar_calltree/

echo "✅ All quality checks passed!"
```

**Step 2: Make it executable**

```bash
chmod +x scripts/run_quality.sh
```

**Step 3: Commit**

```bash
git add scripts/run_quality.sh
git commit -m "feat: add quality check script

Runs black, isort, flake8, mypy in sequence
"
```

---

### Task 1.4: Create Test Runner Script

**Files:**
- Create: `scripts/run_tests.sh`

**Step 1: Create the test runner script**

```bash
#!/bin/bash
# Run tests with coverage

set -e

# Default to running all tests
TEST_PATH="${1:-tests/}"

echo "=== Running tests with coverage ==="
pytest "$TEST_PATH" \
  -v \
  --cov=autosar_calltree \
  --cov-report=html \
  --cov-report=term \
  --cov-report=xml

echo ""
echo "=== Coverage Report ==="
echo "HTML report: htmlcov/index.html"
echo "XML report: coverage.xml"
```

**Step 2: Make it executable**

```bash
chmod +x scripts/run_tests.sh
```

**Step 3: Commit**

```bash
git add scripts/run_tests.sh
git commit -m "feat: add test runner script with coverage

Supports optional path argument
Generates HTML, terminal, and XML coverage reports
"
```

---

### Task 1.5: Create Traceability Checker Script

**Files:**
- Create: `scripts/check_traceability.py`

**Step 1: Create the traceability checker**

```python
#!/usr/bin/env python3
"""Validate requirements traceability (SWUT_XXX → SWR_XXX)."""

import re
import sys
from pathlib import Path
from typing import Dict, Set, Tuple


def extract_swut_from_tests(tests_dir: Path) -> Set[str]:
    """Extract all SWUT_ references from test files."""
    swut_refs = set()

    for test_file in tests_dir.rglob("test_*.py"):
        content = test_file.read_text()
        # Match comments like: # SWUT_MODEL_00001
        matches = re.findall(r'#\s*SWUT_[A-Z_]+_\d+', content)
        swut_refs.update(m.strip() for m in matches)

    return swut_refs


def extract_swr_from_requirements(reqs_dir: Path) -> Set[str]:
    """Extract all SWR_ definitions from requirement documents."""
    swr_defs = set()

    for req_file in reqs_dir.glob("*.md"):
        content = req_file.read_text()
        # Match definitions like: ### SWR_MODEL_00001
        matches = re.findall(r'#+\s*SWR_[A-Z_]+_\d+', content)
        swr_defs.update(m.strip().replace('#', '').strip() for m in matches)

    return swr_defs


def parse_traceability(traceability_file: Path) -> Dict[str, str]:
    """Parse existing traceability matrix."""
    trace_map = {}

    if not traceability_file.exists():
        return trace_map

    content = traceability_file.read_text()
    # Parse markdown table rows with SWR and SWUT
    rows = re.findall(r'\|\s*(SWR_[A-Z_]+_\d+)\s*\|\s*(SWUT_[A-Z_]+_\d+)', content)
    for swr, swut in rows:
        trace_map[swut] = swr

    return trace_map


def validate_traceability(
    swut_refs: Set[str],
    swr_defs: Set[str],
    trace_map: Dict[str, str]
) -> Tuple[int, int, Set[str], Set[str]]:
    """Validate traceability and return statistics."""
    orphaned_tests = set()
    untested_requirements = set()

    # Check for orphaned tests (SWUT without mapped SWR)
    for swut in swut_refs:
        if swut not in trace_map:
            orphaned_tests.add(swut)
        elif trace_map[swut] not in swr_defs:
            orphaned_tests.add(swut)

    # Check for untested requirements (SWR without mapped SWUT)
    mapped_swrs = set(trace_map.values())
    for swr in swr_defs:
        if swr not in mapped_swrs:
            untested_requirements.add(swr)

    return len(swut_refs), len(swr_defs), orphaned_tests, untested_requirements


def main() -> int:
    """Run traceability validation."""
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "tests"
    reqs_dir = project_root / "docs" / "requirements"
    traceability_file = project_root / "docs" / "TRACEABILITY.md"

    print("=== Checking Requirements Traceability ===\n")

    # Extract references
    swut_refs = extract_swut_from_tests(tests_dir)
    swr_defs = extract_swr_from_requirements(reqs_dir)
    trace_map = parse_traceability(traceability_file)

    # Validate
    test_count, req_count, orphaned_tests, untested_reqs = validate_traceability(
        swut_refs, swr_defs, trace_map
    )

    print(f"Test cases found: {test_count}")
    print(f"Requirements found: {req_count}")
    print(f"Traceability links: {len(trace_map)}")

    # Report issues
    exit_code = 0

    if orphaned_tests:
        print(f"\n❌ Orphaned tests ({len(orphaned_tests)}):")
        for swut in sorted(orphaned_tests):
            print(f"  - {swut}")
        exit_code = 1
    else:
        print("\n✅ All tests trace to requirements")

    if untested_reqs:
        print(f"\n⚠️  Untested requirements ({len(untested_reqs)}):")
        for swr in sorted(untested_reqs)[:10]:  # Show first 10
            print(f"  - {swr}")
        if len(untested_reqs) > 10:
            print(f"  ... and {len(untested_reqs) - 10} more")
    else:
        print("✅ All requirements have tests")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
```

**Step 2: Make it executable**

```bash
chmod +x scripts/check_traceability.py
```

**Step 3: Commit**

```bash
git add scripts/check_traceability.py
git commit -m "feat: add traceability validation script

Checks that all SWUT_ tests map to valid SWR_ requirements
Reports orphaned tests and untested requirements
"
```

---

### Task 1.6: Update /test Slash Command

**Files:**
- Modify: `.claude/commands/test.md`

**Step 1: Update the test command**

```markdown
---
description: Run the test suite with coverage
---

Use this command to run the test suite with coverage reporting.

## Usage

Run all tests:
```bash
pytest tests/ -v --cov=autosar_calltree --cov-report=html --cov-report=term
```

Run specific test file:
```bash
pytest tests/unit/test_models.py -v
```

Run specific test function:
```bash
pytest tests/unit/test_models.py::test_SWUT_MODEL_00001_function_info_creation -v
```

## Acceptance Criteria

- All tests pass
- Coverage ≥ 95%
- No unexpected errors or warnings

## Example Output

```
tests/unit/test_models.py::test_SWUT_MODEL_00001_function_info_creation PASSED
tests/unit/test_models.py::test_SWUT_MODEL_00002_parameter_creation PASSED

---------- coverage: platform darwin, python 3.11 -----------
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
src/autosar_calltree/models.py        85      0   100%

TOTAL                                  85      0   100%
```
```

**Step 2: Commit**

```bash
git add .claude/commands/test.md
git commit -m "docs: update /test command to use pytest directly

Removes dependency on non-existent scripts/run_tests.py
"
```

---

### Task 1.7: Update /quality Slash Command

**Files:**
- Modify: `.claude/commands/quality.md`

**Step 1: Update the quality command**

```markdown
---
description: Run all quality checks (linting, type checking, testing)
---

Use this command to run all quality checks in sequence.

## Usage

```bash
# Run all quality checks
scripts/run_quality.sh

# Or run individually
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
mypy src/autosar_calltree/
```

## Checks Performed

1. **Black** - Code formatting (line length 88)
2. **isort** - Import sorting
3. **flake8** - Linting
4. **mypy** - Static type checking (strict mode)

## Acceptance Criteria

- All checks pass
- No formatting errors
- No type errors
- No linting violations

## Exit Codes

- 0: All checks passed
- 1: One or more checks failed
```

**Step 2: Commit**

```bash
git add .claude/commands/quality.md
git commit -m "docs: update /quality command for autosar_calltree

Fixes project path from autosar_pdf2txt to autosar_calltree
"
```

---

### Task 1.8: Remove Inapplicable Slash Commands

**Files:**
- Delete: `.claude/commands/parse.md`
- Delete: `.claude/commands/sync-docs.md`

**Step 1: Remove commands for different project**

```bash
git rm .claude/commands/parse.md
git rm .claude/commands/sync-docs.md
```

**Step 2: Commit**

```bash
git commit -m "chore: remove inapplicable slash commands

These commands are for the autosar-pdf2txt project
"
```

---

### Task 1.9: Create Requirements Documentation Template

**Files:**
- Create: `docs/requirements/_template.md`

**Step 1: Create template**

```markdown
# [Module Name] Requirements

## Overview
[Brief description of what this module does]

## Requirements

### SWR_[MODULE]_00001: [Requirement Title]

**Priority:** High/Medium/Low
**Status:** Draft/Proposed/Accepted/Implemented/Verified
**Maturity:** draft/accept/verified

**Description:**
The system shall [detailed requirement description].

**Rationale:**
[Why this requirement exists]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Related Requirements:** None

---

## Traceability

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_[MODULE]_00001 | SWUT_[MODULE]_00001 | test_SWUT_[MODULE]_00001_[description] | ⏳ Pending |

## Revision History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| YYYY-MM-DD | 1.0 | Name | Initial version |
```

**Step 2: Commit**

```bash
git add docs/requirements/_template.md
git commit -m "docs: add requirements documentation template

Standardized format for requirement documents
Includes traceability table section
"
```

---

### Task 1.10: Create Test Case Documentation Template

**Files:**
- Create: `docs/tests/_template.md`

**Step 1: Create template**

```markdown
# [Module Name] Test Cases

## Overview
This document describes the test cases for the [Module] module.

## Test Cases

### SWUT_[MODULE]_00001: [Test Case Title]

**Requirement:** SWR_[MODULE]_00001
**Priority:** High/Medium/Low
**Status:** Draft/Implemented/Verified

**Description:**
[Test case description]

**Test Function:** `test_SWUT_[MODULE]_00001_[description]()`

**Test Setup:**
```python
# Setup code
```

**Test Execution:**
```python
# Test code
result = function_under_test(input)
```

**Expected Result:**
```python
# Assertion
assert result == expected
```

**Edge Cases Covered:**
- Edge case 1
- Edge case 2

---

## Coverage Summary

| Requirement ID | Test ID | Status | Coverage |
|----------------|---------|--------|----------|
| SWR_[MODULE]_00001 | SWUT_[MODULE]_00001 | ✅ Pass | Full |
```

**Step 2: Commit**

```bash
git add docs/tests/_template.md
git commit -m "docs: add test case documentation template

Standardized format for test case documents
Links tests to requirements
"
```

---

## Phase 2: Wave 1 - Core Data & Parsing

### Task 2.1: Analyze models.py and Extract Requirements

**Files:**
- Reference: `src/autosar_calltree/database/models.py`
- Create: `docs/requirements/models.md`

**Step 1: Read and analyze the models.py file**

Examine the code to identify:
- All dataclasses (FunctionInfo, Parameter, CallTreeNode, etc.)
- All enums (FunctionType)
- All type aliases
- Validation logic
- Serialization methods

**Step 2: Extract requirements**

For each class/enum/type, define requirements following the template:

Example:
```markdown
### SWR_MODEL_00001: FunctionInfo Dataclass

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The system shall provide a FunctionInfo dataclass to store function metadata including:
- Function name (str)
- Return type (str)
- Parameters (List[Parameter])
- Function calls within body (List[str])
- File path (str)
- Line number (int)
- Function type (FunctionType)
- SW module assignment (Optional[str])

**Rationale:**
Central data structure for function call tree analysis.

**Acceptance Criteria:**
- [ ] Dataclass is properly defined
- [ ] All fields have type annotations
- [ ] Default values are appropriate
- [ ] Frozen and slots directives for performance
```

**Step 3: Write complete requirements document**

Create `docs/requirements/models.md` with all 27 requirements (SWR_MODEL_00001 through SWR_MODEL_00027).

**Step 4: Commit**

```bash
git add docs/requirements/models.md
git commit -m "docs: add models module requirements (SWR_MODEL_00001-00027)

Document all 27 requirements for dataclasses, enums, and type aliases
"
```

---

### Task 2.2: Document Test Cases for models

**Files:**
- Create: `docs/tests/models.md`

**Step 1: Document test cases based on requirements**

For each SWR_MODEL_XXXXX, create corresponding SWUT_MODEL_XXXXX entry:

```markdown
### SWUT_MODEL_00001: FunctionInfo Creation

**Requirement:** SWR_MODEL_00001
**Priority:** High
**Status:** Pending

**Description:**
Test that FunctionInfo dataclass can be instantiated with all required fields.

**Test Function:** `test_SWUT_MODEL_00001_function_info_creation()`

**Test Setup:**
```python
from autosar_calltree.database.models import FunctionInfo, FunctionType

func_info = FunctionInfo(
    name="TestFunction",
    return_type="void",
    parameters=[],
    calls=[],
    file_path="/test.c",
    line_number=10,
    function_type=FunctionType.AUTOSAR_FUNC,
    sw_module="TestModule"
)
```

**Expected Result:**
```python
assert func_info.name == "TestFunction"
assert func_info.return_type == "void"
assert func_info.function_type == FunctionType.AUTOSAR_FUNC
```
```

**Step 2: Commit**

```bash
git add docs/tests/models.md
git commit -m "docs: add test case documentation for models module

Documents all SWUT_MODEL_XXXXX test cases
"
```

---

### Task 2.3: Write Test - SWUT_MODEL_00001 (FunctionInfo Creation)

**Files:**
- Create: `tests/unit/test_models.py`

**Step 1: Write the failing test**

```python
"""Tests for models module (SWUT_MODEL_*)"""

# SWUT_MODEL_00001: FunctionInfo creation
def test_SWUT_MODEL_00001_function_info_creation():
    """Test that FunctionInfo can be created with all required fields."""
    from autosar_calltree.database.models import FunctionInfo, FunctionType

    # SWUT_MODEL_00001: Create FunctionInfo
    func_info = FunctionInfo(
        name="TestFunction",
        return_type="void",
        parameters=[],
        calls=[],
        file_path="/test.c",
        line_number=10,
        function_type=FunctionType.AUTOSAR_FUNC,
        sw_module="TestModule"
    )

    # SWUT_MODEL_00001: Verify all fields
    assert func_info.name == "TestFunction"
    assert func_info.return_type == "void"
    assert func_info.parameters == []
    assert func_info.calls == []
    assert func_info.file_path == "/test.c"
    assert func_info.line_number == 10
    assert func_info.function_type == FunctionType.AUTOSAR_FUNC
    assert func_info.sw_module == "TestModule"
```

**Step 2: Run test to verify it passes (code already exists)**

```bash
pytest tests/unit/test_models.py::test_SWUT_MODEL_00001_function_info_creation -v
```

Expected: PASS (implementation exists)

**Step 3: Commit**

```bash
git add tests/unit/test_models.py
git commit -m "test: add SWUT_MODEL_00001 FunctionInfo creation test
"
```

---

### Task 2.4: Write Test - SWUT_MODEL_00002 (Parameter Creation)

**Files:**
- Modify: `tests/unit/test_models.py`

**Step 1: Write the failing test**

```python
# SWUT_MODEL_00002: Parameter creation
def test_SWUT_MODEL_00002_parameter_creation():
    """Test that Parameter can be created with all required fields."""
    from autosar_calltree.database.models import Parameter

    # SWUT_MODEL_00002: Create Parameter
    param = Parameter(
        name="testParam",
        type="uint32",
        is_pointer=False
    )

    # SWUT_MODEL_00002: Verify all fields
    assert param.name == "testParam"
    assert param.type == "uint32"
    assert param.is_pointer is False
```

**Step 2: Run test to verify it passes**

```bash
pytest tests/unit/test_models.py::test_SWUT_MODEL_00002_parameter_creation -v
```

Expected: PASS

**Step 3: Commit**

```bash
git add tests/unit/test_models.py
git commit -m "test: add SWUT_MODEL_00002 Parameter creation test
"
```

---

### Task 2.5: Complete Remaining models Tests (SWUT_MODEL_00003-00027)

**Files:**
- Modify: `tests/unit/test_models.py`

**Step 1: Write tests for remaining requirements**

For each requirement SWR_MODEL_00003 through SWR_MODEL_00027, write a test following the TDD pattern.

Example tests to write:
- FunctionType enum values
- CallTreeNode structure
- AnalysisResult structure
- AnalysisStatistics
- CircularDependency
- Type aliases
- Dataclass equality
- Dataclass serialization
- Edge cases (None values, empty lists, etc.)

**Step 2: Run all models tests**

```bash
pytest tests/unit/test_models.py -v
```

Expected: All PASS

**Step 3: Verify coverage**

```bash
pytest tests/unit/test_models.py --cov=src/autosar_calltree/database/models --cov-report=term
```

Expected: ≥95% coverage for models.py

**Step 4: Commit**

```bash
git add tests/unit/test_models.py
git commit -m "test: add remaining SWUT_MODEL_00003-00027 tests

Complete test coverage for models module
Achieves ≥95% coverage
"
```

---

### Task 2.6: Update Traceability for models

**Files:**
- Modify: `docs/TRACEABILITY.md`

**Step 1: Add traceability entries**

```markdown
## Models Module

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_MODEL_00001 | SWUT_MODEL_00001 | test_SWUT_MODEL_00001_function_info_creation | ✅ Pass |
| SWR_MODEL_00002 | SWUT_MODEL_00002 | test_SWUT_MODEL_00002_parameter_creation | ✅ Pass |
| SWR_MODEL_00003 | SWUT_MODEL_00003 | test_SWUT_MODEL_00003_[...] | ✅ Pass |
...
| SWR_MODEL_00027 | SWUT_MODEL_00027 | test_SWUT_MODEL_00027_[...] | ✅ Pass |
```

**Step 2: Run traceability check**

```bash
python scripts/check_traceability.py
```

Expected: ✅ All tests trace to requirements

**Step 3: Commit**

```bash
git add docs/TRACEABILITY.md
git commit -m "docs: add models traceability (SWR_MODEL_00001-00027)

Complete traceability matrix for models module
All tests validated
"
```

---

### Task 2.7: Push and Verify CI for models

**Step 1: Push to GitHub**

```bash
git push origin HEAD
```

**Step 2: Monitor GitHub Actions**

Wait for CI workflow to complete. Verify:
- Quality checks pass (black, isort, flake8, mypy)
- Tests pass on Python 3.8-3.12
- Coverage report generated
- Traceability check passes

**Step 3: If CI fails, fix issues**

```bash
# Run locally to debug
pytest tests/unit/test_models.py -v
black --check tests/unit/test_models.py
mypy src/autosar_calltree/database/models
```

**Step 4: Merge if all checks pass**

---

### Task 2.8: Analyze autosar_parser.py and Extract Requirements

**Files:**
- Reference: `src/autosar_calltree/parsers/autosar_parser.py`
- Create: `docs/requirements/parsers.md`

**Step 1: Analyze the AUTOSAR parser**

Identify:
- All AUTOSAR macro patterns (FUNC, FUNC_P2VAR, FUNC_P2CONST, VAR, P2VAR, P2CONST, CONST)
- Parameter extraction logic
- Function call extraction
- Return type parsing
- Static keyword handling
- Error handling

**Step 2: Document requirements (SWR_PARSER_AUTOSAR_00001-00015)**

Example:
```markdown
### SWR_PARSER_AUTOSAR_00001: FUNC Macro Parsing

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The parser shall recognize AUTOSAR FUNC macro function declarations with pattern:
```
FUNC(return_type, class) function_name(parameters);
```

**Acceptance Criteria:**
- [ ] Extracts return type
- [ ] Extracts function name
- [ ] Extracts parameter list
- [ ] Handles void return type
- [ ] Handles RTE_CODE and other class specifiers
```

**Step 3: Commit**

```bash
git add docs/requirements/parsers.md
git commit -m "docs: add AUTOSAR parser requirements (SWR_PARSER_AUTOSAR_00001-00015)
"
```

---

### Task 2.9: Create Test Fixtures for AUTOSAR Parser

**Files:**
- Create: `tests/fixtures/autosar_code/basic_functions.c`
- Create: `tests/fixtures/autosar_code/with_parameters.c`
- Create: `tests/fixtures/autosar_code/complex_macros.c`

**Step 1: Create basic_functions.c**

```c
/* Basic AUTOSAR function declarations */

FUNC(void, RTE_CODE) BasicFunction(void);

FUNC(uint8, APPLICATION_CODE) GetValue(void);

STATIC FUNC(void, CODE) InternalFunction(void);
```

**Step 2: Create with_parameters.c**

```c
/* AUTOSAR functions with parameters */

FUNC(void, RTE_CODE) InitFunction(
    VAR(uint8, AUTOMATIC) initValue,
    VAR(uint32, AUTOMATIC) flags
);

FUNC(Std_ReturnType, RTE_CODE) ProcessData(
    P2VAR(uint8, AUTOMATIC, APPL_DATA) buffer,
    VAR(uint32, AUTOMATIC) length
);
```

**Step 3: Create complex_macros.c**

```c
/* Complex AUTOSAR macros */

FUNC_P2VAR(uint8, AUTOMATIC, RTE_VAR) GetBuffer(VAR(uint32, AUTOMATIC) index);

FUNC_P2CONST(ConfigType, AUTOMATIC, APPL_CONST) GetConfig(void);
```

**Step 4: Commit**

```bash
git add tests/fixtures/autosar_code/
git commit -m "test: add AUTOSAR code fixtures for parser testing

Includes basic functions, parameters, and complex macros
"
```

---

### Task 2.10: Write autosar_parser Tests (SWUT_PARSER_AUTOSAR_00001-00015)

**Files:**
- Create: `tests/unit/test_autosar_parser.py`

**Step 1: Write tests following TDD**

For each requirement, write test, verify it passes.

Example:
```python
"""Tests for AUTOSAR parser (SWUT_PARSER_AUTOSAR_*)"""

# SWUT_PARSER_AUTOSAR_00001: FUNC macro parsing
def test_SWUT_PARSER_AUTOSAR_00001_func_macro_basic():
    """Test parsing basic FUNC macro declarations."""
    from autosar_calltree.parsers.autosar_parser import AutosarParser
    from pathlib import Path

    # Setup: Create test file
    test_code = """
    FUNC(void, RTE_CODE) TestFunction(void);
    """

    # Execute: Parse the code
    parser = AutosarParser()
    functions = parser.parse_string(test_code, "test.c")

    # Verify: Function extracted correctly
    assert len(functions) == 1
    func = functions[0]
    assert func.name == "TestFunction"
    assert func.return_type == "void"
    assert func.parameters == []
```

**Step 2: Run tests**

```bash
pytest tests/unit/test_autosar_parser.py -v
```

**Step 3: Verify coverage**

```bash
pytest tests/unit/test_autosar_parser.py --cov=src/autosar_calltree/parsers/autosar_parser --cov-report=term
```

**Step 4: Commit**

```bash
git add tests/unit/test_autosar_parser.py
git commit -m "test: add AUTOSAR parser tests (SWUT_PARSER_AUTOSAR_00001-00015)

Complete test coverage for AUTOSAR parser module
"
```

---

### Task 2.11: Analyze c_parser.py and Extract Requirements

**Files:**
- Reference: `src/autosar_calltree/parsers/c_parser.py`
- Modify: `docs/requirements/parsers.md`

**Step 1: Analyze the C parser**

Identify:
- Traditional C function patterns
- Function call extraction from bodies
- C keyword filtering
- AUTOSAR type recognition
- Parameter parsing
- Static function handling

**Step 2: Document requirements (SWR_PARSER_C_00001-00017)**

Add to existing parsers.md file.

**Step 3: Commit**

```bash
git add docs/requirements/parsers.md
git commit -m "docs: add C parser requirements (SWR_PARSER_C_00001-00017)
"
```

---

### Task 2.12: Create Test Fixtures for C Parser

**Files:**
- Create: `tests/fixtures/traditional_c/standard_functions.c`

**Step 1: Create fixture file**

```c
/* Traditional C function declarations */

void standardFunction(void);

int calculateSum(int a, int b);

static void internalHelper(void);

void processArray(uint8* data, uint32 length);
```

**Step 2: Commit**

```bash
git add tests/fixtures/traditional_c/
git commit -m "test: add traditional C code fixtures

Includes standard functions, parameters, static functions
"
```

---

### Task 2.13: Write c_parser Tests (SWUT_PARSER_C_00001-00017)

**Files:**
- Create: `tests/unit/test_c_parser.py`

**Step 1: Write tests following TDD**

Similar structure to autosar_parser tests.

**Step 2: Run tests**

```bash
pytest tests/unit/test_c_parser.py -v
```

**Step 3: Verify coverage**

```bash
pytest tests/unit/test_c_parser.py --cov=src/autosar_calltree/parsers/c_parser --cov-report=term
```

**Step 4: Commit**

```bash
git add tests/unit/test_c_parser.py
git commit -m "test: add C parser tests (SWUT_PARSER_C_00001-00017)

Complete test coverage for C parser module
"
```

---

### Task 2.14: Update Traceability for parsers

**Files:**
- Modify: `docs/TRACEABILITY.md`

**Step 1: Add parser traceability entries**

**Step 2: Run traceability check**

```bash
python scripts/check_traceability.py
```

**Step 3: Commit**

```bash
git add docs/TRACEABILITY.md
git commit -m "docs: add parsers traceability (SWR_PARSER_00001-00032)

Complete traceability for AUTOSAR and C parsers
"
```

---

### Task 2.15: Push and Verify CI for parsers

**Step 1: Push to GitHub**

```bash
git push origin HEAD
```

**Step 2: Verify CI passes**

**Step 3: If needed, fix and re-push**

---

## Phase 3: Wave 2 - Database & Analysis

### Task 3.1: Analyze function_database.py and Extract Requirements

**Files:**
- Reference: `src/autosar_calltree/database/function_database.py`
- Create: `docs/requirements/database.md`

**Step 1: Analyze the database module**

Focus on:
- Database building and scanning
- Three indexing structures
- Smart function lookup strategy
- Caching mechanism
- Cache validation
- Module configuration integration

**Step 2: Document requirements (SWR_DB_00001-00020)**

**Step 3: Commit**

---

### Task 3.2: Write function_database Tests (SWUT_DB_00001-00020)

**Files:**
- Create: `tests/unit/test_function_database.py`

**Step 1: Write tests following TDD**

Critical tests:
- Database building from source
- Function lookup by name
- Qualified function lookup
- Smart function matching (4-level strategy)
- Cache save/load
- Cache validation
- Module assignment

**Step 2: Run tests and verify coverage**

**Step 3: Commit**

---

### Task 3.3: Update Traceability for database

**Files:**
- Modify: `docs/TRACEABILITY.md`

**Step 1: Add traceability entries**

**Step 2: Run traceability check**

**Step 3: Commit**

---

### Task 3.4: Push and Verify CI

---

### Task 3.5: Analyze call_tree_builder.py and Extract Requirements

**Files:**
- Reference: `src/autosar_calltree/analyzers/call_tree_builder.py`
- Create: `docs/requirements/analyzers.md`

**Step 1: Analyze the call tree builder**

Focus on:
- Depth-first traversal
- Cycle detection
- Statistics collection
- Max depth enforcement
- RTE call inclusion

**Step 2: Document requirements (SWR_ANALYZER_00001-00015)**

**Step 3: Commit**

---

### Task 3.6: Write call_tree_builder Tests (SWUT_ANALYZER_00001-00015)

**Files:**
- Create: `tests/unit/test_call_tree_builder.py`

**Step 1: Write tests following TDD**

**Step 2: Run tests and verify coverage**

**Step 3: Commit**

---

### Task 3.7: Update Traceability and Verify CI

---

## Phase 4: Wave 3 - Output & Configuration

### Task 4.1: Analyze module_config.py and Extract Requirements

**Files:**
- Reference: `src/autosar_calltree/config/module_config.py`
- Create: `docs/requirements/config.md`

**Step 1: Analyze module configuration**

Focus on:
- YAML file loading
- File mappings (exact)
- Pattern mappings (glob)
- Default module
- Lookup caching
- Validation

**Step 2: Document requirements (SWR_CONFIG_00001-00010)**

**Step 3: Commit**

---

### Task 4.2: Write module_config Tests (SWUT_CONFIG_00001-00010)

**Files:**
- Create: `tests/unit/test_module_config.py`

**Step 1: Create test fixtures**

```yaml
# tests/fixtures/configs/module_mapping.yaml
version: "1.0"

file_mappings:
  demo.c: DemoModule

pattern_mappings:
  "hw_*.c": HardwareModule
  "sw_*.c": SoftwareModule

default_module: "Other"
```

**Step 2: Write tests**

**Step 3: Run tests and verify coverage**

**Step 4: Commit**

---

### Task 4.3: Update Traceability and Verify CI

---

### Task 4.4: Analyze mermaid_generator.py and Extract Requirements

**Files:**
- Reference: `src/autosar_calltree/generators/mermaid_generator.py`
- Create: `docs/requirements/generators.md`

**Step 1: Analyze the Mermaid generator**

Focus on:
- Sequence diagram generation
- Module-based participants
- Parameter display
- Return statements
- Function tables
- Text-based trees

**Step 2: Document requirements (SWR_GENERATOR_00001-00020)**

**Step 3: Commit**

---

### Task 4.5: Write mermaid_generator Tests (SWUT_GENERATOR_00001-00020)

**Files:**
- Create: `tests/unit/test_mermaid_generator.py`

**Step 1: Write tests following TDD**

Focus on:
- Diagram generation
- Mermaid syntax correctness
- Module name usage
- Parameter formatting
- Table generation

**Step 2: Run tests and verify coverage**

**Step 3: Commit**

---

### Task 4.6: Update Traceability and Verify CI

---

## Phase 5: Wave 4 - Integration

### Task 5.1: Analyze CLI and Extract Requirements

**Files:**
- Reference: `src/autosar_calltree/cli/main.py`
- Create: `docs/requirements/cli.md`

**Step 1: Analyze CLI**

Focus on:
- Command structure (analysis, list, search)
- Option handling
- Rich console output
- Exit codes
- Error handling

**Step 2: Document requirements (SWR_CLI_00001-00014)**

**Step 3: Commit**

---

### Task 5.2: Write CLI Tests (SWUT_CLI_00001-00014)

**Files:**
- Create: `tests/integration/test_cli.py`

**Step 1: Write tests using Click CliRunner**

```python
from click.testing import CliRunner
from autosar_calltree.cli import cli

def test_SWUT_CLI_00001_analysis_command():
    """Test basic analysis command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--start-function', 'Demo_Init', '--source-dir', 'demo'])

    assert result.exit_code == 0
    assert 'Demo_Init' in result.output
```

**Step 2: Run tests and verify coverage**

**Step 3: Commit**

---

### Task 5.3: Write End-to-End Tests

**Files:**
- Create: `tests/integration/test_end_to_end.py`

**Step 1: Write full workflow tests**

```python
def test_SWUT_E2E_00001_full_workflow():
    """Test complete workflow from source to diagram."""
    # 1. Build database
    # 2. Build call tree
    # 3. Generate diagram
    # 4. Verify output
```

**Step 2: Run tests and verify coverage**

**Step 3: Commit**

---

### Task 5.4: Update Final Traceability

**Files:**
- Modify: `docs/TRACEABILITY.md`

**Step 1: Add all remaining traceability entries**

**Step 2: Run final traceability check**

```bash
python scripts/check_traceability.py
```

Expected: ✅ All requirements traced

**Step 3: Commit**

---

### Task 5.5: Verify Complete Coverage

**Step 1: Run full test suite**

```bash
pytest tests/ -v --cov=autosar_calltree --cov-report=html --cov-report=term
```

Expected:
- All tests pass
- Coverage ≥95%

**Step 2: Generate coverage report**

```bash
open htmlcov/index.html
```

**Step 3: If coverage <95%, add missing tests**

---

### Task 5.6: Final CI Verification

**Step 1: Push all changes**

```bash
git push origin main
```

**Step 2: Monitor GitHub Actions**

Verify all workflows pass on:
- Python 3.8, 3.9, 3.10, 3.11, 3.12
- Quality checks
- Tests
- Traceability

**Step 3: Verify coverage report**

**Step 4: Merge to main**

---

## Phase 6: Documentation & Polish

### Task 6.1: Update README with Testing Instructions

**Files:**
- Modify: `README.md`

**Step 1: Add testing section**

```markdown
## Testing

Run the full test suite:
\`\`\`bash
pytest tests/ -v --cov=autosar_calltree --cov-report=html --cov-report=term
\`\`\`

Run specific test file:
\`\`\`bash
pytest tests/unit/test_models.py -v
\`\`\`

Run quality checks:
\`\`\`bash
scripts/run_quality.sh
\`\`\`

Check requirements traceability:
\`\`\`bash
python scripts/check_traceability.py
\`\`\`

## Coverage

Target: ≥95% code coverage

Current coverage: [Auto-update from CI]
```

**Step 2: Commit**

---

### Task 6.2: Create Requirements Index

**Files:**
- Modify: `docs/requirements/README.md`

**Step 1: Add complete requirements list**

```markdown
# Requirements Index

## Summary

| Module | Requirements | Status |
|--------|-------------|--------|
| Models | SWR_MODEL_00001-00027 | ✅ Complete |
| Parsers | SWR_PARSER_00001-00032 | ✅ Complete |
| Database | SWR_DB_00001-00020 | ✅ Complete |
| Analyzers | SWR_ANALYZER_00001-00015 | ✅ Complete |
| Config | SWR_CONFIG_00001-00010 | ✅ Complete |
| Generators | SWR_GENERATOR_00001-00020 | ✅ Complete |
| CLI | SWR_CLI_00001-00014 | ✅ Complete |
| **Total** | **138** | ✅ Complete |

## Documents

- [Models](models.md)
- [Parsers](parsers.md)
- [Database](database.md)
- [Analyzers](analyzers.md)
- [Configuration](config.md)
- [Generators](generators.md)
- [CLI](cli.md)
```

**Step 2: Commit**

---

### Task 6.3: Create Test Index

**Files:**
- Create: `docs/tests/README.md`

**Step 1: Add test case list**

```markdown
# Test Cases Index

## Summary

| Module | Test Cases | Coverage |
|--------|-----------|----------|
| Models | SWUT_MODEL_00001-00027 | 100% |
| Parsers | SWUT_PARSER_00001-00032 | 98% |
| Database | SWUT_DB_00001-00020 | 96% |
| Analyzers | SWUT_ANALYZER_00001-00015 | 95% |
| Config | SWUT_CONFIG_00001-00010 | 100% |
| Generators | SWUT_GENERATOR_00001-00020 | 97% |
| CLI | SWUT_CLI_00001-00014 | 94% |
| **Total** | **138** | **≥95%** |

## Documents

- [Models](models.md)
- [Parsers](parsers.md)
- [Database](database.md)
- [Analyzers](analyzers.md)
- [Configuration](config.md)
- [Generators](generators.md)
- [CLI](cli.md)
```

**Step 2: Commit**

---

### Task 6.4: Verify All Slash Commands Work

**Step 1: Test each command**

```bash
# /test
pytest tests/ -v --cov=autosar_calltree

# /quality
scripts/run_quality.sh

# /req
# (verify requirement management works)

# /gh-workflow
# (verify workflow generation works)

# /merge-pr
# (verify merge works)
```

**Step 2: Fix any issues**

**Step 3: Commit**

---

### Task 6.5: Final Verification

**Step 1: Run complete checklist**

```bash
# 1. Quality checks
scripts/run_quality.sh

# 2. All tests
pytest tests/ -v --cov=autosar_calltree --cov-report=term

# 3. Traceability
python scripts/check_traceability.py

# 4. Coverage threshold
pytest tests/ --cov=autosar_calltree --cov-fail-under=95
```

**Step 2: Verify all pass**

**Step 3: Tag release**

```bash
git tag -a v0.3.0 -m "Release v0.3.0: Complete testing and CI/CD infrastructure"
git push origin v0.3.0
```

---

## Success Criteria

At completion, verify:

- [x] All 138 requirements documented (SWR_*)
- [x] All 138 test cases implemented (SWUT_*)
- [x] 100% traceability (every SWUT maps to SWR)
- [x] Test coverage ≥95%
- [x] GitHub Actions CI passes on all Python versions
- [x] All quality checks pass (black, isort, flake8, mypy)
- [x] All slash commands work correctly
- [x] Documentation complete and up to date
- [x] Traceability checker validates all tests

---

## Notes

- **TDD Discipline**: Every test must fail first before implementation
- **Commit Frequency**: Commit after each passing test
- **CI Feedback**: Push after each module to catch issues early
- **Documentation First**: Requirements documented before tests
- **Traceability**: Every test must reference its requirement

---

**Related Documents:**
- Design Document: `docs/plans/2025-01-30-testing-cicd-design.md`
- Requirements Index: `docs/requirements/README.md`
- Test Cases Index: `docs/tests/README.md`
- Traceability Matrix: `docs/TRACEABILITY.md`
