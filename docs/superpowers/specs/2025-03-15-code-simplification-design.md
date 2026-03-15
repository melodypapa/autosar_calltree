# Design: Code Simplification Refactoring

**Date:** 2025-03-15
**Status:** Draft
**Author:** Claude

## Overview

This document describes a systematic refactoring of the AUTOSAR Call Tree Analyzer codebase to improve code clarity, consistency, and maintainability. The refactoring follows an incremental approach where each change is isolated, testable, and can be rolled back independently.

## Goals

1. Reduce code duplication across modules
2. Standardize error handling patterns
3. Extract large classes into focused modules
4. Create shared utilities for common operations
5. Maintain 100% backward compatibility

## Non-Goals

- Adding new features
- Changing public APIs
- Performance optimization
- Major architectural changes

## New File Structure

```
src/autosar_calltree/
├── exceptions.py                    # Custom exception hierarchy
└── utils/
    ├── __init__.py                  # Exports: StatisticsFormatter, TreeFormatter
    ├── statistics.py                # StatisticsFormatter, ProcessingStatistics, ProcessingResult
    └── tree_formatter.py            # TreeFormatter
```

**`utils/__init__.py` contents:**

```python
"""Utility modules for autosar-calltree."""

from .statistics import ProcessingResult, ProcessingStatistics, StatisticsFormatter
from .tree_formatter import TreeFormatter

__all__ = [
    "ProcessingResult",
    "ProcessingStatistics",
    "StatisticsFormatter",
    "TreeFormatter",
]
```

## Component Designs

### 1. Exception Hierarchy

**File:** `src/autosar_calltree/exceptions.py`

Create a hierarchy of custom exceptions for better error tracing and handling:

```python
class AutosarCalltreeError(Exception):
    """Base exception for all autosar-calltree errors."""
    pass

class ParseError(AutosarCalltreeError):
    """Raised when parsing fails."""
    def __init__(self, message: str, file_path: str = None, line_number: int = None):
        self.file_path = file_path
        self.line_number = line_number
        super().__init__(message)

class PreprocessError(AutosarCalltreeError):
    """Raised when preprocessing fails."""
    def __init__(self, message: str, file_path: str = None, error_type: str = None):
        self.file_path = file_path
        self.error_type = error_type  # 'cpp_not_found', 'cpp_error', 'timeout'
        super().__init__(message)

class ConfigError(AutosarCalltreeError):
    """Raised when configuration is invalid."""
    pass

class DatabaseError(AutosarCalltreeError):
    """Raised when database operations fail."""
    pass
```

**Usage:**
- `ParseError` replaces generic exceptions in parsers with file/line context
- `PreprocessError` replaces error strings in preprocessing
- `ConfigError` for YAML validation failures
- `DatabaseError` for cache/load failures

### 2. Statistics Utilities

**File:** `src/autosar_calltree/utils/statistics.py`

Create base classes for processing statistics to reduce duplication:

```python
@dataclass
class ProcessingResult:
    """Base result for any processing operation.

    Subclasses may add additional fields for their specific needs
    (e.g., ParseResult adds functions, autosar_functions, traditional_functions).
    """
    source_file: Path
    success: bool
    error_message: Optional[str] = None

@dataclass
class ProcessingStatistics:
    """Base statistics for batch processing operations.

    Subclasses may add additional fields for their specific needs
    (e.g., ParseStatistics adds autosar_functions, traditional_functions, total_functions).
    """
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0  # Used by PreprocessStatistics
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
        """Generate a human-readable summary.

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
                    lines.append(f"    - {result.source_file.name}: {result.error_message}")

        return "\n".join(lines)

    @staticmethod
    def format_parsing_summary(stats: "ParseStatistics") -> str:
        """Format parsing-specific statistics with function counts."""
        extra_lines = [
            "",
            "Functions extracted:",
            f"  AUTOSAR:       {stats.autosar_functions}",
            f"  Traditional:   {stats.traditional_functions}",
            f"  Total:         {stats.total_functions}",
            "",
            f"Correctness Ratio: {stats.correctness_ratio:.1f}%",
        ]
        return StatisticsFormatter.format_summary(
            "Parsing Stage", stats, extra_lines=extra_lines
        )
```

