"""
AUTOSAR-specific function parser.

Parses AUTOSAR macro-based function declarations like:
- FUNC(rettype, memclass) function_name(...)
- FUNC_P2VAR(rettype, ptrclass, memclass) function_name(...)
- STATIC FUNC(...) ...
"""

import re
from pathlib import Path
from typing import Optional, Tuple, List
from ..database.models import FunctionInfo, FunctionType, Parameter


class AutosarParser:
    """Parse AUTOSAR-specific function declarations."""

    # AUTOSAR function patterns
    FUNC_PATTERN = re.compile(
        r"(STATIC\s+)?FUNC\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)\s+(\w+)\s*\(", re.MULTILINE
    )

    FUNC_P2VAR_PATTERN = re.compile(
        r"(STATIC\s+)?FUNC_P2VAR\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)\s+(\w+)\s*\(",
        re.MULTILINE,
    )

    FUNC_P2CONST_PATTERN = re.compile(
        r"(STATIC\s+)?FUNC_P2CONST\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)\s+(\w+)\s*\(",
        re.MULTILINE,
    )

    # Parameter patterns
    VAR_PATTERN = re.compile(r"VAR\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)\s+(\w+)")
    P2VAR_PATTERN = re.compile(
        r"P2VAR\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)\s+(\w+)"
    )
    P2CONST_PATTERN = re.compile(
        r"P2CONST\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)\s+(\w+)"
    )
    CONST_PATTERN = re.compile(r"CONST\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)\s+(\w+)")

    def parse_function_declaration(
        self, line: str, file_path: Path, line_number: int
    ) -> Optional[FunctionInfo]:
        """
        Parse AUTOSAR function declaration.

        Args:
            line: Line of code to parse
            file_path: Path to source file
            line_number: Line number in file

        Returns:
            FunctionInfo object or None if not a function declaration
        """
        # Try FUNC pattern
        match = self.FUNC_PATTERN.search(line)
        if match:
            is_static_str, return_type, memory_class, func_name = match.groups()
            return FunctionInfo(
                name=func_name,
                return_type=return_type.strip(),
                file_path=file_path,
                line_number=line_number,
                is_static=bool(is_static_str),
                function_type=FunctionType.AUTOSAR_FUNC,
                memory_class=memory_class.strip(),
                macro_type="FUNC",
            )

        # Try FUNC_P2VAR pattern
        match = self.FUNC_P2VAR_PATTERN.search(line)
        if match:
            is_static_str, return_type, ptr_class, memory_class, func_name = (
                match.groups()
            )
            return FunctionInfo(
                name=func_name,
                return_type=f"{return_type.strip()}*",
                file_path=file_path,
                line_number=line_number,
                is_static=bool(is_static_str),
                function_type=FunctionType.AUTOSAR_FUNC_P2VAR,
                memory_class=memory_class.strip(),
                macro_type="FUNC_P2VAR",
            )

        # Try FUNC_P2CONST pattern
        match = self.FUNC_P2CONST_PATTERN.search(line)
        if match:
            is_static_str, return_type, ptr_class, memory_class, func_name = (
                match.groups()
            )
            return FunctionInfo(
                name=func_name,
                return_type=f"const {return_type.strip()}*",
                file_path=file_path,
                line_number=line_number,
                is_static=bool(is_static_str),
                function_type=FunctionType.AUTOSAR_FUNC_P2CONST,
                memory_class=memory_class.strip(),
                macro_type="FUNC_P2CONST",
            )

        return None

    def parse_parameters(self, param_string: str) -> List[Parameter]:
        """
        Parse function parameters (both AUTOSAR and traditional).

        Args:
            param_string: Parameter list string (inside parentheses)

        Returns:
            List of Parameter objects
        """
        if not param_string or param_string.strip() in ("void", ""):
            return []

        parameters = []

        # Split by comma, but respect nested parentheses
        params = self._split_parameters(param_string)

        for param in params:
            param = param.strip()
            if not param or param == "void":
                continue

            parsed_param = self._parse_single_parameter(param)
            if parsed_param:
                parameters.append(parsed_param)

        return parameters

    def _parse_single_parameter(self, param_str: str) -> Optional[Parameter]:
        """Parse a single parameter."""
        # Try VAR pattern
        match = self.VAR_PATTERN.search(param_str)
        if match:
            param_type, memory_class, name = match.groups()
            return Parameter(
                name=name,
                param_type=param_type.strip(),
                is_pointer=False,
                is_const=False,
                memory_class=memory_class.strip(),
            )

        # Try P2VAR pattern
        match = self.P2VAR_PATTERN.search(param_str)
        if match:
            param_type, ptr_class, memory_class, name = match.groups()
            return Parameter(
                name=name,
                param_type=param_type.strip(),
                is_pointer=True,
                is_const=False,
                memory_class=memory_class.strip(),
            )

        # Try P2CONST pattern
        match = self.P2CONST_PATTERN.search(param_str)
        if match:
            param_type, ptr_class, memory_class, name = match.groups()
            return Parameter(
                name=name,
                param_type=param_type.strip(),
                is_pointer=True,
                is_const=True,
                memory_class=memory_class.strip(),
            )

        # Try CONST pattern
        match = self.CONST_PATTERN.search(param_str)
        if match:
            param_type, memory_class, name = match.groups()
            return Parameter(
                name=name,
                param_type=param_type.strip(),
                is_pointer=False,
                is_const=True,
                memory_class=memory_class.strip(),
            )

        # Fallback: Traditional C parameter
        return self._parse_traditional_parameter(param_str)

    def _parse_traditional_parameter(self, param_str: str) -> Optional[Parameter]:
        """Parse traditional C parameter format."""
        param_str = param_str.strip()

        # Check for const
        is_const = "const" in param_str
        if is_const:
            param_str = param_str.replace("const", "").strip()

        # Check for pointer
        is_pointer = "*" in param_str
        if is_pointer:
            param_str = param_str.replace("*", "").strip()

        # Split type and name
        parts = param_str.rsplit(None, 1)
        if len(parts) == 2:
            param_type, name = parts
            return Parameter(
                name=name,
                param_type=param_type.strip(),
                is_pointer=is_pointer,
                is_const=is_const,
            )
        elif len(parts) == 1:
            # Only type, no name (parameter name omitted)
            return Parameter(
                name="",
                param_type=parts[0].strip(),
                is_pointer=is_pointer,
                is_const=is_const,
            )

        return None

    def _split_parameters(self, param_string: str) -> List[str]:
        """Split parameters by comma, respecting nested parentheses."""
        parameters = []
        current_param = []
        paren_depth = 0

        for char in param_string:
            if char == "(":
                paren_depth += 1
                current_param.append(char)
            elif char == ")":
                paren_depth -= 1
                current_param.append(char)
            elif char == "," and paren_depth == 0:
                parameters.append("".join(current_param))
                current_param = []
            else:
                current_param.append(char)

        if current_param:
            parameters.append("".join(current_param))

        return parameters

    def is_autosar_function(self, line: str) -> bool:
        """Check if line contains AUTOSAR function declaration."""
        return bool(
            self.FUNC_PATTERN.search(line)
            or self.FUNC_P2VAR_PATTERN.search(line)
            or self.FUNC_P2CONST_PATTERN.search(line)
        )
