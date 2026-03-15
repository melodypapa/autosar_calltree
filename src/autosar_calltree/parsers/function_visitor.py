"""
AST visitor for extracting function definitions from C code.

This module provides the FunctionVisitor class that walks pycparser
AST nodes to extract function definitions and calls.
"""

import re
from pathlib import Path
from typing import List, Optional, Set

from pycparser import c_ast

from ..database.models import FunctionCall, FunctionInfo, FunctionType, Parameter


class FunctionVisitor(c_ast.NodeVisitor):
    """AST visitor to extract function definitions and calls."""

    # C keywords to exclude from function call extraction
    C_KEYWORDS: Set[str] = {
        "if",
        "else",
        "while",
        "for",
        "do",
        "switch",
        "case",
        "default",
        "return",
        "break",
        "continue",
        "goto",
        "sizeof",
        "typedef",
        "struct",
        "union",
        "enum",
        "const",
        "volatile",
        "static",
        "extern",
        "auto",
        "register",
        "inline",
        "__inline",
        "__inline__",
        "restrict",
        "__restrict",
        "__restrict__",
        "_Bool",
        "_Complex",
        "_Imaginary",
    }

    # AUTOSAR and standard C macros to exclude
    AUTOSAR_MACROS: Set[str] = {
        "INT8_C",
        "INT16_C",
        "INT32_C",
        "INT64_C",
        "UINT8_C",
        "UINT16_C",
        "UINT32_C",
        "UINT64_C",
        "INTMAX_C",
        "UINTMAX_C",
        "TS_MAKEREF2CFG",
        "TS_MAKENULLREF2CFG",
        "TS_MAKEREFLIST2CFG",
        "STD_ON",
        "STD_OFF",
    }

    # Common AUTOSAR types
    AUTOSAR_TYPES: Set[str] = {
        "uint8",
        "uint16",
        "uint32",
        "uint64",
        "sint8",
        "sint16",
        "sint32",
        "sint64",
        "boolean",
        "Boolean",
        "float32",
        "float64",
        "Std_ReturnType",
        "StatusType",
    }

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
        # FuncDef -> Decl -> FuncDecl -> type (this is the return type)
        # For FuncDef, node.decl.type is a FuncDecl representing the function
        # The actual return type is node.decl.type.type
        decl_type = node.decl.type

        # For function definitions, decl_type is a FuncDecl
        # We need to go one level deeper to get the actual return type
        if isinstance(decl_type, c_ast.FuncDecl):
            return_type_node = decl_type.type
        else:
            # Fallback for other cases
            return_type_node = decl_type

        # First, get the return type from pycparser
        pycparser_return_type = self._get_return_type_from_node(return_type_node)

        # Workaround: pycparser doesn't preserve const qualifiers in some cases
        # Check if the original source has "const" but pycparser result doesn't
        if "const" not in pycparser_return_type.lower() and node.coord:
            # Try to extract the return type from source as a fallback
            source_return_type = self._extract_return_type_from_source(node)
            if source_return_type and "const" in source_return_type.lower():
                return source_return_type

        return pycparser_return_type

    def _get_return_type_from_node(self, return_type_node: c_ast.Node) -> str:
        """
        Extract return type from an AST node.

        Args:
            return_type_node: The return type AST node

        Returns:
            Return type string
        """
        # Handle pointer return types
        if isinstance(return_type_node, c_ast.PtrDecl):
            # Check for qualifiers on the PtrDecl itself (e.g., for "int * const")
            ptr_quals = []
            if hasattr(return_type_node, "qualifiers") and return_type_node.qualifiers:
                ptr_quals = list(return_type_node.qualifiers)

            # Get the type being pointed to
            underlying_type = return_type_node.type
            base_type = self._get_type_name(underlying_type, include_quals=True)

            # Combine pointer qualifiers with base type
            if ptr_quals:
                return f"{base_type}* {' '.join(ptr_quals)}"
            return f"{base_type}*"

        # Handle array return types (uncommon but valid)
        if isinstance(return_type_node, c_ast.ArrayDecl):
            underlying_type = return_type_node.type
            base_type = self._get_type_name(underlying_type, include_quals=True)
            return f"{base_type}[]"

        # Standard type
        return self._get_type_name(return_type_node, include_quals=True)

    def _extract_return_type_from_source(self, node: c_ast.FuncDef) -> Optional[str]:
        """
        Extract return type from original source code as a fallback.

        This is used when pycparser doesn't preserve const qualifiers.

        Args:
            node: Function definition AST node

        Returns:
            Return type string or None if extraction fails
        """
        if not self.content:
            return None

        # Look for the function declaration pattern in the original content
        # Pattern: return_type function_name(...)
        func_name = node.decl.name

        # Search for the function declaration in the original content
        # Pattern: function_name followed by (
        pattern = rf"([\w\s\*]+)\s+{re.escape(func_name)}\s*\("
        match = re.search(pattern, self.content)

        if not match:
            return None

        # Extract everything before the function name as the return type
        return_type_candidate = match.group(1).strip()

        # Validate that it looks like a type (contains alphanumeric or *)
        if re.match(r"^[\w\s\*]+$", return_type_candidate):
            return return_type_candidate

        return None

    def _get_type_name(self, type_node: c_ast.Node, include_quals: bool = False) -> str:
        """
        Get the name of a type node.

        Args:
            type_node: Type AST node
            include_quals: Whether to include type qualifiers (const, volatile)

        Returns:
            Type name string
        """
        # Handle TypeDecl (most common)
        if isinstance(type_node, c_ast.TypeDecl):
            # Add qualifiers if requested
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

            # Prepend qualifiers if any
            if quals:
                return f"{' '.join(quals)} {type_name}"
            return type_name

        # Handle PtrDecl - need to extract the underlying type and potentially its qualifiers
        if isinstance(type_node, c_ast.PtrDecl):
            # Check for qualifiers on the PtrDecl itself
            quals = []
            if include_quals and hasattr(type_node, "qualifiers"):
                if type_node.qualifiers:
                    quals = list(type_node.qualifiers)

            # Get the underlying type name
            underlying_name = self._get_type_name(
                type_node.type, include_quals=include_quals
            )

            # Prepend qualifiers if any
            if quals:
                return f"{' '.join(quals)} {underlying_name}"
            return underlying_name

        # Handle function types (function pointers)
        if isinstance(type_node, c_ast.FuncDecl):
            return self._get_type_name(type_node.type, include_quals=include_quals)

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
        is_const = False
        if isinstance(param, c_ast.Decl):
            param_name = param.name or ""
            type_node = param.type
            # Check if parameter is const (at PtrDecl or TypeDecl level)
            if hasattr(type_node, "qualifiers") and type_node.qualifiers:
                is_const = "const" in type_node.qualifiers
        elif isinstance(param, c_ast.Typename):
            type_node = param.type
            if hasattr(type_node, "qualifiers") and type_node.qualifiers:
                is_const = "const" in type_node.qualifiers
        else:
            return None

        # Determine if pointer
        is_pointer = False
        if isinstance(type_node, c_ast.PtrDecl):
            is_pointer = True
            # Check for const at the pointer level (e.g., "int * const")
            if hasattr(type_node, "qualifiers") and type_node.qualifiers:
                if "const" in type_node.qualifiers:
                    is_const = True
            type_node = type_node.type

        # Get type name with qualifiers
        param_type = self._get_type_name(type_node, include_quals=True)

        return Parameter(
            name=param_name,
            param_type=param_type,
            is_pointer=is_pointer,
            is_const=is_const,
        )

    def _is_static(self, node: c_ast.FuncDef) -> bool:
        """
        Check if function is static.

        Args:
            node: Function definition AST node

        Returns:
            True if function is static
        """
        if hasattr(node.decl, "storage") and node.decl.storage:
            # The storage attribute is a list of storage class specifiers
            # e.g., ['static'], ['extern'], ['inline', 'static'], etc.
            return "static" in node.decl.storage
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
            def __init__(self, parent_visitor: "FunctionVisitor"):
                self.parent = parent_visitor
                self.calls: List[FunctionCall] = []
                self.seen: Set[str] = set()

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
                            is_conditional=False,  # TODO: Track if/else context
                            condition=None,
                            is_loop=False,  # TODO: Track loop context
                            loop_condition=None,
                        )
                    )

        call_visitor = CallVisitor(self)
        call_visitor.visit(node)

        return call_visitor.calls