**Inheritance Structure:**

```
ProcessingResult (base)
├── ParseResult (adds: preprocessed_file, functions, autosar_functions, traditional_functions)
└── PreprocessResult (adds: output_file, error_type)

ProcessingStatistics (base)
├── ParseStatistics (adds: autosar_functions, traditional_functions, total_functions, correctness_ratio)
└── PreprocessStatistics (uses: skipped)
```

**Migration:**
- `ParseStatistics` and `PreprocessStatistics` inherit from `ProcessingStatistics`
- `ParseResult` and `PreprocessResult` inherit from `ProcessingResult`
- `CParser.get_statistics_summary()` replaced by `StatisticsFormatter.format_parsing_summary()`
- `CPPPreprocessor.get_statistics_summary()` replaced by `StatisticsFormatter.format_summary()`
- `FunctionDatabase._get_pipeline_summary()` uses `StatisticsFormatter` methods

### 3. Tree Formatter

**File:** `src/autosar_calltree/utils/tree_formatter.py`

Consolidate duplicated text tree generation:

```python
class TreeFormatter:
    """Format call trees as text-based tree diagrams."""

    @staticmethod
    def format_tree(
        root: "CallTreeNode",
        show_file: bool = True,
        show_line: bool = True
    ) -> str:
        """Generate text-based tree representation."""
        # Implementation with tree traversal logic
```

**Migration:**
- `MermaidGenerator._generate_text_tree()` calls `TreeFormatter.format_tree()`
- `CallTreeBuilder.print_tree_text()` calls `TreeFormatter.format_tree()`
- Both methods become thin wrappers

### 4. FunctionVisitor Extraction

**File:** `src/autosar_calltree/parsers/function_visitor.py`

Extract `FunctionVisitor` class from `c_parser.py` (~375 lines for the class itself, lines 60-434).

**Constants Handling:**

The constants `C_KEYWORDS`, `AUTOSAR_TYPES`, and `AUTOSAR_MACROS` are currently class attributes on `CParser` and accessed by the nested `CallVisitor` class via `CParser.C_KEYWORDS` etc. After extraction, these constants will be defined as class attributes on `FunctionVisitor`:

```python
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
        self.file_path = file_path
        self.content = content
        self.functions: List[FunctionInfo] = []

    def visit_FuncDef(self, node: c_ast.FuncDef) -> None:
        # Extract function name, return type, parameters, calls
        # Create FunctionInfo objects
```

**Nested CallVisitor Handling:**

The `CallVisitor` class is currently nested inside `_extract_function_calls()` and references `CParser.C_KEYWORDS`, etc. After extraction, `CallVisitor` becomes a nested class inside `FunctionVisitor` and accesses the constants via `FunctionVisitor.C_KEYWORDS`:

```python
def _extract_function_calls(self, node: c_ast.FuncDef) -> List[FunctionCall]:
    """Extract function calls from function body."""

    class CallVisitor(c_ast.NodeVisitor):
        def __init__(self, parent: FunctionVisitor):
            self.parent = parent
            self.calls: List[FunctionCall] = []
            self.seen: Set[str] = set()

        def visit_FuncCall(self, call_node: c_ast.FuncCall) -> None:
            # ... extract function name ...
            # Skip C keywords - now using FunctionVisitor.C_KEYWORDS
            if func_name in FunctionVisitor.C_KEYWORDS:
                return
            # ... rest of implementation
```

**Backward Compatibility:**

`CParser` will re-export the constants for any external callers:

```python
# In c_parser.py after extraction
from .function_visitor import FunctionVisitor

class CParser:
    # Re-export constants for backward compatibility
    C_KEYWORDS = FunctionVisitor.C_KEYWORDS
    AUTOSAR_TYPES = FunctionVisitor.AUTOSAR_TYPES
    AUTOSAR_MACROS = FunctionVisitor.AUTOSAR_MACROS
```

**Result:**
- `c_parser.py` reduced from ~1190 lines to ~750 lines
- `function_visitor.py` ~440 lines of focused AST traversal logic
- Constants are defined once in `FunctionVisitor`, re-exported from `CParser` for compatibility

