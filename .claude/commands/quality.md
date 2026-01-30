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
