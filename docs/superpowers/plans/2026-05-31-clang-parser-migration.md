# Clang Parser Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate from pycparser to clang for 100% accurate function call extraction with precise control flow attribution.

**Architecture:** Replace pycparser-based parsing with libclang AST traversal. Single unified parser handles both AUTOSAR and traditional C code with built-in preprocessing and comprehensive call extraction.

**Tech Stack:** Python 3.8+, libclang >= 16.0.0, clang AST API

---

## File Structure

**Files to Create:**
- `src/autosar_calltree/parsers/clang_parser.py` - Main clang parser entry point
- `src/autosar_calltree/parsers/clang_function_visitor.py` - AST visitor for extraction
- `tests/unit/parsers/test_clang_parser.py` - Unit tests for clang parser
- `tests/fixtures/standard_c_patterns/` - Test fixtures for standard C
- `tests/fixtures/control_flow_attribution/` - Test fixtures for control flow
- `tests/fixtures/complex_scenarios/` - Test fixtures for complex cases

**Files to Remove:**
- `src/autosar_calltree/parsers/c_parser.py` - Old pycparser implementation
- `src/autosar_calltree/parsers/function_visitor.py` - Old pycparser visitor
- `src/autosar_calltree/parsers/autosar_parser.py` - Old regex parser
- `src/autosar_calltree/preprocessing/` - Entire directory (no longer needed)

**Files to Modify:**
- `requirements.txt` - Replace pycparser with libclang
- `requirements-dev.txt` - Replace pycparser with libclang
- `pyproject.toml` - Update dependencies
- `src/autosar_calltree/parsers/__init__.py` - Export ClangParser
- `src/autosar_calltree/database/function_database.py` - Use ClangParser
- `src/autosar_calltree/config/preprocessor_config.py` - Simplify for clang
- All test files with old parser imports

---

## Phase 1: Core Clang Parser

### Task 1: Update Dependencies

**Files:**
- Modify: `requirements.txt`
- Modify: `requirements-dev.txt`
- Modify: `pyproject.toml`

- [ ] **Step 1: Update requirements.txt**

```diff
- pycparser>=2.21
+ libclang>=16.0.0
```

- [ ] **Step 2: Update requirements-dev.txt**

```diff
- pycparser>=2.21
+ libclang>=16.0.0
```

- [ ] **Step 3: Update pyproject.toml**

```toml
[project]
dependencies = [
    "libclang>=16.0.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "flake8>=5.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]
```

- [ ] **Step 4: Install new dependencies**

Run: `pip install -r requirements-dev.txt`
Expected: Successfully installed libclang

- [ ] **Step 5: Commit dependency changes**

```bash
git add requirements.txt requirements-dev.txt pyproject.toml
git commit -m "chore: replace pycparser with libclang dependency"
```

---

### Task 2: Create ClangParser Core

**Files:**
- Create: `src/autosar_calltree/parsers/clang_parser.py`
- Test: `tests/unit/parsers/test_clang_parser.py`

- [ ] **Step 1: Write failing test for ClangParser initialization**

Create `tests/unit/parsers/test_clang_parser.py`:

```python
"""Tests for parsers/clang_parser.py"""

from pathlib import Path
from autosar_calltree.parsers.clang_parser import ClangParser


def test_clang_parser_initialization():
    """Test that ClangParser initializes correctly."""
    parser = ClangParser()
    assert parser is not None
    assert parser.index is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_initialization -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'autosar_calltree.parsers.clang_parser'"

- [ ] **Step 3: Create minimal ClangParser class**

Create `src/autosar_calltree/parsers/clang_parser.py`:

```python
"""
C function parser using clang (libclang).

This module uses clang for accurate parsing of C code with built-in
preprocessing and comprehensive AST analysis.
"""

import clang.cindex
from clang.cindex import Index, TranslationUnit
from pathlib import Path
from typing import List, Optional


