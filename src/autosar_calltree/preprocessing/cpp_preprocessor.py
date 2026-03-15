"""
CPP Preprocessor for C source files.

This module provides functionality for running the C preprocessor (cpp)
on source files before parsing, with metrics collection and error tracking.

Requirements:
- SWR_PREPROCESS_00001: Two-stage preprocessing pipeline
- SWR_PREPROCESS_00002: Preprocessing metrics collection
- SWR_PREPROCESS_00003: Error visibility and tracking
- SWR_PREPROCESS_00004: CPP path resolution
- SWR_PREPROCESS_00005: Windows CPP support
- SWR_PREPROCESS_00006: Batch preprocessing with progress
- SWR_PREPROCESS_00007: Temporary file management
- SWR_PREPROCESS_00008: Preprocessor configuration integration
"""

import platform
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from ..config import PreprocessorConfig
from ..utils.statistics import (
    ProcessingResult,
    ProcessingStatistics,
    StatisticsFormatter,
)


@dataclass
class PreprocessResult(ProcessingResult):
    """
    Result of preprocessing a single file.

    Implements: SWR_PREPROCESS_00003 (Error visibility and tracking)
    """

    output_file: Optional[Path] = None  # Path in temp folder, None if failed
    error_type: Optional[str] = None  # 'cpp_not_found', 'cpp_error', 'timeout'


@dataclass
class PreprocessStatistics(ProcessingStatistics):
    """
    Statistics for preprocessing stage.

    Implements: SWR_PREPROCESS_00002 (Preprocessing metrics collection)
    """

    results: List[PreprocessResult] = field(default_factory=list)  # type: ignore[assignment]


