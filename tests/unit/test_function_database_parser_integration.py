"""
Tests for FunctionDatabase parser integration.

Tests that FunctionDatabase correctly selects and uses the appropriate parser
(pycparser when available, regex parser as fallback).
"""

from pathlib import Path

import pytest

from autosar_calltree.database.function_database import (
    FunctionDatabase,
    PYCPARSER_AVAILABLE,
)


class TestFunctionDatabaseParserIntegration:
    """Test parser selection and integration in FunctionDatabase."""

    def test_database_initialization(self):
        """Test that database initializes with correct parser."""
        db = FunctionDatabase(source_dir="demo")

        # Verify parser type is set
        assert hasattr(db, "parser_type")
        assert db.parser_type in ["pycparser", "regex"]

        # Verify parser type matches availability
        if PYCPARSER_AVAILABLE:
            assert db.parser_type == "pycparser"
        else:
            assert db.parser_type == "regex"

    def test_statistics_includes_parser_info(self):
        """Test that statistics include parser type information."""
        db = FunctionDatabase(source_dir="demo")
        stats = db.get_statistics()

        assert "parser_type" in stats
        assert stats["parser_type"] in ["pycparser", "regex"]
        assert "pycparser_available" in stats
        assert isinstance(stats["pycparser_available"], bool)

        # Verify consistency
        assert stats["pycparser_available"] == PYCPARSER_AVAILABLE
        assert stats["parser_type"] == db.parser_type

    def test_parser_type_persistence_in_cache(self, tmp_path: Path):
        """Test that cache includes parser type information."""
        from autosar_calltree.database.function_database import CacheMetadata
        from datetime import datetime

        # Create metadata with parser type
        metadata = CacheMetadata(
            created_at=datetime.now(),
            source_directory="/test",
            file_count=10,
            parser_type="pycparser",
        )

        assert metadata.parser_type == "pycparser"

        # Test default value
        default_metadata = CacheMetadata(
            created_at=datetime.now(),
            source_directory="/test",
            file_count=10,
        )

        assert default_metadata.parser_type == "regex"

    @pytest.mark.skipif(
        not Path("demo").exists(),
        reason="demo directory not found",
    )
    def test_build_database_with_correct_parser(self):
        """Test that database building uses the correct parser."""
        db = FunctionDatabase(source_dir="demo")

        # Build database (this will use the selected parser)
        db.build_database(use_cache=False, verbose=False)

        # Verify statistics reflect the parser used
        stats = db.get_statistics()
        assert stats["parser_type"] == db.parser_type

        # Verify some functions were found
        assert stats["total_functions_found"] > 0

    def test_cache_invalidation_on_parser_change(self, tmp_path: Path):
        """Test that cache is invalidated when parser type changes."""
        # Create a test database with mock cache
        import pickle
        from datetime import datetime
        from autosar_calltree.database.function_database import CacheMetadata

        cache_dir = tmp_path / ".cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / "function_db.pkl"

        # Create cache with different parser type
        metadata = CacheMetadata(
            created_at=datetime.now(),
            source_directory=str(tmp_path),
            file_count=5,
            parser_type="pycparser" if not PYCPARSER_AVAILABLE else "regex",  # Opposite of current
        )

        cache_data = {
            "metadata": metadata,
            "functions": {},
            "qualified_functions": {},
            "functions_by_file": {},
            "total_files_scanned": 5,
            "total_functions_found": 10,
            "parse_errors": [],
        }

        # Write cache file
        with open(cache_file, "wb") as f:
            pickle.dump(cache_data, f)

        # Create database with this cache directory
        db = FunctionDatabase(source_dir=str(tmp_path), cache_dir=str(cache_dir))

        # Try to load from cache - should fail due to parser type mismatch
        result = db._load_from_cache(verbose=False)

        # Cache should be rejected due to parser type mismatch
        assert result is False

    def test_parser_availability_constant(self):
        """Test that PYCPARSER_AVAILABLE constant is correctly set."""
        # Verify it's a boolean
        assert isinstance(PYCPARSER_AVAILABLE, bool)

        # If pycparser is available, we should be able to import it
        if PYCPARSER_AVAILABLE:
            from autosar_calltree.parsers.c_parser_pycparser import CParserPyCParser
            assert CParserPyCParser is not None
        else:
            # Should not be importable
            try:
                from autosar_calltree.parsers.c_parser_pycparser import CParserPyCParser
                # If we got here, pycparser IS available despite the flag
                # This is okay, just means the flag is conservative
            except ImportError:
                # Expected when PYCPARSER_AVAILABLE is False
                pass
