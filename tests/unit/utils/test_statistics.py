"""Tests for statistics utilities."""

from pathlib import Path

from autosar_calltree.utils.statistics import (
    ProcessingResult,
    ProcessingStatistics,
    StatisticsFormatter,
)


class TestProcessingResult:
    """Tests for ProcessingResult dataclass."""

    def test_required_fields(self):
        """Should have source_file and success as required."""
        result = ProcessingResult(source_file=Path("test.c"), success=True)
        assert result.source_file == Path("test.c")
        assert result.success is True

    def test_optional_error_message(self):
        """Should have optional error_message."""
        result = ProcessingResult(
            source_file=Path("test.c"),
            success=False,
            error_message="test error"
        )
        assert result.error_message == "test error"

    def test_default_error_message_is_none(self):
        """Should default error_message to None."""
        result = ProcessingResult(source_file=Path("test.c"), success=True)
        assert result.error_message is None

    def test_is_dataclass(self):
        """Should be a dataclass."""
        from dataclasses import is_dataclass
        assert is_dataclass(ProcessingResult)


class TestProcessingStatistics:
    """Tests for ProcessingStatistics dataclass."""

    def test_default_values(self):
        """Should have default values."""
        stats = ProcessingStatistics()
        assert stats.total_files == 0
        assert stats.successful == 0
        assert stats.failed == 0
        assert stats.skipped == 0
        assert stats.results == []

    def test_custom_values(self):
        """Should accept custom values."""
        stats = ProcessingStatistics(
            total_files=10,
            successful=8,
            failed=2
        )
        assert stats.total_files == 10
        assert stats.successful == 8
        assert stats.failed == 2

    def test_success_rate_zero_when_no_files(self):
        """Should return 0.0 when no files processed."""
        stats = ProcessingStatistics()
        assert stats.success_rate == 0.0

    def test_success_rate_calculation(self):
        """Should calculate success rate correctly."""
        stats = ProcessingStatistics(total_files=10, successful=8, failed=2)
        assert stats.success_rate == 80.0

    def test_success_rate_100_percent(self):
        """Should return 100.0 when all successful."""
        stats = ProcessingStatistics(total_files=5, successful=5, failed=0)
        assert stats.success_rate == 100.0


class TestStatisticsFormatter:
    """Tests for StatisticsFormatter."""

    def test_format_summary_basic(self):
        """Should format basic summary."""
        stats = ProcessingStatistics(
            total_files=10,
            successful=8,
            failed=2
        )
        result = StatisticsFormatter.format_summary("Test Stage", stats)
        assert "Test Stage:" in result
        assert "Files processed: 10" in result
        assert "Successful:      8" in result
        assert "Failed:          2" in result

    def test_format_summary_with_skipped(self):
        """Should include skipped when > 0."""
        stats = ProcessingStatistics(
            total_files=10,
            successful=7,
            failed=2,
            skipped=1
        )
        result = StatisticsFormatter.format_summary("Test Stage", stats)
        assert "Skipped:         1" in result

    def test_format_summary_without_skipped(self):
        """Should not include skipped when 0."""
        stats = ProcessingStatistics(total_files=10, successful=10, failed=0)
        result = StatisticsFormatter.format_summary("Test Stage", stats)
        assert "Skipped" not in result

    def test_format_summary_with_failures(self):
        """Should list failed files."""
        stats = ProcessingStatistics(
            total_files=2,
            successful=1,
            failed=1,
            results=[
                ProcessingResult(Path("ok.c"), True),
                ProcessingResult(Path("fail.c"), False, "error message"),
            ]
        )
        result = StatisticsFormatter.format_summary("Test Stage", stats, show_failures=True)
        assert "Failed files:" in result
        assert "fail.c: error message" in result

    def test_format_summary_hide_failures(self):
        """Should hide failures when show_failures=False."""
        stats = ProcessingStatistics(
            total_files=2,
            successful=1,
            failed=1,
            results=[
                ProcessingResult(Path("ok.c"), True),
                ProcessingResult(Path("fail.c"), False, "error message"),
            ]
        )
        result = StatisticsFormatter.format_summary("Test Stage", stats, show_failures=False)
        assert "Failed files:" not in result

    def test_format_summary_with_extra_lines(self):
        """Should include extra lines."""
        stats = ProcessingStatistics(total_files=5, successful=5, failed=0)
        extra = ["", "Additional info: test"]
        result = StatisticsFormatter.format_summary("Test Stage", stats, extra_lines=extra)
        assert "Additional info: test" in result