class CPPPreprocessor:
    """
    Runs cpp preprocessor on all source files.

    This class handles:
    - Finding cpp executable (with Windows support)
    - Running preprocessor with configured options
    - Collecting metrics and errors
    - Managing temporary output files

    Implements: SWR_PREPROCESS_00001 (Two-stage preprocessing pipeline)
    """

    # Default CPP paths to search
    DEFAULT_CPP_PATHS = {
        "Windows": [
            "./cpp/cpp.exe",
            "./tools/cpp.exe",
            "./cpp.exe",
            # MinGW/MSYS2 paths (check environment variable)
        ],
        "Linux": ["/usr/bin/cpp", "/usr/local/bin/cpp"],
        "Darwin": ["/usr/bin/cpp", "/usr/local/bin/cpp"],
    }

    def __init__(
        self,
        config: Optional[PreprocessorConfig] = None,
        temp_dir: Optional[Path] = None,
        keep_temp: bool = False,
    ):
        """
        Initialize the CPP preprocessor.

        Args:
            config: Preprocessor configuration (optional)
            temp_dir: Directory for temporary files (default: system temp)
            keep_temp: Whether to keep temp files after processing
        """
        self.config = config
        self.temp_dir = temp_dir
        self.keep_temp = keep_temp
        self._cpp_path: Optional[str] = None
        self._temp_dir_created: Optional[Path] = None

    def _get_cpp_path(self) -> Optional[str]:
        """
        Find the cpp executable path.

        Implements: SWR_PREPROCESS_00004 (CPP path resolution)
        Implements: SWR_PREPROCESS_00005 (Windows CPP support)

        Resolution order:
        1. Use command from config if provided
        2. Check platform-specific default paths
        3. Try to find in PATH

        Returns:
            Path to cpp executable, or None if not found
        """
        if self._cpp_path is not None:
            return self._cpp_path

        # If config specifies a command, use it
        if self.config and self.config.command:
            # Check if it's an absolute path or resolves to one
            if Path(self.config.command).exists():
                self._cpp_path = self.config.command
                return self._cpp_path

            # Check if it's in PATH
            which_result = shutil.which(self.config.command)
            if which_result:
                self._cpp_path = which_result
                return self._cpp_path

        # Get platform-specific default paths
        system = platform.system()
        default_paths = self.DEFAULT_CPP_PATHS.get(system, [])

        # Add MinGW path from environment variable on Windows
        if system == "Windows":
            import os

            mingw_home = os.environ.get("MINGW_HOME", "")
            if mingw_home:
                default_paths = [f"{mingw_home}/bin/cpp.exe"] + default_paths

        # Check default paths
        for path in default_paths:
            expanded = Path(path).expanduser()
            if not expanded.is_absolute():
                # Try relative to current working directory
                expanded = Path.cwd() / path

            if expanded.exists():
                self._cpp_path = str(expanded.resolve())
                return self._cpp_path

        # Try 'gcc -E' as fallback
        gcc_path = shutil.which("gcc")
        if gcc_path:
            self._cpp_path = gcc_path
            return self._cpp_path

        return None

    def _get_temp_dir(self) -> Path:
        """
        Get or create the temporary directory.

        Returns:
            Path to temporary directory
        """
        if self.temp_dir:
            temp = Path(self.temp_dir)
            temp.mkdir(parents=True, exist_ok=True)
            return temp

        if self._temp_dir_created is None:
            # Create a temp directory for this session
            self._temp_dir_created = Path(tempfile.mkdtemp(prefix="autosar_prep_"))

        return self._temp_dir_created

    def cleanup(self) -> None:
        """
        Clean up temporary files if not keeping them.

        Implements: SWR_PREPROCESS_00007 (Temporary file management)
        """
        if not self.keep_temp and self._temp_dir_created:
            import shutil

            try:
                shutil.rmtree(self._temp_dir_created)
            except Exception:
                pass
            self._temp_dir_created = None

    def preprocess_all(
        self, source_files: List[Path], verbose: bool = True
    ) -> PreprocessStatistics:
        """
        Preprocess all files with progress display.

        Implements: SWR_PREPROCESS_00006 (Batch preprocessing with progress)

        Args:
            source_files: List of source files to preprocess
            verbose: Print progress information

        Returns:
            PreprocessStatistics with results
        """
        stats = PreprocessStatistics(total_files=len(source_files))

        if verbose:
            print("=== Preprocessing Stage ===")

        for idx, source_file in enumerate(source_files, 1):
            if verbose:
                print(f"[{idx}/{len(source_files)}] {source_file.name:<30} ", end="")

            result = self.preprocess_file(source_file)
            stats.results.append(result)

            if result.success:
                stats.successful += 1
                if verbose:
                    print("OK")
            else:
                stats.failed += 1
                if verbose:
                    print(f"FAILED ({result.error_type})")
                    if result.error_message:
                        print(f"    Error: {result.error_message}")

        return stats

    def preprocess_file(self, source_file: Path) -> PreprocessResult:
        """
        Preprocess a single file.

        Args:
            source_file: Path to source file

        Returns:
            PreprocessResult with outcome
        """
        # Find cpp executable
        cpp_path = self._get_cpp_path()
        if not cpp_path:
            return PreprocessResult(
                source_file=source_file,
                output_file=None,
                success=False,
                error_message="cpp executable not found",
                error_type="cpp_not_found",
            )

        # Get temp directory
        temp_dir = self._get_temp_dir()

        # Determine output file path
        output_file = temp_dir / f"{source_file.stem}.i"

        try:
            # Build cpp command
            cmd = self._build_command(cpp_path, source_file, output_file)

            # Run preprocessor
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                encoding="utf-8",
                errors="ignore",
            )

            if result.returncode != 0:
                # cpp failed
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                # Extract just the first line of error for brevity
                first_error = error_msg.split("\n")[0] if error_msg else "Unknown error"

                return PreprocessResult(
                    source_file=source_file,
                    output_file=None,
                    success=False,
                    error_message=first_error,
                    error_type="cpp_error",
                )

            # Check output file exists and has content
            if not output_file.exists():
                return PreprocessResult(
                    source_file=source_file,
                    output_file=None,
                    success=False,
                    error_message="Output file not created",
                    error_type="cpp_error",
                )

            if output_file.stat().st_size == 0:
                return PreprocessResult(
                    source_file=source_file,
                    output_file=None,
                    success=False,
                    error_message="Output file is empty",
                    error_type="cpp_error",
                )

            return PreprocessResult(
                source_file=source_file,
                output_file=output_file,
                success=True,
            )

        except subprocess.TimeoutExpired:
            return PreprocessResult(
                source_file=source_file,
                output_file=None,
                success=False,
                error_message="Preprocessing timed out",
                error_type="timeout",
            )
        except FileNotFoundError:
            return PreprocessResult(
                source_file=source_file,
                output_file=None,
                success=False,
                error_message=f"cpp not found at {cpp_path}",
                error_type="cpp_not_found",
            )
        except Exception as e:
            return PreprocessResult(
                source_file=source_file,
                output_file=None,
                success=False,
                error_message=str(e),
                error_type="cpp_error",
            )

    def _build_command(
        self, cpp_path: str, source_file: Path, output_file: Path
    ) -> List[str]:
        """
        Build the cpp command.

        Implements: SWR_PREPROCESS_00008 (Preprocessor configuration integration)

        Args:
            cpp_path: Path to cpp executable
            source_file: Source file to preprocess
            output_file: Output file path

        Returns:
            List of command arguments
        """
        cmd = [cpp_path, "-E"]  # -E for preprocessing only

        # Add -o for output file (if using gcc/clang)
        if "gcc" in cpp_path or "clang" in cpp_path or cpp_path.endswith("cc1"):
            cmd.extend(["-o", str(output_file)])

        # Add include directories from config
        if self.config:
            for inc_dir in self.config.include_dirs:
                # Resolve relative paths
                inc_path = Path(inc_dir)
                if not inc_path.is_absolute():
                    inc_path = Path.cwd() / inc_dir
                cmd.extend(["-I", str(inc_path)])

            # Add extra flags
            cmd.extend(self.config.extra_flags)

        # Add input file
        cmd.append(str(source_file))

        # For cpp (not gcc), redirect output
        if "gcc" not in cpp_path and "clang" not in cpp_path:
            # Pure cpp outputs to stdout, we need to handle this differently
            # Remove the -o flag since cpp doesn't support it the same way
            if "-o" in cmd:
                idx = cmd.index("-o")
                cmd = cmd[:idx] + cmd[idx + 2 :]

        return cmd

    def get_statistics_summary(self, stats: PreprocessStatistics) -> str:
        """
        Generate a human-readable summary of preprocessing statistics.

        Args:
            stats: PreprocessStatistics to summarize

        Returns:
            Formatted summary string
        """
        return StatisticsFormatter.format_summary("Preprocessing Stage", stats)
