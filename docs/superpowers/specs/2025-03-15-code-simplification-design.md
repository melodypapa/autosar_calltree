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
    ├── __init__.py
    ├── statistics.py                # StatisticsFormatter class
    └── tree_formatter.py            # TreeFormatter class
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
    """Base result for any processing operation."""
    source_file: str
    success: bool
    error_message: Optional[str] = None

@dataclass
class ProcessingStatistics:
    """Base statistics for batch processing operations."""
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    results: List[ProcessingResult] = None

    @property
    def success_rate(self) -> float:
        processed = self.successful + self.failed
        return (self.successful / processed * 100.0) if processed > 0 else 0.0

class StatisticsFormatter:
    """Format processing statistics for display."""

    @staticmethod
    def format_summary(
        stage_name: str,
        stats: ProcessingStatistics,
        show_failures: bool = True
    ) -> str:
        """Generate a human-readable summary."""
        # Implementation details...
```

**Migration:**
- `ParseStatistics` and `PreprocessStatistics` inherit from `ProcessingStatistics`
- `ParseResult` and `PreprocessResult` inherit from `ProcessingResult`
- `get_statistics_summary()` methods replaced by `StatisticsFormatter.format_summary()`

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

Extract `FunctionVisitor` class from `c_parser.py` (~450 lines):

```python
class FunctionVisitor(c_ast.NodeVisitor):
    """AST visitor to extract function definitions and calls."""

    C_KEYWORDS = { ... }
    AUTOSAR_TYPES = { ... }
    AUTOSAR_MACROS = { ... }

    def __init__(self, file_path: Path, content: str):
        self.file_path = file_path
        self.content = content
        self.functions: List[FunctionInfo] = []

    def visit_FuncDef(self, node: c_ast.FuncDef) -> None:
        # Extract function name, return type, parameters, calls
        # Create FunctionInfo objects
```

**Result:**
- `c_parser.py` reduced from ~1190 lines to ~700 lines
- `function_visitor.py` ~450 lines of focused AST traversal logic
- Constants (`C_KEYWORDS`, `AUTOSAR_TYPES`, `AUTOSAR_MACROS`) move with the class

## Migration Plan

| Step | Task | Tests |
|------|------|-------|
| 1 | Create `exceptions.py` with exception hierarchy | Unit tests for each exception type |
| 2 | Create `utils/__init__.py` and `utils/statistics.py` | Unit tests for StatisticsFormatter |
| 3 | Create `utils/tree_formatter.py` | Unit tests for TreeFormatter |
| 4 | Create `parsers/function_visitor.py`, move class from c_parser | Existing tests should pass |
| 5 | Update `c_parser.py` to import FunctionVisitor | Existing tests should pass |
| 6 | Update `cpp_preprocessor.py` to use ProcessingStatistics | Existing tests should pass |
| 7 | Update `function_database.py` to use StatisticsFormatter | Existing tests should pass |
| 8 | Update `mermaid_generator.py` to use TreeFormatter | Existing tests should pass |
| 9 | Update `call_tree_builder.py` to use TreeFormatter | Existing tests should pass |
| 10 | Update parsers to raise new exceptions | Update tests for new exception types |
| 11 | Update CLI to catch new exceptions | Integration tests |

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