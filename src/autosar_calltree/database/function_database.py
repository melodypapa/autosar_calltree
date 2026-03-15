"""
Function database module.

This module manages the database of all functions found in the codebase,
including caching for performance and lookup methods.

Requirements:
- SWR_CONFIG_00003: Module Configuration Integration
- SWR_CACHE_00001: File-by-File Cache Loading Progress
- SWR_CACHE_00002: Cache Status Indication
- SWR_CACHE_00003: Cache Loading Errors
- SWR_CACHE_00004: Performance Considerations
"""

import hashlib
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import PreprocessorConfig
from ..config.module_config import ModuleConfig
from ..parsers.autosar_parser import AutosarParser
from ..parsers.c_parser import CParser, ParseResult, ParseStatistics
from ..preprocessing import CPPPreprocessor, PreprocessStatistics
from ..utils.statistics import StatisticsFormatter
from .models import FunctionInfo


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    # Define size thresholds
    KB = 1024
    MB = KB * 1024

    if size_bytes >= MB:
        return f"{size_bytes / MB:.2f}M"
    if size_bytes >= KB:
        return f"{size_bytes / KB:.2f}K"
    return str(size_bytes)


@dataclass
class CacheMetadata:
    """Metadata for cache validation."""

    created_at: datetime
    source_directory: str
    file_count: int
    parser_type: str = "pycparser"  # Track which parser created this cache
    file_checksums: Dict[str, str] = field(default_factory=dict)


