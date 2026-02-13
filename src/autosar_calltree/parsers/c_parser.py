"""
Traditional C function parser.

This module handles parsing of traditional C function declarations and definitions,
extracting function information including parameters, return types, and function calls.
"""

import re
from pathlib import Path
from typing import Callable, List, Optional

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
        from .autosar_parser import AutosarParser

        self.autosar_parser = AutosarParser()

        # Function declaration pattern: [static] [inline] return_type function_name(params)
        # Length limits prevent catastrophic backtracking
        self.function_pattern = re.compile(
            r"^\s*"
            r"(?P<static>static\s+)?"
            r"(?P<inline>inline|__inline__|__inline\s+)?"
            r"(?P<return_type>[\w\s\*]{1,101}?)\s+"
            r"(?P<function_name>[a-zA-Z_][a-zA-Z0-9_]{1,50})\s*"
            r"\((?P<params>[^()]{0,500}(?:\([^()]{0,100}\)[^()]{0,500})*)\)",
            re.MULTILINE,
        )

        # Function body pattern: { ... }
        self.function_body_pattern = re.compile(
            r"\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}", re.DOTALL
        )

        # Function call pattern: identifier(
        self.function_call_pattern = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")

        # RTE call pattern
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
            # Don't skip lines that contain '{' as they might be function definitions
            if not line or "(" not in line or (";" in line and "{" not in line):
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
        self, match: re.Match, content: str, file_path: Path, line_number: Optional[int] = None
    ) -> Optional[FunctionInfo]:
        """
        Parse a regex match into a FunctionInfo object.

        Args:
            match: Regex match object for function declaration
            content: Full file content
            file_path: Path to source file
            line_number: Optional line number (if not provided, calculated from content)

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

        # Determine line number - use provided value or calculate from content
        if line_number is None:
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

        Tracks if/else blocks for conditional calls (SWR_PARSER_00022)
        and for/while loops for loop calls (SWR_PARSER_00023).

        Args:
            function_body: Function body text

        Returns:
            List of FunctionCall objects with conditional/loop status
        """
        called_functions: List[FunctionCall] = []

        # Control flow state
        in_if_block = False
        in_else_block = False
        in_loop_block = False
        current_condition: Optional[str] = None
        current_loop_condition: Optional[str] = None
        brace_depth = 0

        # Multi-line condition state
        multiline_state = self._MultiLineConditionState()

        for line_idx, line in enumerate(function_body.split("\n"), start=1):
            stripped = line.strip()

            # Process multi-line conditions if collecting
            if multiline_state.collecting:
                multiline_state.process_line(stripped)
                if multiline_state.is_complete():
                    current_condition = multiline_state.get_condition()
                    in_if_block = True  # Mark that we're in an if block
                else:
                    continue

            # Process if/elif/else statements
            new_condition = self._process_conditional_statement(stripped, multiline_state)
            if new_condition is not None:
                # Explicit else/elif detected
                in_if_block = True
                current_condition = new_condition
            elif stripped.startswith("else") and not stripped.startswith("else if"):
                in_else_block = True
                current_condition = "else"

            # Process for/while loops
            loop_condition = self._process_loop_statement(stripped)
            if loop_condition is not None:
                in_loop_block = True
                current_loop_condition = loop_condition

            # Track brace depth for nested blocks
            brace_depth += stripped.count("{")
            brace_depth -= stripped.count("}")

            # Extract function calls from this line
            is_conditional = (in_if_block or in_else_block) and brace_depth > 0
            is_loop = in_loop_block and brace_depth > 0

            self._add_calls_from_line(
                line, line_idx, called_functions, is_conditional, current_condition, is_loop, current_loop_condition
            )

            # Reset block state when brace depth returns to 0
            if brace_depth == 0:
                in_if_block = False
                in_else_block = False
                in_loop_block = False
                current_condition = None
                current_loop_condition = None

        return sorted(called_functions, key=lambda fc: fc.name)

    def _add_calls_from_line(
        self,
        line: str,
        line_idx: int,
        called_functions: List[FunctionCall],
        is_conditional: bool,
        condition: Optional[str],
        is_loop: bool,
        loop_condition: Optional[str],
    ) -> None:
        """Extract and add function calls from a single line."""
        # Check all function calls
        for match in self.function_call_pattern.finditer(line):
            function_name = match.group(1)

            if function_name in self.C_KEYWORDS:
                continue
            if function_name in self.AUTOSAR_TYPES:
                continue
            if function_name in self.AUTOSAR_MACROS:
                continue

            self._add_or_update_call(
                called_functions,
                function_name,
                line_idx,
                is_conditional,
                condition,
                is_loop,
                loop_condition,
            )

        # Check RTE calls explicitly
        for match in self.rte_call_pattern.finditer(line):
            rte_function = match.group(0).rstrip("(").strip()

            self._add_or_update_call(
                called_functions,
                rte_function,
                line_idx,
                is_conditional,
                condition,
                is_loop,
                loop_condition,
            )

    def _add_or_update_call(
        self,
        called_functions: List[FunctionCall],
        name: str,
        line_idx: int,
        is_conditional: bool,
        condition: Optional[str],
        is_loop: bool,
        loop_condition: Optional[str],
    ) -> None:
        """Add new call or update existing with conditional/loop info."""
        existing = next((fc for fc in called_functions if fc.name == name), None)

        if existing:
            if is_conditional:
                existing.is_conditional = True
                if condition and not existing.condition:
                    existing.condition = condition
            if is_loop:
                existing.is_loop = True
                if loop_condition and not existing.loop_condition:
                    existing.loop_condition = loop_condition
        else:
            called_functions.append(
                FunctionCall(
                    name=name,
                    is_conditional=is_conditional,
                    condition=condition if is_conditional else None,
                    is_loop=is_loop,
                    loop_condition=loop_condition if is_loop else None,
                    line_number=line_idx,
                )
            )

    def _process_conditional_statement(
        self, line: str, multiline_state: "_MultiLineConditionState"
    ) -> Optional[str]:
        """
        Process if/elif statement and return condition.

        Returns condition string or None if not a conditional statement.
        """
        if not (line.startswith("if ") or line.startswith("if(") or
                line.startswith("else if") or line.startswith("else if(")):
            return None

        # Extract condition from if/elif statement
        if line.startswith("if "):
            pattern = r"if\s*\(\s*(.+?)\s*\)"
        else:  # else if
            pattern = r"else\s+if\s*\(\s*(.+?)\s*\)"

        match = re.match(pattern, line)
        if match:
            condition_candidate = match.group(1).strip()
            # Check for unbalanced parentheses (multi-line condition)
            if condition_candidate.count("(") != condition_candidate.count(")"):
                multiline_state.start_collection(line, self._sanitize_condition)
                return multiline_state.get_condition()
            return self._sanitize_condition(condition_candidate)

        # Fallback: check for multi-line condition
        if "(" in line and ")" not in line:
            multiline_state.start_collection(line, self._sanitize_condition)
            return multiline_state.get_condition()

        # Extract condition between keyword and '{'
        if "{" in line:
            if_pos = line.find("if")
            brace_pos = line.find("{")
            if brace_pos > if_pos:
                condition_part = line[if_pos + 2 : brace_pos].strip()
                condition_part = condition_part.lstrip("(").rstrip(")").strip()
                return self._sanitize_condition(condition_part)

        return self._sanitize_condition("condition")

    def _process_loop_statement(self, line: str) -> Optional[str]:
        """
        Process for/while statement and return condition.

        Returns loop condition string or None if not a loop statement.
        """
        # Check for loop
        if not (line.startswith("for ") or line.startswith("for(") or
                line.startswith("while ") or line.startswith("while(")):
            return None

        # Handle for loop
        if line.startswith("for "):
            match = re.match(r"for\s*\(\s*[^;]*;\s*(.+?)\s*;\s*", line)
            if match:
                return self._sanitize_condition(match.group(1).strip())

            # Fallback: extract middle part
            for_start = line.find("for")
            paren_end = line.find(")")
            if paren_end > for_start:
                loop_part = line[for_start + 3 : paren_end].strip()
                parts = loop_part.split(";")
                if len(parts) >= 2:
                    return self._sanitize_condition(parts[1].strip())

        # Handle while loop
        match = re.match(r"while\s*\(\s*(.+?)\s*\)", line)
        if match:
            return self._sanitize_condition(match.group(1).strip())

        # Fallback for while
        while_start = line.find("while")
        paren_end = line.find(")")
        if paren_end > while_start:
            condition_part = line[while_start + 5 : paren_end].strip()
            return self._sanitize_condition(condition_part.lstrip("(").rstrip(")").strip())

        return self._sanitize_condition("condition")

    class _MultiLineConditionState:
        """State tracker for multi-line condition collection."""

        def __init__(self):
            self.collecting = False
            self.buffer = ""
            self.paren_depth = 0
            self._condition: Optional[str] = None
            self._sanitizer: Optional[Callable[[str], str]] = None

        def start_collection(self, line: str, sanitizer: Callable[[str], str]) -> None:
            """Start collecting a multi-line condition."""
            self.collecting = True
            self.buffer = line
            self.paren_depth = line.count("(") - line.count(")")
            self._sanitizer = sanitizer

        def process_line(self, line: str) -> None:
            """Process a line during multi-line collection."""
            self.buffer += " " + line
            for char in line:
                if char == "(":
                    self.paren_depth += 1
                elif char == ")":
                    self.paren_depth -= 1
                    if self.paren_depth == 0:
                        self._extract_condition()
                        break

        def is_complete(self) -> bool:
            """Check if condition collection is complete."""
            return not self.collecting

        def get_condition(self) -> Optional[str]:
            """Get the collected condition."""
            return self._condition

        def _extract_condition(self) -> None:
            """Extract condition from buffer and stop collecting."""
            if "if" in self.buffer:
                if_pos = self.buffer.find("if")
                paren_start = self.buffer.find("(", if_pos)
                if paren_start != -1:
                    closing_paren_pos = self.buffer.rfind(")")
                    if closing_paren_pos > paren_start:
                        condition_part = self.buffer[paren_start + 1 : closing_paren_pos]
                        if self._sanitizer is not None:
                            self._condition = self._sanitizer(condition_part.strip())
                        else:
                            self._condition = condition_part.strip()

            self.collecting = False

    def _sanitize_condition(self, condition: str) -> str:
        """
        Sanitize condition text for Mermaid output compatibility.

        SWR_PARSER_00024: Condition Text Sanitization for Mermaid Output

        Removes problematic patterns from condition text:
        - Extra closing parentheses that create unbalanced parentheses
        - Preprocessor directives (#if, #endif, #else, #elif, #define)
        - C code statements (braces, semicolons)
        - Incomplete expressions at end of line

        Args:
            condition: Raw condition text extracted from source code

        Returns:
            Sanitized condition text safe for Mermaid rendering
        """
        if not condition:
            return condition

        sanitized = condition

        # 1. Remove preprocessor directives and everything after them
        # Patterns like: "condition) #if (FEATURE" or "condition) #endif"
        preprocessor_patterns = [
            r"\s*#\s*(if|ifdef|ifndef|elif|else|endif|define)\b.*",
            r"\s*#.*",  # Any other preprocessor directive
        ]
        for pattern in preprocessor_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

        # 2. Stop at opening brace - exclude C statements
        # Patterns like: "condition) { statement;" or "condition) { Value = 1; }"
        brace_match = re.search(r"\s*\{", sanitized)
        if brace_match:
            sanitized = sanitized[: brace_match.start()].strip()

        # 3. Remove trailing semicolons
        sanitized = sanitized.rstrip(";").strip()

        # 4. Fix unbalanced parentheses by removing extra closing parens
        # Count opening and closing parentheses
        open_count = sanitized.count("(")
        close_count = sanitized.count(")")

        if close_count > open_count:
            # Remove extra closing parentheses from the end
            chars = list(sanitized)
            chars_to_remove = close_count - open_count
            removed = 0
            for i in range(len(chars) - 1, -1, -1):
                if chars[i] == ")" and removed < chars_to_remove:
                    chars.pop(i)
                    removed += 1
            sanitized = "".join(chars).strip()

        # 5. Remove trailing artifacts like ") {" that might remain
        # This can happen when the condition includes function call syntax
        artifacts_to_remove = [") {", "){", ") {", " )", "( ", "{"]
        for artifact in artifacts_to_remove:
            sanitized = sanitized.rstrip(artifact).strip()

        # 6. Clean up any remaining whitespace issues
        sanitized = re.sub(r"\s+", " ", sanitized)  # Collapse multiple spaces
        sanitized = sanitized.strip()

        # 7. If after sanitization the condition is empty or too short,
        # provide a fallback
        if len(sanitized) < 3:
            return "condition"

        return sanitized

    def parse_function_declaration(
        self, declaration: str, file_path: Path = Path("unknown"), line_number: int = 1
    ) -> Optional[FunctionInfo]:
        """
        Parse a single function declaration string.

        Args:
            declaration: Function declaration as a string
            file_path: Path to the source file (for error reporting)
            line_number: Line number of the declaration

        Returns:
            FunctionInfo object or None if parsing fails
        """
        match = self.function_pattern.search(declaration)
        if not match:
            return None

        return self._parse_function_match(match, declaration, file_path, line_number)
