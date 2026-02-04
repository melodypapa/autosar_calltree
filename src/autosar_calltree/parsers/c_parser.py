"""
Traditional C function parser.

This module handles parsing of traditional C function declarations and definitions,
extracting function information including parameters, return types, and function calls.
"""

import re
from pathlib import Path
from typing import List, Optional

from ..database.models import FunctionCall, FunctionInfo, FunctionType, Parameter


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

    # AUTOSAR and standard C macros to exclude from function detection
    # These macros look like function calls but should not be parsed as functions
    AUTOSAR_MACROS = {
        # Standard C integer literal macros (stdint.h)
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
        # AUTOSAR tool-specific macros
        "TS_MAKEREF2CFG",
        "TS_MAKENULLREF2CFG",
        "TS_MAKEREFLIST2CFG",
        # Common AUTOSAR configuration macros
        "STD_ON",
        "STD_OFF",
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
        # Optimized to avoid catastrophic backtracking with length limits
        self.function_pattern = re.compile(
            r"^\s*"  # Start of line with optional whitespace
            r"(?P<static>static\s+)?"  # Optional static keyword
            r"(?P<inline>inline|__inline__|__inline\s+)?"  # Optional inline
            r"(?P<return_type>[\w\s\*]{1,101}?)\s+"  # Return type (1-101 chars, non-greedy)
            r"(?P<function_name>[a-zA-Z_][a-zA-Z0-9_]{1,50})\s*"  # Function name (1-50 chars)
            r"\((?P<params>[^()]{0,500}(?:\([^()]{0,100}\)[^()]{0,500})*)\)",  # Parameters (limited length)
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
        # Use line-by-line matching to avoid catastrophic backtracking on large files
        lines = content.split("\n")
        current_pos = 0
        for line_num, line in enumerate(lines, 1):
            line_length = len(line) + 1  # +1 for newline
            # Skip empty lines and lines that don't look like function declarations
            if not line or "(" not in line or ";" in line:
                current_pos += line_length
                continue

            # Check if line matches function pattern
            match = self.function_pattern.match(line)
            if match:
                # Adjust match positions to be relative to full content
                class AdjustedMatch:
                    def __init__(self, original_match, offset):
                        self._match = original_match
                        self._offset = offset

                    def group(self, name):
                        return self._match.group(name)

                    def start(self):
                        return self._offset + self._match.start()

                    def end(self):
                        return self._offset + self._match.end()

                adjusted_match = AdjustedMatch(match, current_pos)
                func_info = self._parse_function_match(adjusted_match, content, file_path)  # type: ignore[arg-type]
                if func_info:
                    # Check if this function was already found as AUTOSAR
                    is_duplicate = any(
                        f.name == func_info.name and f.line_number == func_info.line_number
                        for f in functions
                    )
                    if not is_duplicate:
                        functions.append(func_info)

            current_pos += line_length

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

        # Skip AUTOSAR and standard C macros that look like function calls
        # This prevents false positives on macros like UINT32_C(value), TS_MAKEREF2CFG(...)
        if function_name in self.AUTOSAR_MACROS:
            return None

        # Skip standard C integer literal macros (those ending with _C)
        # These are defined in stdint.h and look like: INT32_C(42), UINT64_C(100)
        if function_name.endswith("_C"):
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

    def _extract_function_calls(self, function_body: str) -> List[FunctionCall]:
        """
        Extract function calls from a function body.

        Args:
            function_body: Function body text

        Returns:
            List of FunctionCall objects with conditional status and condition text
        """
        called_functions: List[FunctionCall] = []

        # Analyze function body to track if/else context
        # We'll parse line by line to detect if/else blocks
        lines = function_body.split("\n")
        in_if_block = False
        in_else_block = False
        current_condition = None
        brace_depth = 0

        for line in lines:
            stripped = line.strip()

            # Track if/else block entry and extract condition
            if stripped.startswith("if ") or stripped.startswith("if("):
                in_if_block = True
                # Extract condition from if statement
                # Handle both "if (condition)" and "if(condition)" formats
                if_match = re.match(r'if\s*\(\s*(.+?)\s*\)', stripped)
                if if_match:
                    current_condition = if_match.group(1).strip()
                else:
                    # Fallback: try to extract everything between "if" and the first '{'
                    if_start = stripped.find("if")
                    brace_pos = stripped.find("{")
                    if brace_pos != -1:
                        condition_part = stripped[if_start+2:brace_pos].strip()
                        # Remove leading/trailing parentheses
                        condition_part = condition_part.lstrip("(").rstrip(")").strip()
                        current_condition = condition_part
                    else:
                        current_condition = "condition"
            elif stripped.startswith("else if") or stripped.startswith("else if("):
                in_if_block = True
                # Extract condition from else if statement
                elif_match = re.match(r'else\s+if\s*\(\s*(.+?)\s*\)', stripped)
                if elif_match:
                    current_condition = f"else if {elif_match.group(1).strip()}"
                else:
                    current_condition = "else if condition"
            elif stripped.startswith("else") and not stripped.startswith("else if"):
                in_else_block = True
                current_condition = "else"

            # Track brace depth for nested blocks
            brace_depth += stripped.count("{")
            brace_depth -= stripped.count("}")

            # Find function calls in this line
            for match in self.function_call_pattern.finditer(line):
                function_name = match.group(1)

                # Skip C keywords
                if function_name in self.C_KEYWORDS:
                    continue

                # Skip AUTOSAR types (might be casts)
                if function_name in self.AUTOSAR_TYPES:
                    continue

                # Check if this call is inside an if/else block
                is_conditional = (in_if_block or in_else_block) and brace_depth > 0

                # Add to called functions if not already present
                existing = next((fc for fc in called_functions if fc.name == function_name), None)
                if existing:
                    # Update conditional status if this occurrence is conditional
                    if is_conditional:
                        existing.is_conditional = True
                        if current_condition and not existing.condition:
                            existing.condition = current_condition
                else:
                    called_functions.append(
                        FunctionCall(
                            name=function_name,
                            is_conditional=is_conditional,
                            condition=current_condition if is_conditional else None
                        )
                    )

            # Also extract RTE calls explicitly
            for match in self.rte_call_pattern.finditer(line):
                rte_function = match.group(0).rstrip("(").strip()

                is_conditional = (in_if_block or in_else_block) and brace_depth > 0

                existing = next((fc for fc in called_functions if fc.name == rte_function), None)
                if existing:
                    if is_conditional:
                        existing.is_conditional = True
                        if current_condition and not existing.condition:
                            existing.condition = current_condition
                else:
                    called_functions.append(
                        FunctionCall(
                            name=rte_function,
                            is_conditional=is_conditional,
                            condition=current_condition if is_conditional else None
                        )
                    )

            # Exit if/else block when we close the brace
            if brace_depth == 0:
                in_if_block = False
                in_else_block = False
                current_condition = None

        # Sort by name for consistent output
        return sorted(called_functions, key=lambda fc: fc.name)

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