class ClangParser:
    """C parser using libclang for maximum accuracy."""
    
    def __init__(
        self,
        include_dirs: Optional[List[str]] = None,
        compiler_flags: Optional[List[str]] = None
    ):
        """
        Initialize the clang parser.
        
        Args:
            include_dirs: List of include directories for header resolution
            compiler_flags: Additional compiler flags (e.g., -std=c99)
        """
        self.index = Index.create()
        self.include_dirs = include_dirs or []
        self.compiler_flags = compiler_flags or []
    
    def parse_file(self, file_path: Path) -> List:
        """
        Parse a C source file and extract all function definitions.
        
        Args:
            file_path: Path to the C source file
            
        Returns:
            List of FunctionInfo objects (placeholder for now)
        """
        # Placeholder - will implement in next task
        return []
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_initialization -v`
Expected: PASS

- [ ] **Step 5: Commit ClangParser initialization**

```bash
git add src/autosar_calltree/parsers/clang_parser.py tests/unit/parsers/test_clang_parser.py
git commit -m "feat: add ClangParser initialization"
```

---

### Task 3: Create ClangFunctionVisitor Core

**Files:**
- Create: `src/autosar_calltree/parsers/clang_function_visitor.py`
- Modify: `tests/unit/parsers/test_clang_parser.py`

- [ ] **Step 1: Write failing test for function extraction**

Add to `tests/unit/parsers/test_clang_parser.py`:

```python
import tempfile
from autosar_calltree.database.models import FunctionInfo


def test_clang_parser_extract_simple_function():
    """Test that ClangParser extracts a simple function."""
    parser = ClangParser()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write("""
void simple_function(void) {
}
""")
        fixture_path = Path(f.name)
    
    functions = parser.parse_file(fixture_path)
    
    assert len(functions) == 1
    assert isinstance(functions[0], FunctionInfo)
    assert functions[0].name == 'simple_function'
    assert functions[0].return_type == 'void'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_extract_simple_function -v`
Expected: FAIL with "AssertionError: assert 0 == 1" (empty list returned)

- [ ] **Step 3: Create ClangFunctionVisitor class**

Create `src/autosar_calltree/parsers/clang_function_visitor.py`:

```python
"""
AST visitor for extracting function definitions from clang AST.

This module provides the ClangFunctionVisitor class that walks clang
AST nodes to extract function definitions and calls.
"""

from dataclasses import dataclass
from typing import List, Optional, Set
from pathlib import Path

import clang.cindex
from clang.cindex import CursorKind, Cursor, TranslationUnit

from ..database.models import FunctionInfo, FunctionCall, Parameter, FunctionType


@dataclass
class ControlFlowContext:
    """Tracks current control flow nesting."""
    context_type: str  # 'if', 'else', 'for', 'while', 'do', 'switch', 'case'
    condition: Optional[str] = None
    depth: int = 0


class ClangFunctionVisitor:
    """
    Visit clang AST to extract functions and all their calls.
    """
    
    C_KEYWORDS: Set[str] = {
        'if', 'else', 'while', 'for', 'do', 'switch', 'case', 'default',
        'return', 'break', 'continue', 'goto', 'sizeof', 'typeof',
        '__typeof__', '__builtin_offsetof'
    }
    
    def __init__(self, file_path: Path, translation_unit: TranslationUnit):
        """
        Initialize the visitor.
        
        Args:
            file_path: Path to the source file
            translation_unit: Clang translation unit
        """
        self.file_path = file_path
        self.tu = translation_unit
        self.functions: List[FunctionInfo] = []
        self.current_function: Optional[FunctionInfo] = None
        self.control_flow_stack: List[ControlFlowContext] = []
    
    def extract_functions(self) -> List[FunctionInfo]:
        """Extract all functions from the translation unit."""
        self._visit_cursor(self.tu.cursor)
        return self.functions
    
    def _visit_cursor(self, cursor: Cursor):
        """Recursively visit AST nodes."""
        if cursor.kind == CursorKind.FUNCTION_DECL:
            self._handle_function_decl(cursor)
        
        for child in cursor.get_children():
            self._visit_cursor(child)
    
    def _handle_function_decl(self, cursor: Cursor):
        """Handle function declaration/definition."""
        if not cursor.is_definition():
            return
        
        func_info = FunctionInfo(
            name=cursor.spelling,
            return_type=cursor.result_type.spelling,
            file_path=self.file_path,
            line_number=cursor.location.line,
            is_static=cursor.storage_class == clang.cindex.StorageClass.STATIC,
            function_type=FunctionType.TRADITIONAL_C,
            parameters=[],
            calls=[]
        )
        
        self.functions.append(func_info)
```

- [ ] **Step 4: Update ClangParser to use visitor**

Update `src/autosar_calltree/parsers/clang_parser.py`:

```python
from .clang_function_visitor import ClangFunctionVisitor
from ..database.models import FunctionInfo