## Migration Plan

| Step | Task | Test File | Verification |
|------|------|-----------|--------------|
| 1 | Create `exceptions.py` with exception hierarchy | `tests/unit/test_exceptions.py` | New tests pass |
| 2 | Create `utils/__init__.py` and `utils/statistics.py` | `tests/unit/utils/test_statistics.py` | New tests pass |
| 3 | Create `utils/tree_formatter.py` | `tests/unit/utils/test_tree_formatter.py` | New tests pass |
| 4a | Create `parsers/function_visitor.py` with FunctionVisitor class | Existing tests | Tests pass |
| 4b | Update `c_parser.py` imports to use FunctionVisitor | Existing tests | Tests pass |
| 4c | Add re-exports in `parsers/__init__.py` if needed | Existing tests | Tests pass |
| 5 | Update `cpp_preprocessor.py` to inherit from ProcessingStatistics | Existing tests | Tests pass |
| 6 | Update `function_database.py` to use StatisticsFormatter | Existing tests | Tests pass |
| 7 | Update `mermaid_generator.py` to use TreeFormatter | Existing tests | Tests pass |
| 8 | Update `call_tree_builder.py` to use TreeFormatter | Existing tests | Tests pass |
| 9 | Update parsers to raise new exceptions | Update tests | Tests pass |
| 10 | Update CLI to catch new exceptions | `tests/integration/test_cli.py` | Integration tests pass |

**Test File Structure:**

```
tests/
├── unit/
│   ├── test_exceptions.py          # NEW: Tests for exception hierarchy
│   ├── test_autosar_parser.py      # Existing
│   ├── test_c_parser.py            # Existing (update for new exceptions)
│   ├── test_call_tree_builder.py   # Existing
│   ├── test_function_database.py   # Existing
│   ├── test_mermaid_generator.py   # Existing
│   ├── test_models.py              # Existing
│   ├── test_module_config.py       # Existing
│   └── utils/                      # NEW DIRECTORY
│       ├── __init__.py
│       ├── test_statistics.py      # NEW: Tests for StatisticsFormatter
│       └── test_tree_formatter.py  # NEW: Tests for TreeFormatter
└── integration/
    └── test_cli.py                 # Existing (update for new exceptions)
```

**Import Path Examples:**

After migration, imports will work as follows:

```python
# Before
from autosar_calltree.parsers.c_parser import CParser, FunctionVisitor  # FunctionVisitor was internal

# After
from autosar_calltree.parsers.c_parser import CParser
from autosar_calltree.parsers.function_visitor import FunctionVisitor

# Utilities
from autosar_calltree.utils.statistics import StatisticsFormatter, ProcessingStatistics
from autosar_calltree.utils.tree_formatter import TreeFormatter

# Exceptions
from autosar_calltree.exceptions import ParseError, PreprocessError, ConfigError, DatabaseError
```

## Testing Strategy

- Run full test suite after each step: `pytest`
- Run type checking after each step: `mypy src/`
- Run linting after each step: `ruff check src/ tests/`
- All existing tests must pass - no behavior changes

## Rollback Safety

- Each step is atomic and can be reverted independently
- No step breaks the public API
- Import paths remain stable (re-exports where needed)

## Files Modified

| File | Changes |
|------|---------|
| `parsers/c_parser.py` | Extract FunctionVisitor, use new exceptions |
| `parsers/autosar_parser.py` | Use new exceptions |
| `database/function_database.py` | Use StatisticsFormatter, new exceptions |
| `preprocessing/cpp_preprocessor.py` | Use StatisticsFormatter, new exceptions |
| `generators/mermaid_generator.py` | Use TreeFormatter |
| `analyzers/call_tree_builder.py` | Use TreeFormatter |
| `cli/main.py` | Use new exceptions |

## Success Criteria

1. All existing tests pass
2. No reduction in test coverage
3. `mypy src/` passes with no new errors
4. `ruff check src/ tests/` passes
5. Each module is smaller and more focused
6. No duplication of statistics formatting code
7. No duplication of tree formatting code
8. Consistent error handling across modules