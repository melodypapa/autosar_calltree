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
        i = 0
        while i < len(lines):
            line = lines[i]
            line_num = i + 1
            line_length = len(line) + 1  # +1 for newline

            # Skip empty lines and lines that don't look like function declarations
            if not line or "(" not in line or ";" in line:
                current_pos += line_length
                i += 1
                continue

            # First, try to match single-line function pattern
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
                        f.name == func_info.name
                        and f.line_number == func_info.line_number
                        for f in functions
                    )
                    if not is_duplicate:
                        functions.append(func_info)
                current_pos += line_length
                i += 1
            else:
                # Try to parse multi-line function prototype
                multiline_func = self._try_parse_multiline_function(
                    lines, i, content, current_pos, file_path
                )
                if multiline_func:
                    # Check for duplicates
                    is_duplicate = any(
                        f.name == multiline_func.name
                        and f.line_number == multiline_func.line_number
                        for f in functions
                    )
                    if not is_duplicate:
                        functions.append(multiline_func)
                    # Advance past the multiline function
                    # Find the line where closing ) is
                    lines_consumed = self._count_multiline_lines(lines[i:])
                    current_pos += sum(
                        len(lines[j]) + 1 for j in range(i, i + lines_consumed)
                    )
                    i += lines_consumed
                else:
                    current_pos += line_length
                    i += 1

        return functions

    def _count_multiline_lines(self, lines: List[str]) -> int:
        """
        Count how many lines a multi-line function prototype spans.

        Args:
            lines: List of lines starting from the first line of the prototype

        Returns:
            Number of lines consumed
        """
        paren_count = 0
        line_count = 0

        for line in lines:
            line_count += 1
            for char in line:
                if char == "(":
                    paren_count += 1
                elif char == ")":
                    paren_count -= 1
                    if paren_count == 0:
                        return line_count

        return line_count

    def _try_parse_multiline_function(
        self,
        lines: List[str],
        start_line_idx: int,
        content: str,
        start_pos: int,
        file_path: Path,
    ) -> Optional[FunctionInfo]:
        """
        Try to parse a multi-line function prototype.

        Args:
            lines: List of all lines in the file
            start_line_idx: Index of the first line to start parsing
            content: Full file content
            start_pos: Position of the first line in the content
            file_path: Path to the source file

        Returns:
            FunctionInfo object or None if not a multi-line function
        """
        # Combine lines until we find the closing parenthesis
        # We need to track the original combined string for position calculation
        # and a normalized string for matching (with spaces between lines)
        combined_lines = []
        paren_count = 0
        line_count = 0
        current_pos = start_pos

        # Look backwards to find the return type
        # The function might start with just the return type on a separate line
        actual_start_idx = start_line_idx
        while actual_start_idx > 0:
            prev_line = lines[actual_start_idx - 1].strip()
            # If the previous line looks like a return type (no parenthesis, not empty, not a comment)
            if (
                prev_line
                and "(" not in prev_line
                and not prev_line.startswith("//")
                and not prev_line.startswith("/*")
            ):
                # Check if it looks like a type (contains word characters, possibly with *)
                if re.match(r"^[\w\s\*]+$", prev_line):
                    actual_start_idx -= 1
                else:
                    break
            else:
                break

        # Recalculate start_pos based on actual_start_idx
        actual_start_pos = start_pos
        for i in range(actual_start_idx, start_line_idx):
            actual_start_pos -= len(lines[i]) + 1

        for i in range(actual_start_idx, len(lines)):
            line = lines[i]
            combined_lines.append(line)
            line_count += 1

            for char in line:
                if char == "(":
                    paren_count += 1
                elif char == ")":
                    paren_count -= 1
                    if paren_count == 0:
                        # Found the closing parenthesis, try to parse
                        # Join lines with spaces for pattern matching
                        combined = " ".join(combined_lines)
                        match = self.function_pattern.search(combined)
                        if match:
                            # Calculate the actual position in the content
                            # The match.start() is in the combined string with spaces
                            # We need to map this back to the original content
                            # For simplicity, use the position where the function name appears
                            func_name = match.group("function_name")
                            func_name_pos = combined.find(func_name, match.start())

                            # Calculate offset in original content
                            # Start from actual_start_pos and count characters until we reach func_name_pos
                            chars_seen = 0
                            func_start_pos = actual_start_pos
                            for line_idx, orig_line in enumerate(combined_lines):
                                line_in_combined = orig_line
                                if line_idx > 0:
                                    # Account for space we added
                                    chars_seen += 1
                                if chars_seen + len(line_in_combined) >= func_name_pos:
                                    # Found the line containing the function name
                                    func_start_pos = actual_start_pos + (
                                        func_name_pos - chars_seen
                                    )
                                    break
                                chars_seen += len(line_in_combined)

                            # Create a match object with correct positions
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

                            # Use func_start_pos as the base offset
                            adjusted_match = AdjustedMatch(
                                match, func_start_pos - match.start()
                            )
                            return self._parse_function_match(adjusted_match, content, file_path)  # type: ignore[arg-type]

                        return None

            current_pos += len(line) + 1  # +1 for newline

        return None

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
        collecting_multiline_condition = False
        multiline_condition_buffer = ""
        multiline_paren_depth = 0

        for line in lines:
            stripped = line.strip()

            # Check if we're collecting a multi-line condition
            if collecting_multiline_condition:
                multiline_condition_buffer += " " + stripped
                # Track parentheses in the condition using a stack
                for char in stripped:
                    if char == "(":
                        multiline_paren_depth += 1
                    elif char == ")":
                        multiline_paren_depth -= 1
                        if multiline_paren_depth == 0:
                            # Found the closing parenthesis
                            # Extract condition from the buffer
                            # Find the opening '(' after 'if' or 'else if'
                            if "if" in multiline_condition_buffer:
                                # Find the position after "if"
                                if_pos = multiline_condition_buffer.find("if")
                                # Find the first '(' after "if"
                                paren_start = multiline_condition_buffer.find(
                                    "(", if_pos
                                )
                                if paren_start != -1:
                                    # Find the position of this closing ')' in the buffer
                                    closing_paren_pos = (
                                        multiline_condition_buffer.rfind(")")
                                    )
                                    if closing_paren_pos != -1:
                                        condition_part = multiline_condition_buffer[
                                            paren_start + 1 : closing_paren_pos
                                        ]
                                        current_condition = condition_part.strip()
                            collecting_multiline_condition = False
                            multiline_condition_buffer = ""
                            multiline_paren_depth = 0
                            break
                # Continue to next line if still collecting
                if collecting_multiline_condition:
                    continue

            # Track if/else block entry and extract condition
            if stripped.startswith("if ") or stripped.startswith("if("):
                in_if_block = True
                # Extract condition from if statement
                # Handle both "if (condition)" and "if(condition)" formats
                if_match = re.match(r"if\s*\(\s*(.+?)\s*\)", stripped)
                if if_match:
                    condition_candidate = if_match.group(1).strip()
                    # Check if the condition has unbalanced parentheses
                    # This indicates a multi-line condition
                    if condition_candidate.count("(") != condition_candidate.count(")"):
                        # Fall back to multi-line collection
                        collecting_multiline_condition = True
                        multiline_condition_buffer = stripped
                        # Count all opening parentheses in this line
                        multiline_paren_depth = stripped.count("(") - stripped.count(
                            ")"
                        )
                        # Extract partial condition after the first '('
                        paren_start = stripped.find("(")
                        if paren_start != -1:
                            partial_condition = stripped[paren_start + 1 :].strip()
                            current_condition = partial_condition
                    else:
                        current_condition = condition_candidate
                else:
                    # Check if the line has an opening '(' but no closing ')'
                    # This indicates a multi-line condition
                    if "(" in stripped and ")" not in stripped:
                        collecting_multiline_condition = True
                        multiline_condition_buffer = stripped
                        # Count all opening parentheses in this line
                        multiline_paren_depth = stripped.count("(") - stripped.count(
                            ")"
                        )
                        # Extract partial condition after the first '('
                        paren_start = stripped.find("(")
                        if paren_start != -1:
                            partial_condition = stripped[paren_start + 1 :].strip()
                            current_condition = partial_condition
                    else:
                        # Fallback: try to extract everything between "if" and the first '{'
                        if_start = stripped.find("if")
                        brace_pos = stripped.find("{")
                        if brace_pos != -1:
                            condition_part = stripped[if_start + 2 : brace_pos].strip()
                            # Remove leading/trailing parentheses
                            condition_part = (
                                condition_part.lstrip("(").rstrip(")").strip()
                            )
                            current_condition = condition_part
                        else:
                            current_condition = "condition"
            elif stripped.startswith("else if") or stripped.startswith("else if("):
                in_if_block = True
                # Extract condition from else if statement
                elif_match = re.match(r"else\s+if\s*\(\s*(.+?)\s*\)", stripped)
                if elif_match:
                    condition_candidate = elif_match.group(1).strip()
                    # Check if the condition has unbalanced parentheses
                    if condition_candidate.count("(") != condition_candidate.count(")"):
                        # Fall back to multi-line collection
                        collecting_multiline_condition = True
                        multiline_condition_buffer = stripped
                        # Count all opening parentheses in this line
                        multiline_paren_depth = stripped.count("(") - stripped.count(
                            ")"
                        )
                        # Extract partial condition after the first '('
                        paren_start = stripped.find("(")
                        if paren_start != -1:
                            partial_condition = stripped[paren_start + 1 :].strip()
                            current_condition = partial_condition
                    else:
                        current_condition = f"else if {condition_candidate}"
                else:
                    # Check for multi-line else if condition
                    if "(" in stripped and ")" not in stripped:
                        collecting_multiline_condition = True
                        multiline_condition_buffer = stripped
                        # Count all opening parentheses in this line
                        multiline_paren_depth = stripped.count("(") - stripped.count(
                            ")"
                        )
                        # Extract partial condition before the '('
                        paren_start = stripped.find("(")
                        if paren_start != -1:
                            partial_condition = stripped[paren_start + 1 :].strip()
                            current_condition = partial_condition
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
                existing = next(
                    (fc for fc in called_functions if fc.name == function_name), None
                )
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
                            condition=current_condition if is_conditional else None,
                        )
                    )

            # Also extract RTE calls explicitly
            for match in self.rte_call_pattern.finditer(line):
                rte_function = match.group(0).rstrip("(").strip()

                is_conditional = (in_if_block or in_else_block) and brace_depth > 0

                existing = next(
                    (fc for fc in called_functions if fc.name == rte_function), None
                )
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
                            condition=current_condition if is_conditional else None,
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
