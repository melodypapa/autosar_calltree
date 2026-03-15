"""
C function parser using pycparser.

This module uses pycparser for reliable parsing of standard C code.
AUTOSAR macros are handled via preprocessing before parsing.

Example usage:
    from autosar_calltree.parsers.c_parser import CParser
    from autosar_calltree.config import PreprocessorConfig

    parser = CParser(preprocessor_config=PreprocessorConfig())
    functions = parser.parse_file(Path("example.c"))
"""

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from pycparser import c_parser

from ..config import PreprocessorConfig
from ..database.models import FunctionCall, FunctionInfo, FunctionType
from .function_visitor import FunctionVisitor


@dataclass
class ParseResult:
    """Result of parsing a single file."""

    source_file: Path
    preprocessed_file: Optional[Path]
    functions: List[FunctionInfo] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None
    autosar_functions: int = 0
    traditional_functions: int = 0


@dataclass
class ParseStatistics:
    """Statistics for parsing stage."""

    total_files: int = 0
    successful: int = 0
    failed: int = 0
    autosar_functions: int = 0
    traditional_functions: int = 0
    total_functions: int = 0
    results: List[ParseResult] = field(default_factory=list)

    @property
    def correctness_ratio(self) -> float:
        """Calculate correctness ratio as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.successful / self.total_files) * 100.0


class CParser:
    """C parser using pycparser library."""

    # Re-export constants for backward compatibility
    C_KEYWORDS = FunctionVisitor.C_KEYWORDS
    AUTOSAR_MACROS = FunctionVisitor.AUTOSAR_MACROS
    AUTOSAR_TYPES = FunctionVisitor.AUTOSAR_TYPES

    def __init__(self, preprocessor_config: Optional[PreprocessorConfig] = None):
        """
        Initialize the pycparser-based C parser.

        Args:
            preprocessor_config: Optional PreprocessorConfig for cpp settings.
                                 If None, uses regex-based preprocessing only.
        """
        self.parser = c_parser.CParser()
        self.preprocessor_config = preprocessor_config

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
                                function_body = (
                                    self._extract_function_body_from_content(
                                        content, body_start
                                    )
                                )
                                if function_body:
                                    called_functions = (
                                        self._extract_function_calls_from_body(
                                            function_body
                                        )
                                    )
                                    autosar_func.calls = called_functions
                            all_functions.append(autosar_func)

        # Then, parse traditional C functions using pycparser
        # Remove AUTOSAR function declarations before preprocessing
        # so they don't get converted and parsed as traditional C functions
        content_for_traditional_c = self._remove_autosar_functions(content)

        # Use cpp preprocessor if config is provided and enabled
        if self.preprocessor_config and self.preprocessor_config.enabled:
            preprocessed = self._preprocess_with_cpp(content_for_traditional_c, file_path)
        else:
            preprocessed = self._preprocess_content(content_for_traditional_c)

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

    def _preprocess_with_cpp(self, content: str, file_path: Path) -> str:
        """
        Preprocess C source code using the C preprocessor (cpp).

        This method runs the source file through gcc/clang's preprocessor
        to handle #include, #ifdef, and standard C macros. The result
        is then further processed by _preprocess_content() to handle
        AUTOSAR-specific macros.

        Args:
            content: Original C source code (used as fallback)
            file_path: Path to the C source file

        Returns:
            Preprocessed C code from cpp, or regex-preprocessed content on error
        """
        if not self.preprocessor_config:
            return self._preprocess_content(content)

        try:
            # Build cpp command
            cmd = [self.preprocessor_config.command, "-E"]

            # Add include directories
            for inc_dir in self.preprocessor_config.include_dirs:
                cmd.extend(["-I", inc_dir])

            # Add extra flags
            cmd.extend(self.preprocessor_config.extra_flags)

            # Add input file
            cmd.append(str(file_path))

            # Run preprocessor
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="ignore",
            )

            # The cpp output still needs AUTOSAR macro handling
            cpp_output = result.stdout
            return self._preprocess_content(cpp_output)

        except subprocess.CalledProcessError as e:
            # Log error and fallback to regex preprocessing
            # This can happen if cpp is not installed or file has issues
            print(f"Warning: cpp preprocessing failed: {e.stderr}")
            return self._preprocess_content(content)
        except FileNotFoundError:
            # cpp command not found, fallback to regex preprocessing
            print(
                f"Warning: {self.preprocessor_config.command} not found. "
                "Using regex preprocessing."
            )
            return self._preprocess_content(content)
        except Exception:
            # Any other error, fallback to regex preprocessing
            return self._preprocess_content(content)

    def _preprocess_content(self, content: str) -> str:
        """
        Preprocess C source code for pycparser.

        This handles:
        - AUTOSAR macros (FUNC, VAR, P2VAR, etc.) that pycparser can't handle
        - AUTOSAR types (uint8, uint16, etc.) that need typedefs
        - Preprocessor directives
        - Other issues that would confuse pycparser

        Args:
            content: Original C source code

        Returns:
            Preprocessed C code suitable for pycparser
        """
        preprocessed = content

        # Step 1: Remove ALL comments FIRST (before any macro processing)
        # This prevents comment-like content in strings from being affected
        preprocessed = self._remove_comments(preprocessed)

        # Step 2: Add typedefs for AUTOSAR types
        autosar_typedefs = """typedef unsigned char uint8;