class FunctionDatabase:
    """
    Database of all functions in the codebase.

    This class scans source files, parses function definitions using both
    AUTOSAR and traditional C parsers, and maintains a searchable database
    with optional caching support.
    """

    def __init__(
        self,
        source_dir: str,
        cache_dir: Optional[str] = None,
        module_config: Optional[ModuleConfig] = None,
        preprocessor_config: Optional[PreprocessorConfig] = None,
        temp_dir: Optional[str] = None,
        keep_temp: bool = False,
    ):
        """
        Initialize the function database.

        Args:
            source_dir: Root directory containing source files
            cache_dir: Directory for cache files (default: .cache in source_dir)
            module_config: Module configuration for SW module mappings
            preprocessor_config: Preprocessor configuration for cpp settings
            temp_dir: Directory for temporary preprocessed files
            keep_temp: Whether to keep temporary files after processing
        """
        self.source_dir = Path(source_dir)

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = self.source_dir / ".cache"

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "function_db.pkl"

        # Database: function_name -> List[FunctionInfo]
        # Multiple entries for functions with same name (static in different files)
        self.functions: Dict[str, List[FunctionInfo]] = {}

        # Qualified function keys: "file::function" -> FunctionInfo
        # Used for resolving static functions
        self.qualified_functions: Dict[str, FunctionInfo] = {}

        # All functions by file
        self.functions_by_file: Dict[str, List[FunctionInfo]] = {}

        # Parsers
        self.autosar_parser = AutosarParser()
        self.c_parser = CParser(preprocessor_config=preprocessor_config)
        self.parser_type = "pycparser"

        # Module configuration
        self.module_config = module_config
        self.module_stats: Dict[str, int] = {}

        # Preprocessor configuration
        self.preprocessor_config = preprocessor_config
        self.temp_dir = Path(temp_dir) if temp_dir else None
        self.keep_temp = keep_temp

        # Statistics
        self.total_files_scanned = 0
        self.total_functions_found = 0
        self.parse_errors: List[str] = []

        # Two-stage pipeline statistics
        self.preprocess_stats: Optional[PreprocessStatistics] = None
        self.parse_stats: Optional[ParseStatistics] = None

    def build_database(
        self,
        use_cache: bool = True,
        rebuild_cache: bool = False,
        verbose: bool = False,
        preprocess_only: bool = False,
    ) -> None:
        """
        Build the function database by scanning all source files.

        Args:
            use_cache: Whether to use cached data if available
            rebuild_cache: Force rebuild of cache even if valid
            verbose: Print progress information
            preprocess_only: Only run preprocessing stage (for debugging)
        """
        if verbose:
            print(f"Scanning source directory: {self.source_dir}")
            print(f"Using parser: {self.parser_type}")

        # Try to load from cache first
        if use_cache and not rebuild_cache:
            if self._load_from_cache(verbose):
                if verbose:
                    print(f"Loaded {self.total_functions_found} functions from cache")
                return

        # Clear existing data
        self.functions.clear()
        self.qualified_functions.clear()
        self.functions_by_file.clear()
        self.parse_errors.clear()
        self.total_files_scanned = 0
        self.total_functions_found = 0

        # Find all C source files
        c_files = list(self.source_dir.rglob("*.c"))

        if verbose:
            print(f"Found {len(c_files)} C source files")

        # Print build progress message before processing files
        print(f"Building function database from {self.source_dir}...")

        # Use two-stage pipeline if preprocessor config is provided and enabled
        if self.preprocessor_config and self.preprocessor_config.enabled:
            self._build_with_two_stage_pipeline(c_files, verbose, preprocess_only)
        else:
            # Fall back to single-stage processing
            self._build_with_single_stage(c_files, verbose)

        # Save to cache
        if use_cache and not preprocess_only:
            self._save_to_cache(verbose)

    def _build_with_two_stage_pipeline(
        self,
        c_files: List[Path],
        verbose: bool,
        preprocess_only: bool,
    ) -> None:
        """
        Build database using two-stage preprocessing and parsing pipeline.

        Args:
            c_files: List of C source files to process
            verbose: Print progress information
            preprocess_only: Only run preprocessing stage
        """
        # Stage 1: Preprocess all files
        preprocessor = CPPPreprocessor(
            config=self.preprocessor_config,
            temp_dir=self.temp_dir,
            keep_temp=self.keep_temp,
        )

        self.preprocess_stats = preprocessor.preprocess_all(c_files, verbose=verbose)

        print(self.c_parser.get_statistics_summary(
            self._convert_prep_stats_to_parse_format(self.preprocess_stats)
        ))

        if preprocess_only:
            print("\nPreprocessing only mode - skipping parsing stage")
            return

        # Build mapping of source files to preprocessed files
        preprocessed_files: Dict[Path, Path] = {}
        for result in self.preprocess_stats.results:
            if result.success and result.output_file:
                preprocessed_files[result.source_file] = result.output_file

        # Stage 2: Parse preprocessed files
        self.parse_stats = self.c_parser.parse_all(
            source_files=c_files,
            verbose=verbose,
            preprocessed_files=preprocessed_files,
        )

        # Add functions from parse results to database
        parse_results: List[ParseResult] = self.parse_stats.results
        for parse_result in parse_results:
            for func_info in parse_result.functions:
                self._add_function(func_info)

            # Track functions by file
            if parse_result.functions:
                file_key = str(parse_result.source_file)
                self.functions_by_file[file_key] = parse_result.functions

        self.total_files_scanned = len(c_files)

        # Clean up temp files if not keeping them
        if not self.keep_temp:
            preprocessor.cleanup()

        # Print summary
        print("\n=== Summary ===")
        print(self._get_pipeline_summary())

    def _build_with_single_stage(
        self,
        c_files: List[Path],
        verbose: bool,
    ) -> None:
        """
        Build database using single-stage processing (fallback).

        Args:
            c_files: List of C source files to process
            verbose: Print progress information
        """
        # Parse each file
        for idx, file_path in enumerate(c_files, 1):
            print(
                f"Processing: [{idx}/{len(c_files)}] {file_path.name} (Size: {_format_file_size(file_path.stat().st_size)})"
            )

            try:
                self._parse_file(file_path)
            except Exception as e:
                error_msg = f"Error parsing {file_path}: {e}"
                self.parse_errors.append(error_msg)
                if verbose:
                    print(f"Warning: {error_msg}")

        self.total_files_scanned = len(c_files)

        if verbose:
            print("\nDatabase built successfully:")
            print(f"  - Files scanned: {self.total_files_scanned}")
            print(f"  - Functions found: {self.total_functions_found}")
            print(f"  - Unique function names: {len(self.functions)}")
            print(f"  - Parse errors: {len(self.parse_errors)}")

    def _convert_prep_stats_to_parse_format(
        self, prep_stats: PreprocessStatistics
    ) -> ParseStatistics:
        """Convert preprocessing stats to parse stats format for display."""
        from ..parsers.c_parser import ParseStatistics

        return ParseStatistics(
            total_files=prep_stats.total_files,
            successful=prep_stats.successful,
            failed=prep_stats.failed,
        )

    def _get_pipeline_summary(self) -> str:
        """Generate summary of two-stage pipeline results."""
        lines = []

        if self.preprocess_stats:
            lines.append(StatisticsFormatter.format_summary(
                "Preprocessing Stage",
                self.preprocess_stats,
                show_failures=False
            ))

        if self.parse_stats:
            lines.append("")
            lines.append("Parsing Stage:")
            lines.append(f"  Files parsed:    {self.parse_stats.total_files}")
            lines.append(f"  Successful:      {self.parse_stats.successful}")
            lines.append(f"  Failed:          {self.parse_stats.failed}")
            lines.append("")
            lines.append("Functions extracted:")
            lines.append(f"  AUTOSAR:       {self.parse_stats.autosar_functions}")
            lines.append(f"  Traditional:   {self.parse_stats.traditional_functions}")
            lines.append(f"  Total:         {self.parse_stats.total_functions}")
            lines.append("")
            lines.append(f"Correctness Ratio: {self.parse_stats.correctness_ratio:.1f}%")

            if self.parse_stats.failed > 0:
                lines.append("")
                lines.append("Failed files:")
                for parse_result in self.parse_stats.results:
                    if not parse_result.success:
                        lines.append(
                            f"  - {parse_result.source_file.name}: {parse_result.error_message}"
                        )

        return "\n".join(lines)

    def _parse_file(self, file_path: Path) -> None:
        """
        Parse a single file and add functions to database.

        Args:
            file_path: Path to source file
        """
        # Use C parser which handles both traditional C and AUTOSAR via pycparser
        functions = self.c_parser.parse_file(file_path)

        # Add functions to database
        for func_info in functions:
            self._add_function(func_info)

        # Track functions by file
        if functions:
            file_key = str(file_path)
            self.functions_by_file[file_key] = functions

    def _add_function(self, func_info: FunctionInfo) -> None:
        """
        Add a function to the database.

        Args:
            func_info: Function information to add
        """
        # Apply module mapping if configuration is available
        if self.module_config:
            func_info.sw_module = self.module_config.get_module_for_file(
                func_info.file_path
            )
            if func_info.sw_module:
                self.module_stats[func_info.sw_module] = (
                    self.module_stats.get(func_info.sw_module, 0) + 1
                )

        # Add to main functions dictionary
        if func_info.name not in self.functions:
            self.functions[func_info.name] = []
        self.functions[func_info.name].append(func_info)

        # Add to qualified functions for static function resolution
        file_stem = Path(func_info.file_path).stem
        qualified_key = f"{file_stem}::{func_info.name}"
        self.qualified_functions[qualified_key] = func_info

        self.total_functions_found += 1

    def lookup_function(
        self, function_name: str, context_file: Optional[str] = None
    ) -> List[FunctionInfo]:
        """
        Lookup a function by name.

        Args:
            function_name: Name of function to lookup
            context_file: File path for context (helps resolve static functions)

        Returns:
            List of FunctionInfo objects matching the name
        """
        # If context file is provided and function is qualified, try qualified lookup
        if context_file and "::" in function_name:
            qualified_info = self.qualified_functions.get(function_name)
            if qualified_info:
                return [qualified_info]

        # Try direct lookup
        if function_name in self.functions:
            results = self.functions[function_name]

            # If multiple definitions, select the best one
            if len(results) > 1:
                best_match = self._select_best_function_match(results, context_file)
                if best_match:
                    return [best_match]

            return results

        return []

    def _select_best_function_match(
        self, candidates: List[FunctionInfo], context_file: Optional[str] = None
    ) -> Optional[FunctionInfo]:
        """
        Select the best function from multiple candidates.

        Implements: SWR_CONFIG_00003 (Module Configuration Integration - Smart Function Selection)

        Selection strategy (applied in order):
        1. Implementations: Prefer functions with calls (actual implementation vs declaration)
        2. File name match: Prefer files matching function name (e.g., COM_* in com.c)
        3. Cross-module: Avoid the calling file for cross-module calls
        4. Module assignment: Prefer functions with assigned modules

        Args:
            candidates: List of FunctionInfo objects to choose from
            context_file: File path of the calling function (optional)

        Returns:
            Best matching FunctionInfo, or None if all are equal
        """
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]

        # Strategy 1: Prefer functions with implementations (have calls)
        implementations = [f for f in candidates if f.calls]
        if len(implementations) == 1:
            return implementations[0]
        if len(implementations) > 1:
            candidates = implementations

        # Strategy 2: Prefer files matching function name pattern
        # e.g., COM_InitCommunication should be in communication.c or com_*.c
        func_name_lower = candidates[0].name.lower()
        for func_info in candidates:
            file_stem = Path(func_info.file_path).stem.lower()
            # Check if function name starts with file name (without underscores)
            if func_name_lower.startswith(file_stem.replace("_", "")):
                if func_info.sw_module and func_info.sw_module != "DemoModule":
                    return func_info

        # Strategy 3: For cross-module calls, avoid the calling file
        if context_file:
            context_stem = Path(context_file).stem
            others = [f for f in candidates if Path(f.file_path).stem != context_stem]
            if len(others) == 1:
                return others[0]
            if len(others) > 1:
                candidates = others

        # Strategy 4: Prefer functions with assigned modules
        with_modules = [f for f in candidates if f.sw_module]
        if len(with_modules) == 1:
            return with_modules[0]
        if len(with_modules) > 1:
            candidates = with_modules

        return candidates[0]

    def get_function_by_qualified_name(
        self, qualified_name: str
    ) -> Optional[FunctionInfo]:
        """
        Get a function by its qualified name (file::function).

        Args:
            qualified_name: Qualified function name

        Returns:
            FunctionInfo or None if not found
        """
        return self.qualified_functions.get(qualified_name)

    def get_all_function_names(self) -> List[str]:
        """
        Get all unique function names in the database.

        Returns:
            Sorted list of function names
        """
        return sorted(self.functions.keys())

    def get_functions_in_file(self, file_path: str) -> List[FunctionInfo]:
        """
        Get all functions defined in a specific file.

        Args:
            file_path: Path to source file

        Returns:
            List of FunctionInfo objects
        """
        return self.functions_by_file.get(file_path, [])

    def search_functions(self, pattern: str) -> List[FunctionInfo]:
        """
        Search for functions matching a pattern.

        Args:
            pattern: Search pattern (substring match)

        Returns:
            List of matching FunctionInfo objects
        """
        results = []
        pattern_lower = pattern.lower()

        for func_name, func_list in self.functions.items():
            if pattern_lower in func_name.lower():
                results.extend(func_list)

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with statistics
        """
        static_count = sum(
            1
            for funcs in self.functions.values()
            for func in funcs
            if func.function_type.name == "STATIC"
        )

        return {
            "parser_type": self.parser_type,
            "total_files_scanned": self.total_files_scanned,
            "total_functions_found": self.total_functions_found,
            "unique_function_names": len(self.functions),
            "static_functions": static_count,
            "parse_errors": len(self.parse_errors),
            "files_with_functions": len(self.functions_by_file),
            "module_stats": self.module_stats.copy(),
        }

    def _compute_file_checksum(self, file_path: Path) -> str:
        """
        Compute checksum of a file.

        Args:
            file_path: Path to file

        Returns:
            MD5 checksum as hex string
        """
        md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    md5.update(chunk)
            return md5.hexdigest()
        except Exception:
            return ""

    def _save_to_cache(self, verbose: bool = False) -> None:
        """
        Save database to cache file.

        Args:
            verbose: Print progress information
        """
        try:
            # Create metadata
            metadata = CacheMetadata(
                created_at=datetime.now(),
                source_directory=str(self.source_dir),
                file_count=self.total_files_scanned,
                parser_type=self.parser_type,
            )

            # Create cache data
            cache_data = {
                "metadata": metadata,
                "functions": self.functions,
                "qualified_functions": self.qualified_functions,
                "functions_by_file": self.functions_by_file,
                "total_files_scanned": self.total_files_scanned,
                "total_functions_found": self.total_functions_found,
                "parse_errors": self.parse_errors,
            }

            # Save to pickle
            with open(self.cache_file, "wb") as f:
                pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)

            if verbose:
                print(f"Cache saved to {self.cache_file}")

        except Exception as e:
            if verbose:
                print(f"Warning: Failed to save cache: {e}")

    def _load_from_cache(self, verbose: bool = False) -> bool:
        """
        Load database from cache file.

        Implements: SWR_CACHE_00001 (File-by-File Cache Loading Progress)
        Implements: SWR_CACHE_00002 (Cache Status Indication)
        Implements: SWR_CACHE_00003 (Cache Loading Errors)

        Args:
            verbose: Print progress information

        Returns:
            True if cache loaded successfully, False otherwise
        """
        if not self.cache_file.exists():
            return False

        try:
            with open(self.cache_file, "rb") as f:
                cache_data = pickle.load(f)

            # Validate metadata
            metadata: CacheMetadata = cache_data.get("metadata")
            if not metadata:
                if verbose:
                    print("Cache invalid: missing metadata")
                return False

            # Check source directory matches
            if metadata.source_directory != str(self.source_dir):
                if verbose:
                    print("Cache invalid: source directory mismatch")
                return False

            # Check parser type matches (invalidate cache if parser changed)
            # This ensures consistency when pycparser is installed/uninstalled
            if (
                hasattr(metadata, "parser_type")
                and metadata.parser_type != self.parser_type
            ):
                if verbose:
                    print(
                        f"Cache invalid: parser type mismatch (cached: {metadata.parser_type}, current: {self.parser_type})"
                    )
                return False

            # Load data
            self.functions = cache_data.get("functions", {})
            self.qualified_functions = cache_data.get("qualified_functions", {})
            self.functions_by_file = cache_data.get("functions_by_file", {})
            self.total_files_scanned = cache_data.get("total_files_scanned", 0)
            self.total_functions_found = cache_data.get("total_functions_found", 0)
            self.parse_errors = cache_data.get("parse_errors", [])

            # Show file-by-file progress in verbose mode
            if verbose:
                print(f"Loading {self.total_files_scanned} files from cache...")
                for idx, (file_path, functions) in enumerate(
                    self.functions_by_file.items(), 1
                ):
                    file_name = Path(file_path).name
                    func_count = len(functions)
                    print(
                        f"  [{idx}/{self.total_files_scanned}] {file_name}: {func_count} functions"
                    )

            return True

        except Exception as e:
            if verbose:
                print(f"Warning: Failed to load cache: {e}")
            return False

    def clear_cache(self) -> None:
        """Delete the cache file if it exists."""
        if self.cache_file.exists():
            self.cache_file.unlink()
