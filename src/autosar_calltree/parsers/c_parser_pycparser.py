"""
C function parser using pycparser.

This module provides an alternative to the regex-based CParser that uses
pycparser for more reliable parsing of standard C code. AUTOSAR macros
are still handled by AutosarParser.

Example usage:
    from autosar_calltree.parsers.c_parser_pycparser import CParserPyCParser

    parser = CParserPyCParser()
    functions = parser.parse_file(Path("example.c"))
"""

import re
from pathlib import Path
from typing import List, Optional

try:
    from pycparser import c_ast, c_parser
    PYCPARSER_AVAILABLE = True
except ImportError:
    PYCPARSER_AVAILABLE = False
    c_ast = None  # type: ignore
    c_parser = None  # type: ignore

from ..database.models import FunctionCall, FunctionInfo, FunctionType, Parameter


class FunctionVisitor(c_ast.NodeVisitor):
    """AST visitor to extract function definitions and calls."""

    def __init__(
        self,
        file_path: Path,
        content: str,
    ):
        """
        Initialize the visitor.

        Args:
            file_path: Path to the source file
            content: Original source code content
        """
        self.file_path = file_path
        self.content = content
        self.functions: List[FunctionInfo] = []
        self.current_function: Optional[FunctionInfo] = None

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
        """
        Extract return type from function definition.

        Args:
            node: Function definition AST node

        Returns:
            Return type string
        """
        # Navigate the type hierarchy
        # FuncDef -> Decl -> TypeDecl (or PtrDecl) -> type
        decl_type = node.decl.type

        # Handle pointer return types
        if isinstance(decl_type, c_ast.PtrDecl):
            # Get the type being pointed to
            underlying_type = decl_type.type
            base_type = self._get_type_name(underlying_type)
            return f"{base_type}*"

        # Handle array return types (uncommon but valid)
        if isinstance(decl_type, c_ast.ArrayDecl):
            underlying_type = decl_type.type
            base_type = self._get_type_name(underlying_type)
            return f"{base_type}[]"

        # Standard type
        return self._get_type_name(decl_type)

    def _get_type_name(self, type_node: c_ast.Node) -> str:
        """
        Get the name of a type node.

        Args:
            type_node: Type AST node

        Returns:
            Type name string
        """
        # Handle TypeDecl (most common)
        if isinstance(type_node, c_ast.TypeDecl):
            if isinstance(type_node.type, c_ast.IdentifierType):
                return " ".join(type_node.type.names)
            elif isinstance(type_node.type, c_ast.Struct):
                return f"struct {type_node.type.name}"
            elif isinstance(type_node.type, c_ast.Union):
                return f"union {type_node.type.name}"
            elif isinstance(type_node.type, c_ast.Enum):
                return f"enum {type_node.type.name}"

        # Handle function types (function pointers)
        if isinstance(type_node, c_ast.FuncDecl):
            return self._get_type_name(type_node.type)

        return "unknown"

    def _extract_parameters(self, node: c_ast.FuncDef) -> List[Parameter]:
        """
        Extract parameters from function definition.

        Args:
            node: Function definition AST node

        Returns:
            List of Parameter objects
        """
        parameters: List[Parameter] = []

        # Get the parameters node
        decl = node.decl
        if not hasattr(decl.type, "args") or decl.type.args is None:
            # No parameters (void)
            return parameters

        for param in decl.type.args.params:
            # Skip void parameters (shouldn't happen but defensive)
            if isinstance(param, c_ast.Typename) and hasattr(param.type, "names"):
                if "void" in param.type.names:
                    continue

            param_info = self._extract_parameter(param)
            if param_info:
                parameters.append(param_info)

        return parameters

    def _extract_parameter(self, param: c_ast.Node) -> Optional[Parameter]:
        """
        Extract a single parameter from AST node.

        Args:
            param: Parameter AST node

        Returns:
            Parameter object or None
        """
        # Get parameter name
        param_name = ""
        if isinstance(param, c_ast.Decl):
            param_name = param.name or ""
            type_node = param.type
        elif isinstance(param, c_ast.Typename):
            type_node = param.type
        else:
            return None

        # Determine if pointer
        is_pointer = False
        if isinstance(type_node, c_ast.PtrDecl):
            is_pointer = True
            type_node = type_node.type

        # Get type name
        param_type = self._get_type_name(type_node)

        return Parameter(
            name=param_name,
            param_type=param_type,
            is_pointer=is_pointer,
        )

    def _is_static(self, node: c_ast.FuncDef) -> bool:
        """
        Check if function is static.

        Args:
            node: Function definition AST node

        Returns:
            True if function is static
        """
        if hasattr(node.decl, "storage_class"):
            return str(node.decl.storage_class) == "static"
        return False

    def _extract_function_calls(self, node: c_ast.FuncDef) -> List[FunctionCall]:
        """
        Extract function calls from function body.

        Args:
            node: Function definition AST node

        Returns:
            List of FunctionCall objects
        """
        # Walk the AST to find all function calls
        class CallVisitor(c_ast.NodeVisitor):
            def __init__(self, parent_visitor: FunctionVisitor):
                self.parent = parent_visitor
                self.calls: List[FunctionCall] = []
                self.seen: set[str] = set()

            def visit_FuncCall(self, call_node: c_ast.FuncCall) -> None:
                """Visit a function call node."""
                if isinstance(call_node.name, c_ast.IdentifierType):
                    func_name = call_node.name.names[0]
                elif isinstance(call_node.name, c_ast.ID):
                    func_name = call_node.name.name
                else:
                    # Handle other cases (e.g., function pointers)
                    return

                # Skip C keywords
                if func_name in CParserPyCParser.C_KEYWORDS:
                    return

                # Skip AUTOSAR types (might be casts)
                if func_name in CParserPyCParser.AUTOSAR_TYPES:
                    return

                # Skip AUTOSAR macros
                if func_name in CParserPyCParser.AUTOSAR_MACROS:
                    return

                # Track unique calls
                if func_name not in self.seen:
                    self.seen.add(func_name)
                    self.calls.append(
                        FunctionCall(
                            name=func_name,
                            is_conditional=False,  # TODO: Track if/else context
                            condition=None,
                            is_loop=False,  # TODO: Track loop context
                            loop_condition=None,
                        )
                    )

        call_visitor = CallVisitor(self)
        call_visitor.visit(node)

        return call_visitor.calls