class ClangParser:
    # ... existing code ...
    
    def parse_file(self, file_path: Path) -> List[FunctionInfo]:
        """
        Parse a C source file and extract all function definitions.
        
        Args:
            file_path: Path to the C source file
            
        Returns:
            List of FunctionInfo objects
        """
        args = self._get_clang_args()
        
        tu = self.index.parse(
            str(file_path),
            args=args,
            options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
        )
        
        visitor = ClangFunctionVisitor(file_path, tu)
        return visitor.extract_functions()
    
    def _get_clang_args(self) -> List[str]:
        """Build clang compiler arguments."""
        args = ['-fsyntax-only']
        
        for inc_dir in self.include_dirs:
            args.extend(['-I', inc_dir])
        
        args.extend(self.compiler_flags)
        return args
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_extract_simple_function -v`
Expected: PASS

- [ ] **Step 6: Commit function extraction**

```bash
git add src/autosar_calltree/parsers/clang_function_visitor.py
git commit -m "feat: add ClangFunctionVisitor for function extraction"
```

---

### Task 4: Extract Function Parameters

**Files:**
- Modify: `src/autosar_calltree/parsers/clang_function_visitor.py`
- Modify: `tests/unit/parsers/test_clang_parser.py`

- [ ] **Step 1: Write failing test for parameter extraction**

Add to `tests/unit/parsers/test_clang_parser.py`:

```python
def test_clang_parser_extract_parameters():
    """Test that ClangParser extracts function parameters."""
    parser = ClangParser()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write("""
int add(int a, int b) {
    return a + b;
}
""")
        fixture_path = Path(f.name)
    
    functions = parser.parse_file(fixture_path)
    
    assert len(functions) == 1
    assert functions[0].name == 'add'
    assert len(functions[0].parameters) == 2
    assert functions[0].parameters[0].name == 'a'
    assert functions[0].parameters[0].param_type == 'int'
    assert functions[0].parameters[1].name == 'b'
    assert functions[0].parameters[1].param_type == 'int'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_extract_parameters -v`
Expected: FAIL with "AssertionError: assert 0 == 2" (empty parameters)

- [ ] **Step 3: Implement parameter extraction**

Add to `src/autosar_calltree/parsers/clang_function_visitor.py`:

```python
def _handle_function_decl(self, cursor: Cursor):
    """Handle function declaration/definition."""
    if not cursor.is_definition():
        return
    
    parameters = self._extract_parameters(cursor)
    
    func_info = FunctionInfo(
        name=cursor.spelling,
        return_type=cursor.result_type.spelling,
        file_path=self.file_path,
        line_number=cursor.location.line,
        is_static=cursor.storage_class == clang.cindex.StorageClass.STATIC,
        function_type=FunctionType.TRADITIONAL_C,
        parameters=parameters,
        calls=[]
    )
    
    self.functions.append(func_info)

def _extract_parameters(self, cursor: Cursor) -> List[Parameter]:
    """Extract function parameters."""
    params = []
    for arg in cursor.get_arguments():
        param_type = arg.type.spelling
        param = Parameter(
            name=arg.spelling,
            param_type=param_type,
            is_pointer='*' in param_type,
            is_const='const' in param_type
        )
        params.append(param)
    return params
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_extract_parameters -v`
Expected: PASS

- [ ] **Step 5: Commit parameter extraction**

```bash
git add src/autosar_calltree/parsers/clang_function_visitor.py tests/unit/parsers/test_clang_parser.py
git commit -m "feat: add parameter extraction to ClangFunctionVisitor"
```

---

### Task 5: Extract Basic Function Calls

**Files:**
- Modify: `src/autosar_calltree/parsers/clang_function_visitor.py`
- Modify: `tests/unit/parsers/test_clang_parser.py`

- [ ] **Step 1: Write failing test for call extraction**

Add to `tests/unit/parsers/test_clang_parser.py`:

```python
def test_clang_parser_extract_function_calls():
    """Test that ClangParser extracts function calls."""
    parser = ClangParser()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write("""
void helper1(void) {}
void helper2(void) {}

void caller(void) {
    helper1();
    helper2();
}
""")
        fixture_path = Path(f.name)
    
    functions = parser.parse_file(fixture_path)
    
    caller_func = [f for f in functions if f.name == 'caller'][0]
    assert len(caller_func.calls) == 2
    call_names = [c.name for c in caller_func.calls]
    assert 'helper1' in call_names
    assert 'helper2' in call_names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_extract_function_calls -v`
Expected: FAIL with "AssertionError: assert 0 == 2" (empty calls)

- [ ] **Step 3: Implement basic call extraction**

Add to `src/autosar_calltree/parsers/clang_function_visitor.py`:

```python
def _handle_function_decl(self, cursor: Cursor):
    """Handle function declaration/definition."""
    if not cursor.is_definition():
        return
    
    parameters = self._extract_parameters(cursor)
    
    func_info = FunctionInfo(
        name=cursor.spelling,
        return_type=cursor.result_type.spelling,
        file_path=self.file_path,
        line_number=cursor.location.line,
        is_static=cursor.storage_class == clang.cindex.StorageClass.STATIC,
        function_type=FunctionType.TRADITIONAL_C,
        parameters=parameters,
        calls=[]
    )
    
    self.current_function = func_info
    self._extract_calls_from_body(cursor)
    self.current_function = None
    
    self.functions.append(func_info)

