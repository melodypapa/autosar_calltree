"""
Traditional C function parser.

This module handles parsing of traditional C function declarations and definitions,
extracting function information including parameters, return types, and function calls.
"""

import re
from pathlib import Path
from typing import List, Optional

from ..database.models import FunctionInfo, FunctionType, Parameter


class CParser:
    """Parser for traditional C function declarations and definitions."""

    # C keywords to exclude from function call extraction
    C_KEYWORDS = {
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
        "_Alignas",
        "_Alignof",
        "_Atomic",
        "_Static_assert",
        "_Noreturn",
        "_Thread_local",
        "_Generic",
    }

    # Common AUTOSAR types
    AUTOSAR_TYPES = {
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

    def __init__(self):
        """Initialize the C parser."""
        # Import AutosarParser to handle AUTOSAR macros
        from .autosar_parser import AutosarParser

        self.autosar_parser = AutosarParser()

        # Pattern for traditional C function declarations/definitions
        # Matches: [static] [inline] return_type function_name(params)
        self.function_pattern = re.compile(
            r"^\s*"  # Start of line with optional whitespace
            r"(?P<static>static\s+)?"  # Optional static keyword
            r"(?P<inline>inline|__inline__|__inline\s+)?"  # Optional inline
            r"(?P<return_type>[\w\s\*]+?)\s+"  # Return type (can include spaces, pointers)
            r"(?P<function_name>[a-zA-Z_][a-zA-Z0-9_]*)\s*"  # Function name
            r"\((?P<params>[^)]*)\)",  # Parameters in parentheses
            re.MULTILINE,
        )

        # Pattern to match function bodies { ... }
        self.function_body_pattern = re.compile(
            r"\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}", re.DOTALL
        )

        # Pattern for function calls: identifier(
        self.function_call_pattern = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")

        # Pattern for RTE calls
        self.rte_call_pattern = re.compile(r"\bRte_[a-zA-Z_][a-zA-Z0-9_]*\s*\(")

    def parse_file(self, file_path: Path) -> List[FunctionInfo]:
        """
        Parse a C source file and extract all function definitions.

        Tries AUTOSAR macros first, then falls back to traditional C parsing.

        Args:
            file_path: Path to the C source file

        Returns:
            List of FunctionInfo objects for all functions found
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []

        # Remove comments to avoid false positives
        content = self._remove_comments(content)

        functions = []

        # Quick check: only process AUTOSAR if file contains FUNC macros
        if "FUNC(" in content or "FUNC_P2" in content:
            # Try to find AUTOSAR functions line by line
            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                # Only check lines that look like AUTOSAR declarations
                if "FUNC" in line and "(" in line:
                    autosar_func = self.autosar_parser.parse_function_declaration(
                        line, file_path, line_num
                    )
                    if autosar_func:
                        # Extract function body and calls for AUTOSAR functions too
                        # Find the position of this line in the content
                        line_start = content.find(line)
                        if line_start != -1:
                            # Position after the function declaration line
                            body_start = line_start + len(line)
                            function_body = self._extract_function_body(
                                content, body_start
                            )
                            if function_body:
                                called_functions = self._extract_function_calls(
                                    function_body
                                )
                                autosar_func.calls = called_functions
                        functions.append(autosar_func)

        # Then, parse traditional C functions
        for match in self.function_pattern.finditer(content):
            func_info = self._parse_function_match(match, content, file_path)
            if func_info:
                # Check if this function was already found as AUTOSAR
                is_duplicate = any(
                    f.name == func_info.name and f.line_number == func_info.line_number
                    for f in functions
                )
                if not is_duplicate:
                    functions.append(func_info)

        return functions

    def _remove_comments(self, content: str) -> str:
        """
        Remove C-style comments from source code.

        Args:
            content: Source code content

        Returns:
            Content with comments removed
        """
        # Remove multi-line comments /* ... */
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        # Remove single-line comments // ...
        content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
        return content

    def _parse_function_match(
        self, match: re.Match, content: str, file_path: Path
    ) -> Optional[FunctionInfo]:
        """
        Parse a regex match into a FunctionInfo object.

        Args:
            match: Regex match object for function declaration
            content: Full file content
            file_path: Path to source file

        Returns:
            FunctionInfo object or None if parsing fails
        """
        static_keyword = match.group("static")
        match.group("inline")
        return_type = match.group("return_type").strip()
        function_name = match.group("function_name")
        params_str = match.group("params")

        # Skip if this looks like a macro or preprocessor directive
        if return_type.startswith("#"):
            return None

        # Skip if return type or function name is a C keyword (control structures)
        if return_type in self.C_KEYWORDS or function_name in self.C_KEYWORDS:
            return None

        # Skip common control structures
        if function_name in ["if", "for", "while", "switch", "case", "else"]:
            return None

        # Determine function type - all traditional C functions use TRADITIONAL_C
        # (static is tracked separately via is_static parameter)
        func_type = FunctionType.TRADITIONAL_C

        # Parse parameters
        parameters = self._parse_parameters(params_str)

        # Try to find function body
        body_start = match.end()
        function_body = self._extract_function_body(content, body_start)

        # Extract function calls from body
        called_functions = []
        if function_body:
            called_functions = self._extract_function_calls(function_body)

        # Determine line number
        line_number = content[: match.start()].count("\n") + 1

        return FunctionInfo(
            name=function_name,
            return_type=return_type,
            parameters=parameters,
            function_type=func_type,
            file_path=Path(file_path),
            line_number=line_number,
            calls=called_functions,
            is_static=bool(static_keyword),
        )

    def _parse_parameters(self, params_str: str) -> List[Parameter]:
        """
        Parse function parameters from parameter string.

        Args:
            params_str: String containing function parameters

        Returns:
            List of Parameter objects
        """
        params_str = params_str.strip()

        # Handle void or empty parameters
        if not params_str or params_str == "void":
            return []

        parameters = []
        # Split by comma, but respect nested parentheses and brackets
        param_parts = self._smart_split(params_str, ",")

        for param in param_parts:
            param = param.strip()
            if not param:
                continue

            # Parse parameter: type [*] name [array]
            # Examples: "uint8 value", "uint16* ptr", "const ConfigType* config"
            param_match = re.match(
                r"^(?P<type>[\w\s\*]+?)\s*(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)?"
                r"(?P<array>\[[^\]]*\])?$",
                param,
            )

            if param_match:
                param_type = param_match.group("type").strip()
                param_name = param_match.group("name") or ""
                is_pointer = "*" in param_type
                # Note: arrays detected but not separately tracked in current Parameter model

                # Clean up type (remove extra spaces and trailing *)
                param_type = re.sub(r"\s+", " ", param_type).strip()
                param_type = param_type.rstrip("*").strip()

                parameters.append(
                    Parameter(
                        name=param_name, param_type=param_type, is_pointer=is_pointer
                    )
                )

        return parameters

    def _smart_split(self, text: str, delimiter: str) -> List[str]:
        """
        Split text by delimiter, respecting nested parentheses/brackets.

        Args:
            text: Text to split
            delimiter: Delimiter character

        Returns:
            List of split parts
        """
        parts = []
        current = []
        depth = 0

        for char in text:
            if char in "([{":
                depth += 1
                current.append(char)
            elif char in ")]}":
                depth -= 1
                current.append(char)
            elif char == delimiter and depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(char)

        if current:
            parts.append("".join(current))

        return parts

    def _extract_function_body(self, content: str, start_pos: int) -> Optional[str]:
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

    def _extract_function_calls(self, function_body: str) -> List[str]:
        """
        Extract function calls from a function body.

        Args:
            function_body: Function body text

        Returns:
            List of called function names
        """
        called_functions = set()

        # Find all potential function calls
        for match in self.function_call_pattern.finditer(function_body):
            function_name = match.group(1)

            # Skip C keywords
            if function_name in self.C_KEYWORDS:
                continue

            # Skip AUTOSAR types (might be casts)
            if function_name in self.AUTOSAR_TYPES:
                continue

            called_functions.add(function_name)

        # Also extract RTE calls explicitly
        for match in self.rte_call_pattern.finditer(function_body):
            rte_function = match.group(0).rstrip("(").strip()
            called_functions.add(rte_function)

        return sorted(list(called_functions))

    def parse_function_declaration(self, declaration: str) -> Optional[FunctionInfo]:
        """
        Parse a single function declaration string.

        Args:
            declaration: Function declaration as a string

        Returns:
            FunctionInfo object or None if parsing fails
        """
        match = self.function_pattern.search(declaration)
        if not match:
            return None

        return self._parse_function_match(match, declaration, Path("unknown"))