class CParserPyCParser:
    """C parser using pycparser library."""

    # C keywords to exclude from function call extraction
    C_KEYWORDS = {
        "if", "else", "while", "for", "do", "switch", "case", "default",
        "return", "break", "continue", "goto", "sizeof", "typedef", "struct",
        "union", "enum", "const", "volatile", "static", "extern", "auto",
        "register", "inline", "__inline", "__inline__", "restrict",
        "__restrict", "__restrict__", "_Bool", "_Complex", "_Imaginary",
    }

    # AUTOSAR and standard C macros to exclude
    AUTOSAR_MACROS = {
        "INT8_C", "INT16_C", "INT32_C", "INT64_C",
        "UINT8_C", "UINT16_C", "UINT32_C", "UINT64_C",
        "INTMAX_C", "UINTMAX_C",
        "TS_MAKEREF2CFG", "TS_MAKENULLREF2CFG", "TS_MAKEREFLIST2CFG",
        "STD_ON", "STD_OFF",
    }

    # Common AUTOSAR types
    AUTOSAR_TYPES = {
        "uint8", "uint16", "uint32", "uint64",
        "sint8", "sint16", "sint32", "sint64",
        "boolean", "Boolean", "float32", "float64",
        "Std_ReturnType", "StatusType",
    }

    def __init__(self):
        """Initialize the pycparser-based C parser."""
        if not PYCPARSER_AVAILABLE:
            raise ImportError(
                "pycparser is not installed. Install it with: pip install pycparser"
            )

        self.parser = c_parser.CParser()

    def parse_file(self, file_path: Path) -> List[FunctionInfo]:
        """
        Parse a C source file and extract all function definitions.

        Handles both AUTOSAR macros (via AutosarParser) and traditional C functions
        (via pycparser AST).

        Args:
            file_path: Path to the C source file

        Returns:
            List of FunctionInfo objects
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []

        all_functions = []
        seen_functions = set()  # Track (name, line_number) to avoid duplicates

        # First, parse AUTOSAR functions if any
        if "FUNC(" in content:
            from .autosar_parser import AutosarParser

            autosar_parser = AutosarParser()
            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                if "FUNC" in line and "(" in line:
                    autosar_func = autosar_parser.parse_function_declaration(
                        line, file_path, line_num
                    )
                    if autosar_func:
                        key = (autosar_func.name, autosar_func.line_number)
                        if key not in seen_functions:
                            seen_functions.add(key)
                            # Extract function body and calls
                            line_start = content.find(line)
                            if line_start != -1:
                                body_start = line_start + len(line)
                                function_body = self._extract_function_body_from_content(
                                    content, body_start
                                )
                                if function_body:
                                    called_functions = self._extract_function_calls_from_body(
                                        function_body
                                    )
                                    autosar_func.calls = called_functions
                            all_functions.append(autosar_func)

        # Then, parse traditional C functions using pycparser
        preprocessed = self._preprocess_content(content)

        # Check if file contains any traditional C functions
        if self._has_traditional_c_functions(preprocessed):
            try:
                # Parse the preprocessed code
                ast = self.parser.parse(preprocessed, filename=str(file_path))

                # Visit the AST to extract functions
                visitor = FunctionVisitor(file_path, content)
                visitor.visit(ast)

                # Add traditional C functions, avoiding duplicates
                for func in visitor.functions:
                    key = (func.name, func.line_number)
                    if key not in seen_functions:
                        seen_functions.add(key)
                        all_functions.append(func)

            except Exception:
                # Parsing failed - silently ignore and return what we have
                pass

        return all_functions

    def _preprocess_content(self, content: str) -> str:
        """
        Preprocess C source code for pycparser.

        This handles:
        - AUTOSAR macros (FUNC, VAR, P2VAR, etc.) that pycparser can't handle
        - Preprocessor directives
        - Other issues that would confuse pycparser

        Args:
            content: Original C source code

        Returns:
            Preprocessed C code suitable for pycparser
        """
        preprocessed = content

        # Remove comments (pycparser can handle them, but removing helps)
        preprocessed = re.sub(r"/\*.*?\*/", "", preprocessed, flags=re.DOTALL)
        preprocessed = re.sub(r"//.*?$", "", preprocessed, flags=re.MULTILINE)

        # Replace AUTOSAR function macros with dummy declarations
        # Pattern: FUNC(return_type, class) func_name(params);
        # We convert to: return_type func_name(params);
        preprocessed = re.sub(
            r"FUNC\s*\(\s*([^,]+)\s*,\s*[^)]+\)\s*",
            r"\1 ",
            preprocessed,
        )

        # Replace FUNC_P2VAR, FUNC_P2CONST, etc.
        preprocessed = re.sub(
            r"FUNC_P2\w+\s*\(\s*([^,]+)\s*,\s*[^,]+,\s*[^)]+\)\s*",
            r"\1* ",
            preprocessed,
        )

        # Remove AUTOSAR variable macros from parameter lists
        # VAR(type, class) -> type
        preprocessed = re.sub(
            r"VAR\s*\(\s*([^,]+)\s*,\s*[^)]+\)",
            r"\1",
            preprocessed,
        )

        # P2VAR(type, class, ...) -> type*
        preprocessed = re.sub(
            r"P2VAR\s*\(\s*([^,]+)\s*,\s*[^,]+,\s*[^)]+\)",
            r"\1*",
            preprocessed,
        )

        # P2CONST(type, class, ...) -> const type*
        preprocessed = re.sub(
            r"P2CONST\s*\(\s*([^,]+)\s*,\s*[^,]+,\s*[^)]+\)",
            r"const \1*",
            preprocessed,
        )

        # CONST(type, ...) -> const type
        preprocessed = re.sub(
            r"CONST\s*\(\s*([^,]+)\s*,\s*[^)]+\)",
            r"const \1",
            preprocessed,
        )

        # Remove other problematic preprocessor directives
        # (keep includes for now, they'll be handled by cpp if needed)
        # Remove #pragma, #line, etc.
        preprocessed = re.sub(r"^#\s*(pragma|line|error|warning).*$", "", preprocessed, flags=re.MULTILINE)

        return preprocessed

    def _extract_function_body_from_content(
        self, content: str, start_pos: int
    ) -> Optional[str]:
        """
        Extract function body starting from a position.

        Args:
            content: Full file content
            start_pos: Position to start searching for body

        Returns:
            Function body string or None if not found
        """
        # Skip whitespace and look for opening brace
        remaining = content[start_pos:].lstrip()
        if not remaining.startswith("{"):
            return None

        # Match balanced braces
        brace_count = 0
        body_chars = []

        for char in remaining:
            body_chars.append(char)
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    break

        if brace_count == 0:
            return "".join(body_chars)

        return None

    def _extract_function_calls_from_body(self, function_body: str) -> List[FunctionCall]:
        """
        Extract function calls from a function body.

        Simple regex-based extraction for AUTOSAR functions.

        Args:
            function_body: Function body text

        Returns:
            List of FunctionCall objects
        """
        called_functions: List[FunctionCall] = []
        seen_names = set()

        # Pattern to match function calls: identifier(
        call_pattern = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")

        for match in call_pattern.finditer(function_body):
            function_name = match.group(1)

            # Skip C keywords
            if function_name in self.C_KEYWORDS:
                continue

            # Skip AUTOSAR types (might be casts)
            if function_name in self.AUTOSAR_TYPES:
                continue

            # Skip AUTOSAR macros
            if function_name in self.AUTOSAR_MACROS:
                continue

            # Track unique calls
            if function_name not in seen_names:
                seen_names.add(function_name)
                called_functions.append(
                    FunctionCall(
                        name=function_name,
                        is_conditional=False,  # Simple extraction, no if/else tracking
                        condition=None,
                        is_loop=False,  # No loop tracking
                        loop_condition=None,
                    )
                )

        return sorted(called_functions, key=lambda fc: fc.name)

    def _has_traditional_c_functions(self, content: str) -> bool:
        """
        Check if content contains traditional C functions (not just AUTOSAR macros).

        Args:
            content: Preprocessed C source code

        Returns:
            True if traditional C functions are likely present
        """
        # Quick heuristic: look for function-like patterns
        # that don't start with FUNC (AUTOSAR macros)

        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            # Look for patterns like: "return_type func_name("
            # but not "FUNC(...)"
            if re.match(r"^[a-zA-Z_][a-zA-Z0-9_*\s]+\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(", line):
                if not line.startswith("FUNC"):
                    return True

        return False


# Backward compatibility: provide the CParser class name
# that users might expect
CParser = CParserPyCParser