def _extract_calls_from_body(self, func_cursor: Cursor):
    """Extract all function calls from function body."""
    for child in func_cursor.get_children():
        if child.kind == CursorKind.COMPOUND_STMT:
            self._extract_calls_from_node(child)

def _extract_calls_from_node(self, cursor: Cursor):
    """Recursively extract all function calls from any AST node."""
    if cursor.kind == CursorKind.CALL_EXPR:
        self._handle_call_expr(cursor)
    
    for child in cursor.get_children():
        self._extract_calls_from_node(child)

def _handle_call_expr(self, cursor: Cursor):
    """Handle a function call expression."""
    callee_name = cursor.spelling
    
    if callee_name in self.C_KEYWORDS or callee_name.startswith('__builtin'):
        return
    
    call = FunctionCall(
        name=callee_name,
        line_number=cursor.location.line
    )
    
    if self.current_function:
        self.current_function.calls.append(call)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_extract_function_calls -v`
Expected: PASS

- [ ] **Step 5: Commit call extraction**

```bash
git add src/autosar_calltree/parsers/clang_function_visitor.py tests/unit/parsers/test_clang_parser.py
git commit -m "feat: add basic function call extraction"
```

---

### Task 6: Update Parser Exports

**Files:**
- Modify: `src/autosar_calltree/parsers/__init__.py`

- [ ] **Step 1: Update parsers __init__.py**

Update `src/autosar_calltree/parsers/__init__.py`:

```python
"""Parsers package for AUTOSAR Call Tree Analyzer."""

from .clang_parser import ClangParser

__all__ = ["ClangParser"]
```

- [ ] **Step 2: Verify imports work**

Run: `python -c "from autosar_calltree.parsers import ClangParser; print('Import successful')"`
Expected: "Import successful"

- [ ] **Step 3: Commit parser exports**

```bash
git add src/autosar_calltree/parsers/__init__.py
git commit -m "feat: export ClangParser from parsers package"
```

---

### Task 7: Update FunctionDatabase to Use ClangParser

**Files:**
- Modify: `src/autosar_calltree/database/function_database.py`

- [ ] **Step 1: Update FunctionDatabase imports**

Update `src/autosar_calltree/database/function_database.py` imports:

```python
from ..parsers import ClangParser
```

- [ ] **Step 2: Update FunctionDatabase initialization**

Find the `__init__` method and update parser initialization:

```python
def __init__(self, config: Optional[ModuleConfig] = None):
    self.config = config or ModuleConfig()
    self.functions: Dict[str, List[FunctionInfo]] = {}
    self.file_functions: Dict[Path, List[FunctionInfo]] = {}
    
    self.parser = ClangParser(
        include_dirs=self.config.include_dirs if hasattr(self.config, 'include_dirs') else [],
        compiler_flags=self.config.compiler_flags if hasattr(self.config, 'compiler_flags') else []
    )
