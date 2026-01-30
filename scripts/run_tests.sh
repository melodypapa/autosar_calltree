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
