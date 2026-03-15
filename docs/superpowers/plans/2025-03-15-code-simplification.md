# Code Simplification Refactoring Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the AUTOSAR Call Tree Analyzer codebase to reduce duplication, standardize error handling, and extract large classes into focused modules.

**Architecture:** Create new utility modules (exceptions, statistics, tree_formatter) and extract FunctionVisitor from c_parser.py. All changes preserve backward compatibility through re-exports.

**Tech Stack:** Python 3.10+, dataclasses, pycparser, pytest, mypy, ruff

---

## File Structure

### New Files
| File | Purpose |
|------|---------|
| `src/autosar_calltree/exceptions.py` | Custom exception hierarchy |
| `src/autosar_calltree/utils/__init__.py` | Package init with exports |
| `src/autosar_calltree/utils/statistics.py` | Base statistics classes and formatter |
| `src/autosar_calltree/utils/tree_formatter.py` | Tree formatting utility |
| `src/autosar_calltree/parsers/function_visitor.py` | Extracted AST visitor |
| `tests/unit/test_exceptions.py` | Exception tests |
| `tests/unit/utils/__init__.py` | Test package init |
| `tests/unit/utils/test_statistics.py` | Statistics formatter tests |
| `tests/unit/utils/test_tree_formatter.py` | Tree formatter tests |

### Modified Files
| File | Changes |
|------|---------|
| `src/autosar_calltree/parsers/c_parser.py` | Extract FunctionVisitor, import from new module |
| `src/autosar_calltree/preprocessing/cpp_preprocessor.py` | Inherit from ProcessingStatistics |
| `src/autosar_calltree/database/function_database.py` | Use StatisticsFormatter |
| `src/autosar_calltree/generators/mermaid_generator.py` | Use TreeFormatter |
| `src/autosar_calltree/analyzers/call_tree_builder.py` | Use TreeFormatter |

---

## Chunk 1: Exception Hierarchy

### Task 1: Create Exception Classes

**Files:**
- Create: `src/autosar_calltree/exceptions.py`
- Test: `tests/unit/test_exceptions.py`

- [ ] **Step 1: Write failing tests for exception hierarchy**

Create `tests/unit/test_exceptions.py`:

```python
"""Tests for custom exception hierarchy."""

import pytest

from autosar_calltree.exceptions import (
    AutosarCalltreeError,
    ConfigError,
    DatabaseError,
    ParseError,
    PreprocessError,
)


class TestAutosarCalltreeError:
    """Tests for base exception class."""

    def test_is_exception_subclass(self):
        """Should be subclass of Exception."""
        assert issubclass(AutosarCalltreeError, Exception)

    def test_can_be_raised(self):
        """Should be raisable with message."""
        with pytest.raises(AutosarCalltreeError, match="test error"):
            raise AutosarCalltreeError("test error")


class TestParseError:
    """Tests for ParseError exception."""

    def test_inherits_from_base(self):
        """Should inherit from AutosarCalltreeError."""
        assert issubclass(ParseError, AutosarCalltreeError)

    def test_message_only(self):
        """Should work with message only."""
        error = ParseError("parsing failed")
        assert str(error) == "parsing failed"
        assert error.file_path is None
        assert error.line_number is None

    def test_with_file_path(self):
        """Should store file path."""
        error = ParseError("parsing failed", file_path="test.c")
        assert error.file_path == "test.c"
        assert error.line_number is None

    def test_with_file_and_line(self):
        """Should store file path and line number."""
        error = ParseError("parsing failed", file_path="test.c", line_number=42)
        assert error.file_path == "test.c"
        assert error.line_number == 42


class TestPreprocessError:
    """Tests for PreprocessError exception."""

    def test_inherits_from_base(self):
        """Should inherit from AutosarCalltreeError."""
        assert issubclass(PreprocessError, AutosarCalltreeError)

    def test_message_only(self):
        """Should work with message only."""
        error = PreprocessError("preprocessing failed")
        assert str(error) == "preprocessing failed"
        assert error.file_path is None
        assert error.error_type is None

    def test_with_file_path(self):
        """Should store file path."""
        error = PreprocessError("preprocessing failed", file_path="test.c")
        assert error.file_path == "test.c"

    def test_with_error_type(self):
        """Should store error type."""
        error = PreprocessError("cpp not found", error_type="cpp_not_found")
        assert error.error_type == "cpp_not_found"

    def test_all_fields(self):
        """Should store all fields."""
        error = PreprocessError(
            "timeout",
            file_path="test.c",
            error_type="timeout"
        )
        assert error.file_path == "test.c"
        assert error.error_type == "timeout"


class TestConfigError:
    """Tests for ConfigError exception."""

    def test_inherits_from_base(self):
        """Should inherit from AutosarCalltreeError."""
        assert issubclass(ConfigError, AutosarCalltreeError)

    def test_message(self):
        """Should work with message."""
        with pytest.raises(ConfigError, match="invalid config"):
            raise ConfigError("invalid config")


class TestDatabaseError:
    """Tests for DatabaseError exception."""

    def test_inherits_from_base(self):
        """Should inherit from AutosarCalltreeError."""
        assert issubclass(DatabaseError, AutosarCalltreeError)

    def test_message(self):
        """Should work with message."""
        with pytest.raises(DatabaseError, match="cache error"):
            raise DatabaseError("cache error")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_exceptions.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'autosar_calltree.exceptions'"

- [ ] **Step 3: Create the exceptions module**

Create `src/autosar_calltree/exceptions.py`:

```python
"""
Custom exception hierarchy for AUTOSAR Call Tree Analyzer.

This module provides specialized exceptions for better error tracing
and handling throughout the codebase.
"""