```

- [ ] **Step 3: Run existing database tests**

Run: `pytest tests/unit/database/test_function_database.py -v`
Expected: Most tests should pass (some may fail due to preprocessing changes)

- [ ] **Step 4: Commit database changes**

```bash
git add src/autosar_calltree/database/function_database.py
git commit -m "refactor: update FunctionDatabase to use ClangParser"
```

---

### Task 8: Simplify PreprocessorConfig

**Files:**
- Modify: `src/autosar_calltree/config/preprocessor_config.py`

- [ ] **Step 1: Update PreprocessorConfig for clang**

Update `src/autosar_calltree/config/preprocessor_config.py`:

```python
"""
Configuration for clang-based preprocessing.

Note: clang handles preprocessing internally, so this config
mainly controls include paths and compiler flags.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class PreprocessorConfig:
    """
    Configuration for clang-based preprocessing.
    
    clang handles preprocessing internally, so this config
    mainly controls include paths and compiler flags.
    """
    include_dirs: List[str] = field(default_factory=list)
    compiler_flags: List[str] = field(default_factory=list)
    
    enabled: bool = True  # Always enabled with clang
    preprocessor: str = "clang"  # Always clang
```

- [ ] **Step 2: Run config tests**

Run: `pytest tests/unit/config/test_preprocessor_config.py -v`
Expected: Most tests should pass (some may need updates)

- [ ] **Step 3: Commit config changes**

```bash
git add src/autosar_calltree/config/preprocessor_config.py
git commit -m "refactor: simplify PreprocessorConfig for clang"
```

---

## Phase 2: Enhanced Call Extraction

### Task 9: Extract Nested Calls

**Files:**
- Create: `tests/fixtures/standard_c_patterns/test_nested_calls.c`
- Modify: `tests/unit/parsers/test_clang_parser.py`

- [ ] **Step 1: Create test fixture**

Create `tests/fixtures/standard_c_patterns/test_nested_calls.c`:

```c
/*
 * Test nested function calls
 */

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

int calculate(int x, int y) {
    return x + y;
}

void nested_calls(void) {
    int result = calculate(add(1, 2), multiply(3, 4));
}
```

- [ ] **Step 2: Write test for nested calls**

Add to `tests/unit/parsers/test_clang_parser.py`:

```python
def test_clang_parser_nested_calls():
    """Test that nested function calls are all extracted."""
    parser = ClangParser()
    fixture_path = Path('tests/fixtures/standard_c_patterns/test_nested_calls.c')
    
    functions = parser.parse_file(fixture_path)
    
    nested_func = [f for f in functions if f.name == 'nested_calls'][0]
    call_names = [c.name for c in nested_func.calls]
    
    assert 'calculate' in call_names
    assert 'add' in call_names
    assert 'multiply' in call_names
```

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_nested_calls -v`
Expected: PASS (clang's recursive AST traversal should already handle this)

- [ ] **Step 4: Commit nested calls test**

```bash
git add tests/fixtures/standard_c_patterns/test_nested_calls.c tests/unit/parsers/test_clang_parser.py
git commit -m "test: add test for nested function calls"
```

---

### Task 10: Extract Calls in Initializers

**Files:**
- Create: `tests/fixtures/standard_c_patterns/test_initializer_calls.c`
- Modify: `tests/unit/parsers/test_clang_parser.py`

- [ ] **Step 1: Create test fixture**

Create `tests/fixtures/standard_c_patterns/test_initializer_calls.c`:

```c
/*
 * Test calls in variable initializers
 */

int get_default(void) {
    return 42;
}

char* allocate_buffer(int size) {
    return 0;
}

int get_a(void) { return 1; }
int get_b(void) { return 2; }
int get_c(void) { return 3; }

void initializer_calls(void) {
    int value = get_default();
    char* buffer = allocate_buffer(1024);
    int arr[] = {get_a(), get_b(), get_c()};
}
```

- [ ] **Step 2: Write test for initializer calls**

Add to `tests/unit/parsers/test_clang_parser.py`:

```python
def test_clang_parser_initializer_calls():
    """Test that calls in variable initializers are extracted."""
    parser = ClangParser()
    fixture_path = Path('tests/fixtures/standard_c_patterns/test_initializer_calls.c')
    
    functions = parser.parse_file(fixture_path)
    
    init_func = [f for f in functions if f.name == 'initializer_calls'][0]
    call_names = [c.name for c in init_func.calls]
    
    assert 'get_default' in call_names
    assert 'allocate_buffer' in call_names
    assert 'get_a' in call_names
    assert 'get_b' in call_names
    assert 'get_c' in call_names
```

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_initializer_calls -v`
Expected: PASS

- [ ] **Step 4: Commit initializer calls test**

```bash
git add tests/fixtures/standard_c_patterns/test_initializer_calls.c tests/unit/parsers/test_clang_parser.py
git commit -m "test: add test for calls in initializers"
```

---

### Task 11: Implement Control Flow Tracking

**Files:**
- Modify: `src/autosar_calltree/parsers/clang_function_visitor.py`
- Create: `tests/fixtures/control_flow_attribution/test_if_statements.c`
- Modify: `tests/unit/parsers/test_clang_parser.py`

- [ ] **Step 1: Create test fixture for if statements**

Create `tests/fixtures/control_flow_attribution/test_if_statements.c`:

```c
/*
 * Test control flow attribution for if statements
 */

void outer_if_call(void) {}
void inner_if_call(void) {}
void else_call(void) {}

void test_if_statements(int mode) {
    if (mode == 1) {
        outer_if_call();
        
        if (mode > 0) {
            inner_if_call();
        }
    } else {
        else_call();
    }
}
```

- [ ] **Step 2: Write test for if statement attribution**

Add to `tests/unit/parsers/test_clang_parser.py`:

```python
def test_clang_parser_if_statement_attribution():
    """Test that calls are attributed to if statements."""
    parser = ClangParser()
    fixture_path = Path('tests/fixtures/control_flow_attribution/test_if_statements.c')
    
    functions = parser.parse_file(fixture_path)
    
    test_func = [f for f in functions if f.name == 'test_if_statements'][0]
    
    outer_call = [c for c in test_func.calls if c.name == 'outer_if_call'][0]
    assert outer_call.is_conditional == True
    assert 'mode == 1' in outer_call.condition
    
    inner_call = [c for c in test_func.calls if c.name == 'inner_if_call'][0]
    assert inner_call.is_conditional == True
    
    else_call = [c for c in test_func.calls if c.name == 'else_call'][0]
    assert else_call.is_conditional == True
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_if_statement_attribution -v`
Expected: FAIL with "AssertionError: assert False == True" (is_conditional not set)

- [ ] **Step 4: Implement control flow tracking**

Update `src/autosar_calltree/parsers/clang_function_visitor.py`:

```python
def _extract_calls_from_body(self, func_cursor: Cursor):
    """Extract all function calls from function body."""
    for child in func_cursor.get_children():
        if child.kind == CursorKind.COMPOUND_STMT:
            self._visit_statement(child)

def _visit_statement(self, cursor: Cursor):
    """Visit a statement and extract calls."""
    if cursor.kind == CursorKind.IF_STMT:
        self._handle_if_stmt(cursor)
    elif cursor.kind == CursorKind.FOR_STMT:
        self._handle_for_stmt(cursor)
    elif cursor.kind == CursorKind.WHILE_STMT:
        self._handle_while_stmt(cursor)
    else:
        self._extract_calls_from_node(cursor)

def _handle_if_stmt(self, cursor: Cursor):
    """Handle if statement with proper context tracking."""
    children = list(cursor.get_children())
    
    if children:
        condition = self._get_condition_text(children[0])
        self._push_control_flow('if', condition)
        
        self._extract_calls_from_node(children[0])
        
        for child in children[1:]:
            if child.kind == CursorKind.COMPOUND_STMT:
                self._visit_statement(child)
        
        self._pop_control_flow()

def _handle_for_stmt(self, cursor: Cursor):
    """Handle for loop."""
    children = list(cursor.get_children())
    
    condition = None
    if len(children) >= 2:
        condition = self._get_condition_text(children[1])
    
    self._push_control_flow('for', condition)
    
    for child in children:
        self._extract_calls_from_node(child)
    
    self._pop_control_flow()

def _handle_while_stmt(self, cursor: Cursor):
    """Handle while loop."""
    children = list(cursor.get_children())
    
    condition = None
    if children:
        condition = self._get_condition_text(children[0])
    
    self._push_control_flow('while', condition)
    
    for child in children:
        self._extract_calls_from_node(child)
    
    self._pop_control_flow()

def _push_control_flow(self, context_type: str, condition: str = None):
    """Push control flow context onto stack."""
    depth = len(self.control_flow_stack)
    self.control_flow_stack.append(
        ControlFlowContext(context_type, condition, depth)
    )

def _pop_control_flow(self):
    """Pop control flow context from stack."""
    if self.control_flow_stack:
        self.control_flow_stack.pop()

def _get_condition_text(self, cursor: Cursor) -> str:
    """Extract condition text from cursor."""
    start = cursor.extent.start
    end = cursor.extent.end
    source = self.tu.get_source(start, end)
    return source.strip()
```

- [ ] **Step 5: Update call extraction to use context**

Update `_handle_call_expr` in `src/autosar_calltree/parsers/clang_function_visitor.py`:

```python
def _handle_call_expr(self, cursor: Cursor):
    """Handle a function call expression."""
    callee_name = cursor.spelling
    
    if callee_name in self.C_KEYWORDS or callee_name.startswith('__builtin'):
        return
    
    is_conditional = False
    condition = None
    is_loop = False
    loop_condition = None
    
    if self.control_flow_stack:
        ctx = self.control_flow_stack[-1]
        if ctx.context_type in ('if', 'else'):
            is_conditional = True
            condition = ctx.condition
        elif ctx.context_type in ('for', 'while', 'do'):
            is_loop = True
            loop_condition = ctx.condition
    
    call = FunctionCall(
        name=callee_name,
        is_conditional=is_conditional,
        condition=condition,
        is_loop=is_loop,
        loop_condition=loop_condition,
        line_number=cursor.location.line
    )
    
    if self.current_function:
        self.current_function.calls.append(call)
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_if_statement_attribution -v`
Expected: PASS

- [ ] **Step 7: Commit control flow tracking**

```bash
git add src/autosar_calltree/parsers/clang_function_visitor.py tests/fixtures/control_flow_attribution/ tests/unit/parsers/test_clang_parser.py
git commit -m "feat: implement control flow tracking for if statements"
```

---

### Task 12: Test Loop Attribution

**Files:**
- Create: `tests/fixtures/control_flow_attribution/test_loops.c`
- Modify: `tests/unit/parsers/test_clang_parser.py`

- [ ] **Step 1: Create test fixture for loops**

Create `tests/fixtures/control_flow_attribution/test_loops.c`:

```c
/*
 * Test control flow attribution for loops
 */

void for_loop_call(void) {}
void while_loop_call(void) {}
void do_while_call(void) {}

void test_loops(int max) {
    for (int i = 0; i < max; i++) {
        for_loop_call();
    }
    
    while (max > 0) {
        while_loop_call();
        max--;
    }
    
    do {
        do_while_call();
    } while (max < 10);
}
```

- [ ] **Step 2: Write test for loop attribution**

Add to `tests/unit/parsers/test_clang_parser.py`:

```python
def test_clang_parser_loop_attribution():
    """Test that calls are attributed to loops."""
    parser = ClangParser()
    fixture_path = Path('tests/fixtures/control_flow_attribution/test_loops.c')
    
    functions = parser.parse_file(fixture_path)
    
    test_func = [f for f in functions if f.name == 'test_loops'][0]
    
    for_call = [c for c in test_func.calls if c.name == 'for_loop_call'][0]
    assert for_call.is_loop == True
    assert 'i < max' in for_call.loop_condition
    
    while_call = [c for c in test_func.calls if c.name == 'while_loop_call'][0]
    assert while_call.is_loop == True
    assert 'max > 0' in while_call.loop_condition
```

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest tests/unit/parsers/test_clang_parser.py::test_clang_parser_loop_attribution -v`
Expected: PASS

- [ ] **Step 4: Commit loop attribution test**

```bash
git add tests/fixtures/control_flow_attribution/test_loops.c tests/unit/parsers/test_clang_parser.py
git commit -m "test: add test for loop attribution"
```

---

## Phase 3: Cleanup and Migration

### Task 13: Remove Old Parser Files

**Files:**
- Remove: `src/autosar_calltree/parsers/c_parser.py`
- Remove: `src/autosar_calltree/parsers/function_visitor.py`
- Remove: `src/autosar_calltree/parsers/autosar_parser.py`

- [ ] **Step 1: Remove old parser files**

```bash
rm src/autosar_calltree/parsers/c_parser.py
rm src/autosar_calltree/parsers/function_visitor.py
rm src/autosar_calltree/parsers/autosar_parser.py
```

- [ ] **Step 2: Verify no imports of old parsers**

Run: `grep -r "from.*c_parser import" src/ tests/`
Expected: No matches

Run: `grep -r "from.*autosar_parser import" src/ tests/`
Expected: No matches

- [ ] **Step 3: Commit removal**

```bash
git add -A
git commit -m "refactor: remove old pycparser-based parsers"
```

---

### Task 14: Remove Preprocessing Module

**Files:**
- Remove: `src/autosar_calltree/preprocessing/` (entire directory)
- Remove: `tests/unit/preprocessing/` (entire directory)

- [ ] **Step 1: Remove preprocessing directories**

```bash
rm -rf src/autosar_calltree/preprocessing/
rm -rf tests/unit/preprocessing/
```

- [ ] **Step 2: Verify no imports of preprocessing**

Run: `grep -r "from.*preprocessing import" src/ tests/`
Expected: No matches

- [ ] **Step 3: Commit removal**

```bash
git add -A
git commit -m "refactor: remove preprocessing module (clang handles this)"
```

---

### Task 15: Update All Test Imports

**Files:**
- Modify: All test files that import old parsers

- [ ] **Step 1: Find all test files with old imports**

Run: `grep -l "CParser\|AutosarParser" tests/unit/**/*.py`
Expected: List of files to update

- [ ] **Step 2: Update test imports**

For each file found, replace:
```python
from autosar_calltree.parsers.c_parser import CParser
```

With:
```python
from autosar_calltree.parsers import ClangParser
```

And replace `CParser` with `ClangParser` in test code.

- [ ] **Step 3: Run all tests**

Run: `pytest tests/unit/ -v`
Expected: All tests pass (or identify issues to fix)

- [ ] **Step 4: Commit test updates**

```bash
git add tests/
git commit -m "refactor: update all tests to use ClangParser"
```

---

### Task 16: Update Documentation

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/requirements/requirements_parsers.md`

- [ ] **Step 1: Update README.md**

Update installation section in `README.md`:

```markdown
## Installation

### Prerequisites

**libclang** is required for parsing C code:

**macOS (with Homebrew)**:
```bash
brew install llvm
pip install autosar-calltree
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install libclang-dev
pip install autosar-calltree
```

**Windows**:
```bash
pip install autosar-calltree
# libclang is bundled with the Python package
```
```

- [ ] **Step 2: Update CHANGELOG.md**

Add entry to `CHANGELOG.md`:

```markdown
## [0.9.0] - 2026-05-31

### Changed
- **BREAKING**: Replaced pycparser with clang for more accurate parsing
- Removed separate preprocessing module (clang handles preprocessing internally)
- Simplified PreprocessorConfig to control include paths and compiler flags only

### Added
- Comprehensive function call extraction from all expression contexts
- Precise control flow attribution for if/else/for/while statements
- Better handling of nested calls and complex expressions

### Removed
- pycparser dependency
- AutosarParser (functionality merged into ClangParser)
- Separate preprocessing stage

### Migration Guide
See `docs/superpowers/specs/2026-05-31-clang-parser-migration-design.md` for detailed migration instructions.
```

- [ ] **Step 3: Update requirements documentation**

Update `docs/requirements/requirements_parsers.md` to reflect clang-based architecture.

- [ ] **Step 4: Commit documentation updates**

```bash
git add README.md CHANGELOG.md docs/
git commit -m "docs: update documentation for clang parser migration"
```

---

### Task 17: Update Version Number

**Files:**
- Modify: `src/autosar_calltree/version.py`

- [ ] **Step 1: Update version**

Update `src/autosar_calltree/version.py`:

```python
__version__ = "0.9.0"
```

- [ ] **Step 2: Commit version update**

```bash
git add src/autosar_calltree/version.py
git commit -m "chore: bump version to 0.9.0 for clang parser"
```

---

### Task 18: Run Full Test Suite

**Files:**
- Test: All tests

- [ ] **Step 1: Run all unit tests**

Run: `pytest tests/unit/ -v --tb=short`
Expected: All tests pass

- [ ] **Step 2: Run all integration tests**

Run: `pytest tests/integration/ -v --tb=short`
Expected: All tests pass

- [ ] **Step 3: Run quality checks**

Run: `./scripts/run_quality.sh`
Expected: All quality checks pass

- [ ] **Step 4: Fix any failing tests**

If any tests fail, debug and fix them before proceeding.

---

### Task 19: Create Release

**Files:**
- Git: Create release tag

- [ ] **Step 1: Create release branch**

```bash
git checkout -b release/0.9.0
```

- [ ] **Step 2: Merge to main**

```bash
git checkout main
git merge release/0.9.0
```

- [ ] **Step 3: Create release tag**

```bash
git tag -a v0.9.0 -m "Release 0.9.0: Clang parser migration"
```

- [ ] **Step 4: Push to remote**

```bash
git push origin main
git push origin v0.9.0
```

---

## Success Criteria

After completing all tasks:

1. ✅ All tests pass with clang parser
2. ✅ No pycparser dependencies remain
3. ✅ Function call extraction is 100% accurate
4. ✅ Control flow attribution works correctly
5. ✅ Documentation is updated
6. ✅ Version is bumped to 0.9.0
7. ✅ Quality checks pass (flake8, mypy, black)

---

## Notes

- Each task should be completed in order
- Run tests after each task to catch issues early
- Commit frequently with clear messages
- If tests fail, debug before moving to next task
- Update this plan if unexpected issues arise
