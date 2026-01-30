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