from typing import Optional


__all__ = [
    "AutosarCalltreeError",
    "ParseError",
    "PreprocessError",
    "ConfigError",
    "DatabaseError",
]


class AutosarCalltreeError(Exception):
    """Base exception for all autosar-calltree errors."""
    pass


class ParseError(AutosarCalltreeError):
    """
    Raised when parsing fails.

    Attributes:
        file_path: Path to the file being parsed (optional)
        line_number: Line number where error occurred (optional)
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None
    ):
        self.file_path = file_path
        self.line_number = line_number
        super().__init__(message)


class PreprocessError(AutosarCalltreeError):
    """
    Raised when preprocessing fails.

    Attributes:
        file_path: Path to the file being preprocessed (optional)
        error_type: Type of error ('cpp_not_found', 'cpp_error', 'timeout')
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        error_type: Optional[str] = None
    ):
        self.file_path = file_path
        self.error_type = error_type
        super().__init__(message)


class ConfigError(AutosarCalltreeError):
    """Raised when configuration is invalid."""
    pass


class DatabaseError(AutosarCalltreeError):
    """Raised when database operations fail."""
    pass
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_exceptions.py -v`
Expected: PASS (8 tests)

- [ ] **Step 5: Run full test suite to ensure no regressions**

Run: `pytest`
Expected: PASS (all existing tests)

- [ ] **Step 6: Run type checking**

Run: `mypy src/autosar_calltree/exceptions.py`
Expected: PASS (no errors)

- [ ] **Step 7: Run linting**

Run: `ruff check src/autosar_calltree/exceptions.py tests/unit/test_exceptions.py`
Expected: PASS (no errors)

- [ ] **Step 8: Commit**

```bash
git add src/autosar_calltree/exceptions.py tests/unit/test_exceptions.py
git commit -m "$(cat <<'EOF'
feat: Add custom exception hierarchy

Add specialized exceptions for better error tracing:
- AutosarCalltreeError: base exception
- ParseError: parsing failures with file/line context
- PreprocessError: preprocessing failures with error type
- ConfigError: configuration validation failures
- DatabaseError: database operation failures

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Chunk 2: Statistics Utilities

### Task 2: Create Utils Package and Statistics Module

**Files:**
- Create: `src/autosar_calltree/utils/__init__.py`
- Create: `src/autosar_calltree/utils/statistics.py`
- Create: `tests/unit/utils/__init__.py`
- Test: `tests/unit/utils/test_statistics.py`

- [ ] **Step 1: Create utils package directory**

Run:
```bash
mkdir -p src/autosar_calltree/utils
mkdir -p tests/unit/utils
```

- [ ] **Step 2: Create utils test package init**

Create `tests/unit/utils/__init__.py`:

```python
"""Tests for utility modules."""
```

- [ ] **Step 3: Write failing tests for ProcessingResult**

Create `tests/unit/utils/test_statistics.py`:

```python
"""Tests for statistics utilities."""

from dataclasses import fields
from pathlib import Path

import pytest

from autosar_calltree.utils.statistics import (
    ProcessingResult,
    ProcessingStatistics,
    StatisticsFormatter,
)


class TestProcessingResult:
    """Tests for ProcessingResult dataclass."""

    def test_required_fields(self):
        """Should have source_file and success as required."""
        result = ProcessingResult(source_file=Path("test.c"), success=True)
        assert result.source_file == Path("test.c")
        assert result.success is True

    def test_optional_error_message(self):
        """Should have optional error_message."""
        result = ProcessingResult(
            source_file=Path("test.c"),
            success=False,
            error_message="test error"
        )
        assert result.error_message == "test error"

    def test_default_error_message_is_none(self):
        """Should default error_message to None."""
        result = ProcessingResult(source_file=Path("test.c"), success=True)
        assert result.error_message is None

    def test_is_dataclass(self):
        """Should be a dataclass."""
        from dataclasses import is_dataclass
        assert is_dataclass(ProcessingResult)


class TestProcessingStatistics:
    """Tests for ProcessingStatistics dataclass."""

    def test_default_values(self):
        """Should have default values."""
        stats = ProcessingStatistics()
        assert stats.total_files == 0
        assert stats.successful == 0
        assert stats.failed == 0
        assert stats.skipped == 0
        assert stats.results == []

    def test_custom_values(self):
        """Should accept custom values."""
        stats = ProcessingStatistics(
            total_files=10,
            successful=8,
            failed=2
        )
        assert stats.total_files == 10
        assert stats.successful == 8
        assert stats.failed == 2

    def test_success_rate_zero_when_no_files(self):
        """Should return 0.0 when no files processed."""
        stats = ProcessingStatistics()
        assert stats.success_rate == 0.0

    def test_success_rate_calculation(self):
        """Should calculate success rate correctly."""
        stats = ProcessingStatistics(total_files=10, successful=8, failed=2)
        assert stats.success_rate == 80.0

    def test_success_rate_100_percent(self):
        """Should return 100.0 when all successful."""
        stats = ProcessingStatistics(total_files=5, successful=5, failed=0)
        assert stats.success_rate == 100.0


class TestStatisticsFormatter:
    """Tests for StatisticsFormatter."""

    def test_format_summary_basic(self):
        """Should format basic summary."""
        stats = ProcessingStatistics(
            total_files=10,
            successful=8,
            failed=2
        )
        result = StatisticsFormatter.format_summary("Test Stage", stats)
        assert "Test Stage:" in result
        assert "Files processed: 10" in result
        assert "Successful:      8" in result
        assert "Failed:          2" in result

    def test_format_summary_with_skipped(self):
        """Should include skipped when > 0."""
        stats = ProcessingStatistics(
            total_files=10,
            successful=7,
            failed=2,
            skipped=1
        )
        result = StatisticsFormatter.format_summary("Test Stage", stats)
        assert "Skipped:         1" in result

    def test_format_summary_without_skipped(self):
        """Should not include skipped when 0."""
        stats = ProcessingStatistics(total_files=10, successful=10, failed=0)
        result = StatisticsFormatter.format_summary("Test Stage", stats)
        assert "Skipped" not in result

    def test_format_summary_with_failures(self):
        """Should list failed files."""
        stats = ProcessingStatistics(
            total_files=2,
            successful=1,
            failed=1,
            results=[
                ProcessingResult(Path("ok.c"), True),
                ProcessingResult(Path("fail.c"), False, "error message"),
            ]
        )
        result = StatisticsFormatter.format_summary("Test Stage", stats, show_failures=True)
        assert "Failed files:" in result
        assert "fail.c: error message" in result

    def test_format_summary_hide_failures(self):
        """Should hide failures when show_failures=False."""
        stats = ProcessingStatistics(
            total_files=2,
            successful=1,
            failed=1,
            results=[
                ProcessingResult(Path("ok.c"), True),
                ProcessingResult(Path("fail.c"), False, "error message"),
            ]
        )
        result = StatisticsFormatter.format_summary("Test Stage", stats, show_failures=False)
        assert "Failed files:" not in result

    def test_format_summary_with_extra_lines(self):
        """Should include extra lines."""
        stats = ProcessingStatistics(total_files=5, successful=5, failed=0)
        extra = ["", "Additional info: test"]
        result = StatisticsFormatter.format_summary("Test Stage", stats, extra_lines=extra)
        assert "Additional info: test" in result
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `pytest tests/unit/utils/test_statistics.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'autosar_calltree.utils'"

