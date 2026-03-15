"""
Statistics utilities for processing operations.

This module provides base classes and formatters for collecting
and displaying processing statistics across the codebase.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ProcessingResult:
    """
    Base result for any processing operation.

    Subclasses may add additional fields for their specific needs
    (e.g., ParseResult adds functions, autosar_functions, traditional_functions).
    """
    source_file: Path
    success: bool
    error_message: Optional[str] = None


@dataclass
class ProcessingStatistics:
    """
    Base statistics for batch processing operations.

    Subclasses may add additional fields for their specific needs
    (e.g., ParseStatistics adds autosar_functions, traditional_functions, total_functions).
    """
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    results: List[ProcessingResult] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        processed = self.successful + self.failed
        return (self.successful / processed * 100.0) if processed > 0 else 0.0


class StatisticsFormatter:
    """Format processing statistics for display."""

    @staticmethod
    def format_summary(
        stage_name: str,
        stats: ProcessingStatistics,
        extra_lines: Optional[List[str]] = None,
        show_failures: bool = True
    ) -> str:
        """
        Generate a human-readable summary.

        Args:
            stage_name: Name of the processing stage (e.g., "Preprocessing Stage")
            stats: Statistics object to format
            extra_lines: Optional additional lines for stage-specific metrics
            show_failures: Whether to list failed files

        Returns:
            Formatted summary string
        """
        lines = [
            f"{stage_name}:",
            f"  Files processed: {stats.total_files}",
            f"  Successful:      {stats.successful}",
            f"  Failed:          {stats.failed}",
        ]

        if stats.skipped > 0:
            lines.append(f"  Skipped:         {stats.skipped}")

        if extra_lines:
            lines.extend(extra_lines)

        if show_failures and stats.failed > 0:
            lines.append("  Failed files:")
            for result in stats.results:
                if not result.success:
                    lines.append(
                        f"    - {result.source_file.name}: {result.error_message}"
                    )

        return "\n".join(lines)