typedef unsigned short uint16;
typedef unsigned int uint32;
typedef unsigned long long uint64;
typedef signed char sint8;
typedef short sint16;
typedef int sint32;
typedef long long sint64;
typedef unsigned char uchar;
typedef unsigned short ushort;
typedef unsigned int uint;
typedef unsigned long ulong;
"""
        preprocessed = autosar_typedefs + preprocessed

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
        preprocessed = re.sub(
            r"^#\s*(pragma|line|error|warning).*$", "", preprocessed, flags=re.MULTILINE
        )

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

    def _extract_function_calls_from_body(
        self, function_body: str
    ) -> List[FunctionCall]:
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

    def _remove_autosar_functions(self, content: str) -> str:
        """
        Remove AUTOSAR function declarations from content.

        This prevents AUTOSAR macros from being converted to traditional C
        and then parsed as traditional C functions.

        Args:
            content: Original C source code

        Returns:
            Content with AUTOSAR function declarations removed
        """
        lines = content.split("\n")
        filtered_lines = []
        in_autosar_func = False

        for line in lines:
            stripped = line.strip()

            # Check if this line starts an AUTOSAR function declaration
            # Pattern: FUNC(...) or FUNC_P2VAR(...) etc.
            if re.match(r"^\s*FUNC(_P2\w+)?\s*\(", stripped):
                # Check if this is a full declaration (ends with ; or {)
                # or a multi-line declaration
                if ";" in stripped or "{" in stripped:
                    # Single-line declaration - skip it
                    in_autosar_func = False
                    # If it ends with {, we need to skip the body too
                    if "{" in stripped:
                        # Keep the body (everything after {)
                        open_brace_pos = stripped.find("{")
                        if open_brace_pos != -1:
                            filtered_lines.append(stripped[open_brace_pos:])
                else:
                    # Multi-line declaration start
                    in_autosar_func = True
            elif in_autosar_func:
                # We're in a multi-line AUTOSAR declaration
                if ";" in stripped or "{" in stripped:
                    # End of declaration
                    in_autosar_func = False
                    # If it ends with {, we need to keep the body
                    if "{" in stripped:
                        open_brace_pos = stripped.find("{")
                        if open_brace_pos != -1:
                            filtered_lines.append(stripped[open_brace_pos:])
                # Skip the declaration lines
            else:
                # Not an AUTOSAR function line
                filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def _remove_comments(self, content: str) -> str:
        """
        Remove all C-style comments while preserving string/char literals.

        Handles both comment formats:
        - Block comments: /* ... */ (can span multiple lines)
        - Line comments: // ... (extends to end of line)

        Args:
            content: C source code

        Returns:
            Source with comments removed, string/char literals preserved
        """
        # Placeholders for protected content
        string_placeholders: Dict[str, str] = {}
        char_placeholders: Dict[str, str] = {}

        def replace_string(match: re.Match) -> str:
            """Replace string literal with placeholder."""
            key = f"__STR_{len(string_placeholders)}__"
            string_placeholders[key] = match.group(0)
            return key

        def replace_char(match: re.Match) -> str:
            """Replace character literal with placeholder."""
            key = f"__CHR_{len(char_placeholders)}__"
            char_placeholders[key] = match.group(0)
            return key

        # Step 1: Protect string literals (handles escaped quotes)
        # Pattern: " followed by (non-"-or-backslash OR escaped-char)* followed by "
        content = re.sub(r'"(?:[^"\\]|\\.)*"', replace_string, content)

        # Step 2: Protect character literals (handles escaped chars)
        # Pattern: ' followed by (non-'-or-backslash OR escaped-char)* followed by '
        content = re.sub(r"'(?:[^'\\]|\\.)*'", replace_char, content)

        # Step 3: Remove block comments /* ... */
        # Use DOTALL so . matches newlines (multi-line comments)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        # Step 4: Remove line comments // ... (to end of line)
        # MULTILINE makes $ match at end of each line
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)

        # Step 5: Restore string literals
        for key, value in string_placeholders.items():
            content = content.replace(key, value)

        # Step 6: Restore character literals
        for key, value in char_placeholders.items():
            content = content.replace(key, value)

        return content

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
            if re.match(
                r"^[a-zA-Z_][a-zA-Z0-9_*\s]+\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(", line
            ):
                if not line.startswith("FUNC"):
                    return True

        return False

    def parse_all(
        self,
        source_files: List[Path],
        verbose: bool = True,
        preprocessed_files: Optional[Dict[Path, Path]] = None,
    ) -> ParseStatistics:
        """
        Parse multiple files with statistics collection.

        Args:
            source_files: List of source files to parse
            verbose: Print progress information
            preprocessed_files: Optional mapping of source_file -> preprocessed_file

        Returns:
            ParseStatistics with results
        """
        stats = ParseStatistics(total_files=len(source_files))

        if verbose:
            print("=== Parsing Stage ===")

        for idx, source_file in enumerate(source_files, 1):
            if verbose:
                print(f"[{idx}/{len(source_files)}] {source_file.name:<30} ", end="")

            # Get preprocessed file path if available
            preprocessed_file = None
            if preprocessed_files:
                preprocessed_file = preprocessed_files.get(source_file)

            result = self.parse_file_with_stats(source_file, preprocessed_file)
            stats.results.append(result)

            if result.success:
                stats.successful += 1
                stats.autosar_functions += result.autosar_functions
                stats.traditional_functions += result.traditional_functions
                stats.total_functions += len(result.functions)
                if verbose:
                    func_count = len(result.functions)
                    print(f"OK ({func_count} functions)")
            else:
                stats.failed += 1
                if verbose:
                    print("FAILED")
                    if result.error_message:
                        print(f"    Error: {result.error_message}")

        return stats

    def parse_file_with_stats(
        self,
        source_file: Path,
        preprocessed_file: Optional[Path] = None,
    ) -> ParseResult:
        """
        Parse a single file with statistics collection.

        Args:
            source_file: Path to source file
            preprocessed_file: Optional path to preprocessed file

        Returns:
            ParseResult with outcome and functions
        """
        try:
            # If preprocessed file provided, use it
            if preprocessed_file and preprocessed_file.exists():
                functions = self._parse_preprocessed_file(source_file, preprocessed_file)
            else:
                # Fall back to regular parsing
                functions = self.parse_file(source_file)

            # Count function types
            autosar_count = sum(
                1 for f in functions
                if f.function_type in (FunctionType.AUTOSAR_FUNC, FunctionType.AUTOSAR_FUNC_P2VAR, FunctionType.AUTOSAR_FUNC_P2CONST)
            )
            traditional_count = len(functions) - autosar_count

            return ParseResult(
                source_file=source_file,
                preprocessed_file=preprocessed_file,
                functions=functions,
                success=True,
                autosar_functions=autosar_count,
                traditional_functions=traditional_count,
            )

        except Exception as e:
            return ParseResult(
                source_file=source_file,
                preprocessed_file=preprocessed_file,
                functions=[],
                success=False,
                error_message=str(e),
            )

    def _parse_preprocessed_file(
        self,
        source_file: Path,
        preprocessed_file: Path,
    ) -> List[FunctionInfo]:
        """
        Parse a preprocessed file.

        This method expects the file to already be preprocessed by cpp.
        It applies regex preprocessing for any remaining AUTOSAR macros.

        Args:
            source_file: Original source file (for file path in FunctionInfo)
            preprocessed_file: Path to preprocessed .i file

        Returns:
            List of FunctionInfo objects
        """
        try:
            content = preprocessed_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []

        all_functions = []
        seen_functions = set()

        # First, parse AUTOSAR functions if any
        if "FUNC(" in content:
            from .autosar_parser import AutosarParser

            autosar_parser = AutosarParser()
            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                if "FUNC" in line and "(" in line:
                    autosar_func = autosar_parser.parse_function_declaration(
                        line, source_file, line_num
                    )
                    if autosar_func:
                        key = (autosar_func.name, autosar_func.line_number)
                        if key not in seen_functions:
                            seen_functions.add(key)
                            all_functions.append(autosar_func)

        # Remove AUTOSAR function declarations before traditional parsing
        content_for_traditional_c = self._remove_autosar_functions(content)

        # Apply regex preprocessing for any remaining AUTOSAR macros
        preprocessed = self._preprocess_content(content_for_traditional_c)

        # Check if file contains any traditional C functions
        if self._has_traditional_c_functions(preprocessed):
            try:
                ast = self.parser.parse(preprocessed, filename=str(source_file))

                visitor = FunctionVisitor(source_file, content)
                visitor.visit(ast)

                for func in visitor.functions:
                    key = (func.name, func.line_number)
                    if key not in seen_functions:
                        seen_functions.add(key)
                        all_functions.append(func)

            except Exception:
                pass

        return all_functions

    def get_statistics_summary(self, stats: ParseStatistics) -> str:
        """
        Generate a human-readable summary of parsing statistics.

        Args:
            stats: ParseStatistics to summarize

        Returns:
            Formatted summary string
        """
        lines = [
            "Parsing Stage:",
            f"  Files parsed:    {stats.total_files}",
            f"  Successful:      {stats.successful}",
            f"  Failed:          {stats.failed}",
            "",
            "Functions extracted:",
            f"  AUTOSAR:       {stats.autosar_functions}",
            f"  Traditional:   {stats.traditional_functions}",
            f"  Total:         {stats.total_functions}",
            "",
            f"Correctness Ratio: {stats.correctness_ratio:.1f}%",
        ]

        if stats.failed > 0:
            lines.append("")
            lines.append("Failed files:")
            for result in stats.results:
                if not result.success:
                    lines.append(
                        f"  - {result.source_file.name}: {result.error_message}"
                    )

        return "\n".join(lines)