- [ ] **Step 5: Create utils package init**

Create `src/autosar_calltree/utils/__init__.py`:

```python
"""Utility modules for autosar-calltree."""

from .statistics import (
    ProcessingResult,
    ProcessingStatistics,
    StatisticsFormatter,
)

__all__ = [
    "ProcessingResult",
    "ProcessingStatistics",
    "StatisticsFormatter",
]
```

- [ ] **Step 6: Create statistics module**

Create `src/autosar_calltree/utils/statistics.py`:

```python
"""
Statistics utilities for processing operations.

This module provides base classes and formatters for collecting
and displaying processing statistics across the codebase.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ProcessingResult:
    """
    Base result for any processing operation.

    Subclasses may add additional fields for their specific needs
    (e.g., ParseResult adds functions, autosar_functions, traditional_functions).
    """
    source_file: Path
    success: bool
    error_message: Optional[str] = None


@dataclass
class ProcessingStatistics:
    """
    Base statistics for batch processing operations.

    Subclasses may add additional fields for their specific needs
    (e.g., ParseStatistics adds autosar_functions, traditional_functions, total_functions).
    """
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    results: List[ProcessingResult] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        processed = self.successful + self.failed
        return (self.successful / processed * 100.0) if processed > 0 else 0.0


class StatisticsFormatter:
    """Format processing statistics for display."""

    @staticmethod
    def format_summary(
        stage_name: str,
        stats: ProcessingStatistics,
        extra_lines: Optional[List[str]] = None,
        show_failures: bool = True
    ) -> str:
        """
        Generate a human-readable summary.

        Args:
            stage_name: Name of the processing stage (e.g., "Preprocessing Stage")
            stats: Statistics object to format
            extra_lines: Optional additional lines for stage-specific metrics
            show_failures: Whether to list failed files

        Returns:
            Formatted summary string
        """
        lines = [
            f"{stage_name}:",
            f"  Files processed: {stats.total_files}",
            f"  Successful:      {stats.successful}",
            f"  Failed:          {stats.failed}",
        ]

        if stats.skipped > 0:
            lines.append(f"  Skipped:         {stats.skipped}")

        if extra_lines:
            lines.extend(extra_lines)

        if show_failures and stats.failed > 0:
            lines.append("  Failed files:")
            for result in stats.results:
                if not result.success:
                    lines.append(
                        f"    - {result.source_file.name}: {result.error_message}"
                    )

        return "\n".join(lines)
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `pytest tests/unit/utils/test_statistics.py -v`
Expected: PASS (14 tests)

- [ ] **Step 8: Run full test suite**

Run: `pytest`
Expected: PASS (all tests)

- [ ] **Step 9: Run type checking**

Run: `mypy src/autosar_calltree/utils/`
Expected: PASS (no errors)

- [ ] **Step 10: Run linting**

Run: `ruff check src/autosar_calltree/utils/ tests/unit/utils/`
Expected: PASS (no errors)

- [ ] **Step 11: Commit**

```bash
git add src/autosar_calltree/utils/ tests/unit/utils/
git commit -m "$(cat <<'EOF'
feat: Add statistics utilities module

Add base classes for processing statistics:
- ProcessingResult: base result with source_file, success, error_message
- ProcessingStatistics: base stats with success_rate property
- StatisticsFormatter: format_summary() for human-readable output

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Chunk 3: Tree Formatter

### Task 3: Create TreeFormatter Utility

**Files:**
- Create: `src/autosar_calltree/utils/tree_formatter.py`
- Test: `tests/unit/utils/test_tree_formatter.py`

- [ ] **Step 1: Write failing tests for TreeFormatter**

Add to `tests/unit/utils/test_tree_formatter.py`:

```python
"""Tests for tree formatter utility."""

from pathlib import Path

import pytest

from autosar_calltree.database.models import (
    CallTreeNode,
    FunctionInfo,
    FunctionType,
)
from autosar_calltree.utils.tree_formatter import TreeFormatter


@pytest.fixture
def sample_function_info():
    """Create a sample FunctionInfo for testing."""
    return FunctionInfo(
        name="main",
        return_type="void",
        file_path=Path("src/main.c"),
        line_number=10,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )


@pytest.fixture
def sample_child_function_info():
    """Create a sample child FunctionInfo for testing."""
    return FunctionInfo(
        name="helper",
        return_type="int",
        file_path=Path("src/helper.c"),
        line_number=20,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
    )


class TestTreeFormatter:
    """Tests for TreeFormatter."""

    def test_format_single_node(self, sample_function_info):
        """Should format a single node without children."""
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[],
        )
        result = TreeFormatter.format_tree(node)
        assert "main (main.c:10)" in result

    def test_format_with_child(self, sample_function_info, sample_child_function_info):
        """Should format node with child."""
        child = CallTreeNode(
            function_info=sample_child_function_info,
            depth=1,
            children=[],
        )
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[child],
        )
        result = TreeFormatter.format_tree(node)
        assert "main (main.c:10)" in result
        assert "helper (helper.c:20)" in result
        assert "└──" in result

    def test_format_multiple_children(self, sample_function_info):
        """Should format multiple children with correct connectors."""
        child1 = CallTreeNode(
            function_info=FunctionInfo(
                name="child1",
                return_type="void",
                file_path=Path("src/a.c"),
                line_number=1,
                is_static=False,
                function_type=FunctionType.TRADITIONAL_C,
            ),
            depth=1,
            children=[],
        )
        child2 = CallTreeNode(
            function_info=FunctionInfo(
                name="child2",
                return_type="void",
                file_path=Path("src/b.c"),
                line_number=2,
                is_static=False,
                function_type=FunctionType.TRADITIONAL_C,
            ),
            depth=1,
            children=[],
        )
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[child1, child2],
        )
        result = TreeFormatter.format_tree(node)
        assert "├── child1" in result
        assert "└── child2" in result

    def test_format_recursive_node(self, sample_function_info):
        """Should mark recursive nodes."""
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[],
            is_recursive=True,
        )
        result = TreeFormatter.format_tree(node)
        assert "[RECURSIVE]" in result

    def test_format_without_file(self, sample_function_info):
        """Should hide file when show_file=False."""
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[],
        )
        result = TreeFormatter.format_tree(node, show_file=False)
        assert "main.c" not in result
        assert "main" in result

    def test_format_without_line(self, sample_function_info):
        """Should hide line number when show_line=False."""
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[],
        )
        result = TreeFormatter.format_tree(node, show_line=False)
        assert ":10" not in result
        assert "main.c" in result

    def test_format_nested_children(self, sample_function_info):
        """Should format nested children with correct indentation."""
        grandchild = CallTreeNode(
            function_info=FunctionInfo(
                name="grandchild",
                return_type="void",
                file_path=Path("src/gc.c"),
                line_number=5,
                is_static=False,
                function_type=FunctionType.TRADITIONAL_C,
            ),
            depth=2,
            children=[],
        )
        child = CallTreeNode(
            function_info=FunctionInfo(
                name="child",
                return_type="void",
                file_path=Path("src/c.c"),
                line_number=3,
                is_static=False,
                function_type=FunctionType.TRADITIONAL_C,
            ),
            depth=1,
            children=[grandchild],
        )
        node = CallTreeNode(
            function_info=sample_function_info,
            depth=0,
            children=[child],
        )
        result = TreeFormatter.format_tree(node)
        assert "main" in result
        assert "child" in result
        assert "grandchild" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/utils/test_tree_formatter.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'autosar_calltree.utils.tree_formatter'"

- [ ] **Step 3: Create tree_formatter module**

Create `src/autosar_calltree/utils/tree_formatter.py`:

```python
"""
Tree formatter utility for call tree visualization.

This module provides utilities for formatting call trees as
text-based tree diagrams.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..database.models import CallTreeNode


class TreeFormatter:
    """Format call trees as text-based tree diagrams."""

    @staticmethod
    def format_tree(
        root: "CallTreeNode",
        show_file: bool = True,
        show_line: bool = True
    ) -> str:
        """
        Generate text-based tree representation.

        Args:
            root: Root node of call tree
            show_file: Include file name in output
            show_line: Include line number in output

        Returns:
            Formatted tree string
        """
        lines = []

        def format_location(node: "CallTreeNode") -> str:
            """Format file:line location."""
            if not show_file:
                return ""
            file_name = Path(node.function_info.file_path).name
            if show_line:
                return f" ({file_name}:{node.function_info.line_number})"
            return f" ({file_name})"

        def traverse(node: "CallTreeNode", prefix: str = "", is_last: bool = True):
            connector = "└── " if is_last else "├── "

            func_name = node.function_info.name
            location = format_location(node)
            line = f"{prefix}{connector}{func_name}{location}"

            if node.is_recursive:
                line += " [RECURSIVE]"

            lines.append(line)

            if node.children:
                new_prefix = prefix + ("    " if is_last else "│   ")
                for idx, child in enumerate(node.children):
                    is_last_child = idx == len(node.children) - 1
                    traverse(child, new_prefix, is_last_child)

        # Root node (no prefix)
        func_name = root.function_info.name
        location = format_location(root)
        lines.append(f"{func_name}{location}")

        for idx, child in enumerate(root.children):
            is_last = idx == len(root.children) - 1
            traverse(child, "", is_last)

        return "\n".join(lines)
```

- [ ] **Step 4: Update utils/__init__.py to export TreeFormatter**

Edit `src/autosar_calltree/utils/__init__.py`:

```python
"""Utility modules for autosar-calltree."""

from .statistics import (
    ProcessingResult,
    ProcessingStatistics,
    StatisticsFormatter,
)
from .tree_formatter import TreeFormatter

__all__ = [
    "ProcessingResult",
    "ProcessingStatistics",
    "StatisticsFormatter",
    "TreeFormatter",
]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/unit/utils/test_tree_formatter.py -v`
Expected: PASS (7 tests)

- [ ] **Step 6: Run full test suite**

Run: `pytest`
Expected: PASS (all tests)

- [ ] **Step 7: Run type checking**

Run: `mypy src/autosar_calltree/utils/`
Expected: PASS (no errors)

- [ ] **Step 8: Run linting**

Run: `ruff check src/autosar_calltree/utils/ tests/unit/utils/`
Expected: PASS (no errors)

- [ ] **Step 9: Commit**

```bash
git add src/autosar_calltree/utils/ tests/unit/utils/
git commit -m "$(cat <<'EOF'
feat: Add TreeFormatter utility

Add TreeFormatter class for text-based tree visualization:
- format_tree() method with show_file and show_line options
- Handles recursive nodes with [RECURSIVE] marker
- Uses box-drawing characters for tree connectors

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Chunk 4: Extract FunctionVisitor

### Task 4: Create function_visitor.py and Update c_parser.py

**Files:**
- Create: `src/autosar_calltree/parsers/function_visitor.py`
- Modify: `src/autosar_calltree/parsers/c_parser.py`

- [ ] **Step 1: Verify FunctionVisitor location in c_parser.py**

Run: `grep -n "class FunctionVisitor" src/autosar_calltree/parsers/c_parser.py`
Expected: Output shows `60:class FunctionVisitor(c_ast.NodeVisitor):`

This confirms FunctionVisitor starts at line 60. The class spans approximately lines 60-434.

- [ ] **Step 2: Create function_visitor.py with extracted class**

Create `src/autosar_calltree/parsers/function_visitor.py`:

```python
"""
AST visitor for extracting function definitions from C code.

