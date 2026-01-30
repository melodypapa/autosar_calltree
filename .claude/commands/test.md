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