This module provides the FunctionVisitor class that walks pycparser
AST nodes to extract function definitions and calls.
"""

from pathlib import Path
from typing import List, Optional, Set

from pycparser import c_ast

from ..database.models import FunctionCall, FunctionInfo, FunctionType, Parameter


class FunctionVisitor(c_ast.NodeVisitor):
    """AST visitor to extract function definitions and calls."""

    # C keywords to exclude from function call extraction
    C_KEYWORDS = {
        "if", "else", "while", "for", "do", "switch", "case", "default",
        "return", "break", "continue", "goto", "sizeof", "typedef",
        "struct", "union", "enum", "const", "volatile", "static",
        "extern", "auto", "register", "inline", "__inline", "__inline__",
        "restrict", "__restrict", "__restrict__", "_Bool", "_Complex", "_Imaginary",
    }

    # Common AUTOSAR types
    AUTOSAR_TYPES = {
        "uint8", "uint16", "uint32", "uint64",
        "sint8", "sint16", "sint32", "sint64",
        "boolean", "Boolean", "float32", "float64",
        "Std_ReturnType", "StatusType",
    }

    # AUTOSAR and standard C macros to exclude
    AUTOSAR_MACROS = {
        "INT8_C", "INT16_C", "INT32_C", "INT64_C",
        "UINT8_C", "UINT16_C", "UINT32_C", "UINT64_C",
        "INTMAX_C", "UINTMAX_C", "TS_MAKEREF2CFG",
        "TS_MAKENULLREF2CFG", "TS_MAKEREFLIST2CFG",
        "STD_ON", "STD_OFF",
    }

    def __init__(self, file_path: Path, content: str):
        """
        Initialize the visitor.

        Args:
            file_path: Path to the source file
            content: Original source code content
        """
        self.file_path = file_path
        self.content = content
        self.functions: List[FunctionInfo] = []

    def visit_FuncDef(self, node: c_ast.FuncDef) -> None:
        """
        Visit a function definition node.

        Args:
            node: Function definition AST node
        """
        # Extract function name
        func_name = node.decl.name

        # Extract return type
        return_type = self._extract_return_type(node)

        # Extract parameters
        parameters = self._extract_parameters(node)

        # Determine if static
        is_static = self._is_static(node)

        # Get line number
        line_number = node.coord.line if node.coord else 0

        # Extract function calls from body
        calls = self._extract_function_calls(node)

        # Create FunctionInfo
        func_info = FunctionInfo(
            name=func_name,
            return_type=return_type,
            parameters=parameters,
            function_type=FunctionType.TRADITIONAL_C,
            file_path=self.file_path,
            line_number=line_number,
            calls=calls,
            is_static=is_static,
        )

        self.functions.append(func_info)

    def _extract_return_type(self, node: c_ast.FuncDef) -> str:
        """Extract return type from function definition."""
        decl_type = node.decl.type

        if isinstance(decl_type, c_ast.FuncDecl):
            return_type_node = decl_type.type
        else:
            return_type_node = decl_type

        pycparser_return_type = self._get_return_type_from_node(return_type_node)

        # Workaround: pycparser doesn't preserve const qualifiers in some cases
        if "const" not in pycparser_return_type.lower() and node.coord:
            source_return_type = self._extract_return_type_from_source(node)
            if source_return_type and "const" in source_return_type.lower():
                return source_return_type

        return pycparser_return_type

    def _get_return_type_from_node(self, return_type_node: c_ast.Node) -> str:
        """Extract return type from an AST node."""
        if isinstance(return_type_node, c_ast.PtrDecl):
            ptr_quals = []
            if hasattr(return_type_node, "qualifiers") and return_type_node.qualifiers:
                ptr_quals = list(return_type_node.qualifiers)

            underlying_type = return_type_node.type
            base_type = self._get_type_name(underlying_type, include_quals=True)

            if ptr_quals:
                return f"{base_type}* {' '.join(ptr_quals)}"
            return f"{base_type}*"

        if isinstance(return_type_node, c_ast.ArrayDecl):
            underlying_type = return_type_node.type
            base_type = self._get_type_name(underlying_type, include_quals=True)
            return f"{base_type}[]"

        return self._get_type_name(return_type_node, include_quals=True)

    def _extract_return_type_from_source(self, node: c_ast.FuncDef) -> Optional[str]:
        """Extract return type from original source code as a fallback."""
        import re

        if not self.content:
            return None

        func_name = node.decl.name
        pattern = rf"([\w\s\*]+)\s+{re.escape(func_name)}\s*\("
        match = re.search(pattern, self.content)

        if not match:
            return None

        return_type_candidate = match.group(1).strip()

        if re.match(r"^[\w\s\*]+$", return_type_candidate):
            return return_type_candidate

        return None

    def _get_type_name(self, type_node: c_ast.Node, include_quals: bool = False) -> str:
        """Get the name of a type node."""
        if isinstance(type_node, c_ast.TypeDecl):
            quals = []
            if include_quals and hasattr(type_node, "qualifiers"):
                if type_node.qualifiers:
                    quals = list(type_node.qualifiers)

            if isinstance(type_node.type, c_ast.IdentifierType):
                type_name = " ".join(type_node.type.names)
            elif isinstance(type_node.type, c_ast.Struct):
                type_name = f"struct {type_node.type.name}"
            elif isinstance(type_node.type, c_ast.Union):
                type_name = f"union {type_node.type.name}"
            elif isinstance(type_node.type, c_ast.Enum):
                type_name = f"enum {type_node.type.name}"
            else:
                type_name = "unknown"

            if quals:
                return f"{' '.join(quals)} {type_name}"
            return type_name

        if isinstance(type_node, c_ast.PtrDecl):
            quals = []
            if include_quals and hasattr(type_node, "qualifiers"):
                if type_node.qualifiers:
                    quals = list(type_node.qualifiers)

            underlying_name = self._get_type_name(type_node.type, include_quals=include_quals)

            if quals:
                return f"{' '.join(quals)} {underlying_name}"
            return underlying_name

        if isinstance(type_node, c_ast.FuncDecl):
            return self._get_type_name(type_node.type, include_quals=include_quals)

        return "unknown"

    def _extract_parameters(self, node: c_ast.FuncDef) -> List[Parameter]:
        """Extract parameters from function definition."""
        parameters: List[Parameter] = []

        decl = node.decl
        if not hasattr(decl.type, "args") or decl.type.args is None:
            return parameters

        for param in decl.type.args.params:
            if isinstance(param, c_ast.Typename) and hasattr(param.type, "names"):
                if "void" in param.type.names:
                    continue

            param_info = self._extract_parameter(param)
            if param_info:
                parameters.append(param_info)

        return parameters

    def _extract_parameter(self, param: c_ast.Node) -> Optional[Parameter]:
        """Extract a single parameter from AST node."""
        param_name = ""
        is_const = False

        if isinstance(param, c_ast.Decl):
            param_name = param.name or ""
            type_node = param.type
            if hasattr(type_node, "qualifiers") and type_node.qualifiers:
                is_const = "const" in type_node.qualifiers
        elif isinstance(param, c_ast.Typename):
            type_node = param.type
            if hasattr(type_node, "qualifiers") and type_node.qualifiers:
                is_const = "const" in type_node.qualifiers
        else:
            return None

        is_pointer = False
        if isinstance(type_node, c_ast.PtrDecl):
            is_pointer = True
            if hasattr(type_node, "qualifiers") and type_node.qualifiers:
                if "const" in type_node.qualifiers:
                    is_const = True
            type_node = type_node.type

        param_type = self._get_type_name(type_node, include_quals=True)

        return Parameter(
            name=param_name,
            param_type=param_type,
            is_pointer=is_pointer,
            is_const=is_const,
        )

    def _is_static(self, node: c_ast.FuncDef) -> bool:
        """Check if function is static."""
        if hasattr(node.decl, "storage") and node.decl.storage:
            return "static" in node.decl.storage
        return False

    def _extract_function_calls(self, node: c_ast.FuncDef) -> List[FunctionCall]:
        """Extract function calls from function body."""

        class CallVisitor(c_ast.NodeVisitor):
            def __init__(self, parent: FunctionVisitor):
                self.parent = parent
                self.calls: List[FunctionCall] = []
                self.seen: Set[str] = set()

            def visit_FuncCall(self, call_node: c_ast.FuncCall) -> None:
                """Visit a function call node."""
                if isinstance(call_node.name, c_ast.IdentifierType):
                    func_name = call_node.name.names[0]
                elif isinstance(call_node.name, c_ast.ID):
                    func_name = call_node.name.name
                else:
                    return

                # Skip C keywords
                if func_name in FunctionVisitor.C_KEYWORDS:
                    return

                # Skip AUTOSAR types (might be casts)
                if func_name in FunctionVisitor.AUTOSAR_TYPES:
                    return

                # Skip AUTOSAR macros
                if func_name in FunctionVisitor.AUTOSAR_MACROS:
                    return

                # Track unique calls
                if func_name not in self.seen:
                    self.seen.add(func_name)
                    self.calls.append(
                        FunctionCall(
                            name=func_name,
                            is_conditional=False,
                            condition=None,
                            is_loop=False,
                            loop_condition=None,
                        )
                    )

        call_visitor = CallVisitor(self)
        call_visitor.visit(node)

        return call_visitor.calls
```

- [ ] **Step 3: Update c_parser.py to import FunctionVisitor**

Edit `src/autosar_calltree/parsers/c_parser.py`:

**3a. Add import at top of file (after existing imports):**
```python
from .function_visitor import FunctionVisitor
```

**3b. Remove the FunctionVisitor class (approximately lines 60-434):**
Delete everything from `class FunctionVisitor(c_ast.NodeVisitor):` to the end of the `_extract_function_calls` method.

**3c. Remove the constant definitions from CParser class:**
Delete the `C_KEYWORDS`, `AUTOSAR_TYPES`, and `AUTOSAR_MACROS` class attributes from inside the `CParser` class. Use grep to find their location:
```bash
grep -n "C_KEYWORDS = {" src/autosar_calltree/parsers/c_parser.py
```
Delete all three constant definitions (they are grouped together).

**3d. Add re-export constants inside the CParser class body:**
After removing the old constants, add these lines inside the `CParser` class:
```python
    # Re-export constants for backward compatibility
    C_KEYWORDS = FunctionVisitor.C_KEYWORDS
    AUTOSAR_TYPES = FunctionVisitor.AUTOSAR_TYPES
    AUTOSAR_MACROS = FunctionVisitor.AUTOSAR_MACROS
```

- [ ] **Step 4: Run tests to verify no regressions**

Run: `pytest tests/unit/test_c_parser.py -v`
Expected: PASS (all existing tests)

- [ ] **Step 5: Run full test suite**

Run: `pytest`
Expected: PASS (all tests)

- [ ] **Step 6: Run type checking**

Run: `mypy src/autosar_calltree/parsers/`
Expected: PASS (no errors)

- [ ] **Step 7: Run linting**

Run: `ruff check src/autosar_calltree/parsers/`
Expected: PASS (no errors)

- [ ] **Step 8: Commit**

```bash
git add src/autosar_calltree/parsers/function_visitor.py src/autosar_calltree/parsers/c_parser.py
git commit -m "$(cat <<'EOF'
refactor: Extract FunctionVisitor from c_parser.py

Extract FunctionVisitor class to separate module:
- Move ~375 lines of AST traversal logic to function_visitor.py
- Keep constants (C_KEYWORDS, AUTOSAR_TYPES, AUTOSAR_MACROS) on FunctionVisitor
- Re-export constants from CParser for backward compatibility
- c_parser.py reduced from ~1190 to ~750 lines

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Chunk 5: Migrate to StatisticsFormatter

### Task 5: Update cpp_preprocessor.py

**Files:**
- Modify: `src/autosar_calltree/preprocessing/cpp_preprocessor.py`

- [ ] **Step 1: Update imports in cpp_preprocessor.py**

Add imports at top of file:
```python
from ..utils.statistics import ProcessingResult, ProcessingStatistics, StatisticsFormatter
```

- [ ] **Step 2: Update PreprocessResult to inherit from ProcessingResult**

Change:
```python
@dataclass
class PreprocessResult:
    source_file: Path
    output_file: Optional[Path]
    success: bool
    error_message: Optional[str] = None
    error_type: Optional[str] = None
```

To:
```python
@dataclass
class PreprocessResult(ProcessingResult):
    """Result of preprocessing a single file."""
    output_file: Optional[Path] = None
    error_type: Optional[str] = None
```

- [ ] **Step 3: Update PreprocessStatistics to inherit from ProcessingStatistics**

Change:
```python
@dataclass
class PreprocessStatistics:
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    results: List[PreprocessResult] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        processed = self.successful + self.failed
        if processed == 0:
            return 0.0
        return (self.successful / processed) * 100.0
```

To:
```python
@dataclass
class PreprocessStatistics(ProcessingStatistics):
    """Statistics for preprocessing stage."""
    results: List[PreprocessResult] = field(default_factory=list)
```

- [ ] **Step 4: Update get_statistics_summary to use StatisticsFormatter**

Change the method to:
```python
def get_statistics_summary(self, stats: PreprocessStatistics) -> str:
    """Generate a human-readable summary of preprocessing statistics."""
    return StatisticsFormatter.format_summary("Preprocessing Stage", stats)
```

- [ ] **Step 5: Run tests to verify no regressions**

Run: `pytest`
Expected: PASS (all tests)

- [ ] **Step 6: Run type checking**

Run: `mypy src/autosar_calltree/preprocessing/`
Expected: PASS (no errors)

- [ ] **Step 7: Commit**

```bash
git add src/autosar_calltree/preprocessing/cpp_preprocessor.py
git commit -m "$(cat <<'EOF'
refactor: Update cpp_preprocessor to use statistics utilities

- PreprocessResult now inherits from ProcessingResult
- PreprocessStatistics now inherits from ProcessingStatistics
- get_statistics_summary() uses StatisticsFormatter

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Task 6: Update function_database.py

**Files:**
- Modify: `src/autosar_calltree/database/function_database.py`

- [ ] **Step 1: Update imports**

Add:
```python
from ..utils.statistics import StatisticsFormatter
```

- [ ] **Step 2: Update _get_pipeline_summary to use StatisticsFormatter**

Replace the `_get_pipeline_summary` method with:
```python
def _get_pipeline_summary(self) -> str:
    """Generate summary of two-stage pipeline results."""
    lines = []

    if self.preprocess_stats:
        lines.append(StatisticsFormatter.format_summary(
            "Preprocessing Stage",
            self.preprocess_stats,
            show_failures=False
        ))

    if self.parse_stats:
        # Use CParser's format for parsing with function counts
        lines.append("")
        lines.append("Parsing Stage:")
        lines.append(f"  Files parsed:    {self.parse_stats.total_files}")
        lines.append(f"  Successful:      {self.parse_stats.successful}")
        lines.append(f"  Failed:          {self.parse_stats.failed}")
        lines.append("")
        lines.append("Functions extracted:")
        lines.append(f"  AUTOSAR:       {self.parse_stats.autosar_functions}")
        lines.append(f"  Traditional:   {self.parse_stats.traditional_functions}")
        lines.append(f"  Total:         {self.parse_stats.total_functions}")
        lines.append("")
        lines.append(f"Correctness Ratio: {self.parse_stats.correctness_ratio:.1f}%")

        if self.parse_stats.failed > 0:
            lines.append("")
            lines.append("Failed files:")
            for parse_result in self.parse_stats.results:
                if not parse_result.success:
                    lines.append(
                        f"  - {parse_result.source_file.name}: {parse_result.error_message}"
                    )

    return "\n".join(lines)
```

- [ ] **Step 3: Run tests**

Run: `pytest`
Expected: PASS (all tests)

- [ ] **Step 4: Commit**

```bash
git add src/autosar_calltree/database/function_database.py
git commit -m "$(cat <<'EOF'
refactor: Update function_database to use StatisticsFormatter

Update _get_pipeline_summary() to use StatisticsFormatter
for preprocessing stage output.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Chunk 6: Migrate to TreeFormatter

### Task 7: Update mermaid_generator.py

**Files:**
- Modify: `src/autosar_calltree/generators/mermaid_generator.py`

- [ ] **Step 1: Add import for TreeFormatter**

Add at top of file:
```python
from ..utils.tree_formatter import TreeFormatter
```

- [ ] **Step 2: Update _generate_text_tree to use TreeFormatter**

Replace the `_generate_text_tree` method with:
```python
def _generate_text_tree(self, root: CallTreeNode) -> str:
    """
    Generate text-based tree representation.

    Args:
        root: Root node of call tree

    Returns:
        Markdown formatted text tree
    """
    lines = ["## Call Tree (Text)\n", "```"]
    lines.append(TreeFormatter.format_tree(root, show_file=True, show_line=True))
    lines.append("```\n")
    return "\n".join(lines)
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/unit/test_mermaid_generator.py -v`
Expected: PASS (all tests)

- [ ] **Step 4: Commit**

```bash
git add src/autosar_calltree/generators/mermaid_generator.py
git commit -m "$(cat <<'EOF'
refactor: Update mermaid_generator to use TreeFormatter

Replace _generate_text_tree() implementation with TreeFormatter.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Task 8: Update call_tree_builder.py

**Files:**
- Modify: `src/autosar_calltree/analyzers/call_tree_builder.py`

- [ ] **Step 1: Add import for TreeFormatter**

Add at top of file:
```python
from ..utils.tree_formatter import TreeFormatter
```

- [ ] **Step 2: Update print_tree_text to use TreeFormatter**

Replace the `print_tree_text` method with:
```python
def print_tree_text(self, root: CallTreeNode, show_file: bool = True) -> str:
    """
    Generate a text representation of the call tree.

    Args:
        root: Root node of call tree
        show_file: Whether to show file paths

    Returns:
        Text representation as string
    """
    return TreeFormatter.format_tree(root, show_file=show_file, show_line=show_file)
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/unit/test_call_tree_builder.py -v`
Expected: PASS (all tests)

- [ ] **Step 4: Commit**

```bash
git add src/autosar_calltree/analyzers/call_tree_builder.py
git commit -m "$(cat <<'EOF'
refactor: Update call_tree_builder to use TreeFormatter

Replace print_tree_text() implementation with TreeFormatter.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Chunk 7: Final Verification

### Task 9: Run Complete Test Suite

- [ ] **Step 1: Run all tests**

Run: `pytest --cov=autosar_calltree --cov-report=term`
Expected: All tests pass, coverage maintained

- [ ] **Step 2: Run type checking**

Run: `mypy src/`
Expected: No errors

- [ ] **Step 3: Run linting**

Run: `ruff check src/ tests/`
Expected: No errors

Run: `isort --check-only src/ tests/`
Expected: No errors

Run: `flake8 src/ tests/`
Expected: No errors

- [ ] **Step 4: Verify line counts**

Run:
```bash
wc -l src/autosar_calltree/parsers/c_parser.py
wc -l src/autosar_calltree/parsers/function_visitor.py
```
Expected: c_parser.py ~750 lines, function_visitor.py ~440 lines

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
refactor: Complete code simplification

Summary of changes:
- Added custom exception hierarchy (ParseError, PreprocessError, ConfigError, DatabaseError)
- Added statistics utilities (ProcessingResult, ProcessingStatistics, StatisticsFormatter)
- Added TreeFormatter for consolidated tree visualization
- Extracted FunctionVisitor from c_parser.py (~440 lines)
- Reduced c_parser.py from ~1190 to ~750 lines
- Eliminated duplicate tree formatting code
- Standardized statistics formatting across modules

All tests pass, no regressions, backward compatibility maintained.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Success Criteria Checklist

- [ ] All existing tests pass (`pytest`)
- [ ] No reduction in test coverage
- [ ] `mypy src/` passes with no new errors
- [ ] `ruff check src/ tests/` passes
- [ ] `flake8 src/ tests/` passes
- [ ] `isort --check-only src/ tests/` passes
- [ ] c_parser.py reduced from ~1190 to ~750 lines
- [ ] function_visitor.py created (~440 lines)
- [ ] No duplication of statistics formatting code
- [ ] No duplication of tree formatting code
- [ ] Exception hierarchy in place for future error handling standardization