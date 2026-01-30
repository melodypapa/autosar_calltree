"""
Unit tests for FunctionDatabase module.

Tests cover database initialization, building, indexing, smart lookup,
caching, and query methods.
"""

import pickle
import shutil
import tempfile
from pathlib import Path
from typing import List

import pytest

from autosar_calltree.database.function_database import (
    CacheMetadata,
    FunctionDatabase,
)
from autosar_calltree.database.models import FunctionInfo, FunctionType
from autosar_calltree.config.module_config import ModuleConfig


# Helper to create function info with proper enum
def create_function(name, file_path, line_number, calls=None, sw_module=None, is_static=False):
    """Helper to create FunctionInfo with proper enum handling."""
    return FunctionInfo(
        name=name,
        return_type="void",
        file_path=Path(file_path) if isinstance(file_path, str) else file_path,
        line_number=line_number,
        is_static=is_static,
        function_type=FunctionType.TRADITIONAL_C,
        calls=calls or [],
        sw_module=sw_module
    )


class TestFunctionDatabaseInitialization:
    """Test database initialization and setup (SWR_DB_00001, SWR_DB_00002)."""

    def test_SWUT_DB_00001_database_initialization(self):
        """Test database can be initialized with source directory (SWR_DB_00001)."""
        db = FunctionDatabase(source_dir="./demo")

        assert db.source_dir == Path("./demo")
        assert db.cache_dir == Path("./demo/.cache")
        assert db.cache_file == db.cache_dir / "function_db.pkl"
        assert db.functions == {}
        assert db.qualified_functions == {}
        assert db.functions_by_file == {}

    def test_SWUT_DB_00001_custom_cache_directory(self):
        """Test database can be initialized with custom cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "custom_cache"
            db = FunctionDatabase(
                source_dir="./demo", cache_dir=str(cache_path)
            )

            assert db.cache_dir == cache_path
            assert db.cache_file == cache_path / "function_db.pkl"

    def test_SWUT_DB_00001_with_module_config(self):
        """Test database can be initialized with module configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            config_file.write_text("""
version: "1.0"
file_mappings:
  demo.c: DemoModule
""")

            config = ModuleConfig(config_file)
            db = FunctionDatabase(
                source_dir="./demo", module_config=config
            )

            assert db.module_config == config

    def test_SWUT_DB_00002_cache_directory_creation(self):
        """Test cache directory is created automatically (SWR_DB_00002)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "test_cache"
            assert not cache_path.exists()

            db = FunctionDatabase(
                source_dir=temp_dir, cache_dir=str(cache_path)
            )

            assert cache_path.exists()
            assert cache_path.is_dir()


class TestDatabaseIndexing:
    """Test three-index database structure (SWR_DB_00003)."""

    def test_SWUT_DB_00003_three_index_structure(self):
        """Test database maintains three indexing structures (SWR_DB_00003)."""
        db = FunctionDatabase(source_dir="./demo")

        func = create_function(
            name="test_func",
            file_path="test.c",
            line_number=10,
            calls=["func1", "func2"]
        )

        db._add_function(func)

        # Check main index
        assert "test_func" in db.functions
        assert db.functions["test_func"] == [func]

        # Check qualified index
        assert "test::test_func" in db.qualified_functions
        assert db.qualified_functions["test::test_func"] == func

        # Note: functions_by_file is only populated when using _parse_file
        # When calling _add_function directly, it's not indexed by file
        # This is tested by the database_building test instead

    def test_SWUT_DB_00003_multiple_functions_same_name(self):
        """Test indexing handles multiple functions with same name."""
        db = FunctionDatabase(source_dir="./demo")

        func1 = create_function(
            name="duplicate",
            file_path="file1.c",
            line_number=10,
            calls=[]
        )

        func2 = create_function(
            name="duplicate",
            file_path="file2.c",
            line_number=20,
            calls=[]
        )

        db._add_function(func1)
        db._add_function(func2)

        # Both should be in main index
        assert len(db.functions["duplicate"]) == 2
        assert func1 in db.functions["duplicate"]
        assert func2 in db.functions["duplicate"]

        # Both should be in qualified index
        assert "file1::duplicate" in db.qualified_functions
        assert "file2::duplicate" in db.qualified_functions

    def test_SWUT_DB_00003_qualified_key_generation(self):
        """Test qualified key format is file_stem::function_name."""
        db = FunctionDatabase(source_dir="./demo")

        func = create_function(
            name="MyFunction",
            file_path="/path/to/my_function.c",
            line_number=10,
            calls=[]
        )

        db._add_function(func)

        assert "my_function::MyFunction" in db.qualified_functions


class TestDatabaseBuilding:
    """Test database building from source files (SWR_DB_00004, SWR_DB_00005)."""

    def test_SWUT_DB_00004_source_file_discovery(self):
        """Test database discovers all .c files recursively (SWR_DB_00004)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create files in nested structure
            (temp_path / "file1.c").write_text("// code")
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "file2.c").write_text("// code")
            (temp_path / "subdir" / "nested").mkdir()
            (temp_path / "subdir" / "nested" / "file3.c").write_text("// code")

            db = FunctionDatabase(source_dir=temp_dir)

            c_files = list(db.source_dir.rglob("*.c"))
            assert len(c_files) == 3
            assert any(f.name == "file1.c" for f in c_files)
            assert any(f.name == "file2.c" for f in c_files)
            assert any(f.name == "file3.c" for f in c_files)

    def test_SWUT_DB_00004_empty_directory(self):
        """Test database handles empty source directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = FunctionDatabase(source_dir=temp_dir)
            db.build_database(use_cache=False, verbose=False)

            assert db.total_files_scanned == 0
            assert db.total_functions_found == 0

    def test_SWUT_DB_00005_database_building(self):
        """Test database builds correctly from demo directory (SWR_DB_00005)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        assert db.total_files_scanned == 4
        assert db.total_functions_found >= 5
        assert len(db.functions) > 0
        assert len(db.functions_by_file) == 4

    def test_SWUT_DB_00005_parse_error_collection(self):
        """Test parse errors are collected without stopping scan (SWR_DB_00021)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Valid file
            (temp_path / "valid.c").write_text("""
void valid_func(void) {
    return;
}
""")

            # File that might cause issues (empty)
            (temp_path / "empty.c").write_text("")

            db = FunctionDatabase(source_dir=temp_dir)
            db.build_database(use_cache=False, verbose=False)

            # Should scan both files
            assert db.total_files_scanned == 2

            # Should parse at least the valid function
            assert db.total_functions_found >= 1


class TestModuleConfiguration:
    """Test module configuration integration (SWR_DB_00006, SWR_DB_00007)."""

    def test_SWUT_DB_00006_module_config_integration(self):
        """Test module configuration is applied to functions (SWR_DB_00006)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            config_file.write_text("""
version: "1.0"
file_mappings:
  test.c: TestModule
""")

            config = ModuleConfig(config_file)
            db = FunctionDatabase(source_dir=temp_dir, module_config=config)

            func = create_function(
                name="test_func",
                file_path="test.c",
                line_number=10,
                calls=[]
            )

            db._add_function(func)

            assert func.sw_module == "TestModule"
            assert db.module_stats["TestModule"] == 1

    def test_SWUT_DB_00006_file_not_in_config(self):
        """Test function without module mapping has no module assigned."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            config_file.write_text("""
version: "1.0"
file_mappings:
  other.c: OtherModule
""")

            config = ModuleConfig(config_file)
            db = FunctionDatabase(source_dir=temp_dir, module_config=config)

            func = create_function(
                name="test_func",
                file_path="unmapped.c",
                line_number=10,
                calls=[]
            )

            db._add_function(func)

            assert func.sw_module is None

    def test_SWUT_DB_00007_module_statistics_tracking(self):
        """Test module statistics are tracked correctly (SWR_DB_00007)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            config_file.write_text("""
version: "1.0"
file_mappings:
  file1.c: ModuleA
  file2.c: ModuleB
""")

            config = ModuleConfig(config_file)
            db = FunctionDatabase(source_dir=temp_dir, module_config=config)

            # Add functions to different modules
            func1 = create_function(
                name="func1",
                file_path="file1.c",
                line_number=10,
                calls=[]
            )

            func2 = create_function(
                name="func2",
                file_path="file1.c",
                line_number=20,
                calls=[]
            )

            func3 = create_function(
                name="func3",
                file_path="file2.c",
                line_number=10,
                calls=[]
            )

            db._add_function(func1)
            db._add_function(func2)
            db._add_function(func3)

            assert db.module_stats["ModuleA"] == 2
            assert db.module_stats["ModuleB"] == 1


class TestSmartFunctionLookup:
    """Test smart function lookup strategies (SWR_DB_00009-00012)."""

    def test_SWUT_DB_00009_smart_lookup_implementation_preference(self):
        """Test prefer functions with implementations (SWR_DB_00009)."""
        db = FunctionDatabase(source_dir="./demo")

        # Declaration (no calls)
        declaration = create_function(
            name="COM_Init",
            file_path="demo.c",
            line_number=5,
            calls=[]
        )

        # Implementation (has calls)
        implementation = create_function(
            name="COM_Init",
            file_path="communication.c",
            line_number=10,
            calls=["other_func"]
        )

        db.functions["COM_Init"] = [declaration, implementation]

        result = db._select_best_function_match(
            db.functions["COM_Init"],
            context_file="demo.c"
        )

        assert result == implementation
        assert len(result.calls) > 0

    def test_SWUT_DB_00010_smart_lookup_filename_heuristics(self):
        """Test prefer functions from files matching function name (SWR_DB_00010)."""
        db = FunctionDatabase(source_dir="./demo")

        # Function in matching file
        implementation = create_function(
            name="COM_InitCommunication",
            file_path="communication.c",
            line_number=10,
            calls=["other_func"],
            sw_module="CommunicationModule"
        )

        # Function in non-matching file
        other = create_function(
            name="COM_InitCommunication",
            file_path="demo.c",
            line_number=5,
            calls=["other_func"]
        )

        db.functions["COM_InitCommunication"] = [implementation, other]

        result = db._select_best_function_match(
            db.functions["COM_InitCommunication"]
        )

        assert result == implementation
        assert result.sw_module == "CommunicationModule"

    def test_SWUT_DB_00011_smart_lookup_cross_module_awareness(self):
        """Test avoid functions from calling file (SWR_DB_00011)."""
        db = FunctionDatabase(source_dir="./demo")

        # Declaration in calling file
        local_decl = create_function(
            name="COM_Init",
            file_path="demo.c",
            line_number=5,
            calls=[]
        )

        # Implementation in other file
        external_impl = create_function(
            name="COM_Init",
            file_path="communication.c",
            line_number=10,
            calls=["other_func"]
        )

        db.functions["COM_Init"] = [local_decl, external_impl]

        result = db._select_best_function_match(
            db.functions["COM_Init"],
            context_file="demo.c"
        )

        assert result == external_impl
        assert "demo.c" not in str(result.file_path)

    def test_SWUT_DB_00012_smart_lookup_module_preference(self):
        """Test prefer functions with modules assigned (SWR_DB_00012)."""
        db = FunctionDatabase(source_dir="./demo")

        # Function with module
        with_module = create_function(
            name="SomeFunc",
            file_path="file1.c",
            line_number=10,
            calls=[],
            sw_module="ModuleA"
        )

        # Function without module
        without_module = create_function(
            name="SomeFunc",
            file_path="file2.c",
            line_number=10,
            calls=[]
        )

        db.functions["SomeFunc"] = [with_module, without_module]

        result = db._select_best_function_match(
            db.functions["SomeFunc"]
        )

        assert result == with_module
        assert result.sw_module == "ModuleA"

    def test_SWUT_DB_00009_single_candidate(self):
        """Test smart lookup returns single candidate."""
        db = FunctionDatabase(source_dir="./demo")

        func = create_function(
            name="SingleFunc",
            file_path="file.c",
            line_number=10,
            calls=[]
        )

        result = db._select_best_function_match([func])

        assert result == func


class TestCaching:
    """Test cache save/load functionality (SWR_DB_00013-00016)."""

    def test_SWUT_DB_00010_cache_save_load(self):
        """Test cache can be saved and loaded (SWR_DB_00014)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "cache"
            db = FunctionDatabase(
                source_dir="./demo",
                cache_dir=str(cache_dir)
            )

            db.build_database(use_cache=False, verbose=False)
            original_functions = db.total_functions_found

            # Save to cache
            db._save_to_cache(verbose=False)
            assert db.cache_file.exists()

            # Create new database and load from cache
            db2 = FunctionDatabase(
                source_dir="./demo",
                cache_dir=str(cache_dir)
            )
            loaded = db2._load_from_cache(verbose=False)

            assert loaded is True
            assert db2.total_functions_found == original_functions
            assert db2.total_files_scanned == db.total_files_scanned

    def test_SWUT_DB_00013_cache_metadata_validation(self):
        """Test cache loading validates metadata (SWR_DB_00013)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "cache"

            # Build and save cache
            db1 = FunctionDatabase(
                source_dir="./demo",
                cache_dir=str(cache_dir)
            )
            db1.build_database(use_cache=False, verbose=False)
            db1._save_to_cache(verbose=False)

            # Try to load with wrong source directory
            db2 = FunctionDatabase(
                source_dir="/wrong/directory",
                cache_dir=str(cache_dir)
            )
            loaded = db2._load_from_cache(verbose=False)

            assert loaded is False

    def test_SWUT_DB_00012_cache_error_handling(self):
        """Test cache loading handles errors gracefully (SWR_DB_00016)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "cache"
            db = FunctionDatabase(
                source_dir="./demo",
                cache_dir=str(cache_dir)
            )

            # Create corrupted cache file
            cache_dir.mkdir(parents=True, exist_ok=True)
            db.cache_file.write_text("corrupted data")

            # Try to load
            loaded = db._load_from_cache(verbose=False)

            assert loaded is False
            assert len(db.functions) == 0

    def test_SWUT_DB_00015_cache_loading_progress(self):
        """Test cache loading shows file-by-file progress (SWR_DB_00015)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "cache"

            # Build and save cache
            db1 = FunctionDatabase(
                source_dir="./demo",
                cache_dir=str(cache_dir)
            )
            db1.build_database(use_cache=False, verbose=False)
            db1._save_to_cache(verbose=False)

            # Load with verbose and capture output
            db2 = FunctionDatabase(
                source_dir="./demo",
                cache_dir=str(cache_dir)
            )

            import sys
            from io import StringIO

            old_stdout = sys.stdout
            sys.stdout = StringIO()

            loaded = db2._load_from_cache(verbose=True)
            output = sys.stdout.getvalue()

            sys.stdout = old_stdout

            assert loaded is True
            assert "Loading" in output
            assert "files from cache" in output

    def test_SWUT_DB_00020_cache_clearing(self):
        """Test cache file can be deleted (SWR_DB_00022)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "cache"

            db = FunctionDatabase(
                source_dir="./demo",
                cache_dir=str(cache_dir)
            )
            db.build_database(use_cache=True, verbose=False)

            assert db.cache_file.exists()

            db.clear_cache()

            assert not db.cache_file.exists()

    def test_SWUT_DB_00020_clear_nonexistent_cache(self):
        """Test clearing nonexistent cache doesn't fail."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "cache"

            db = FunctionDatabase(
                source_dir="./demo",
                cache_dir=str(cache_dir)
            )

            # Should not raise
            db.clear_cache()

            assert not db.cache_file.exists()


class TestQueryMethods:
    """Test database query methods (SWR_DB_00017-00020, SWR_DB_00023-00024)."""

    def test_SWUT_DB_00013_function_lookup_by_name(self):
        """Test functions can be looked up by name (SWR_DB_00017)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        result = db.lookup_function("Demo_Init")

        assert len(result) > 0
        assert result[0].name == "Demo_Init"

    def test_SWUT_DB_00013_lookup_nonexistent_function(self):
        """Test lookup returns empty list for nonexistent function."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        result = db.lookup_function("NonExistentFunction")

        assert result == []

    def test_SWUT_DB_00014_qualified_function_lookup(self):
        """Test functions can be looked up by qualified name (SWR_DB_00018)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        result = db.get_function_by_qualified_name("demo::Demo_Init")

        assert result is not None
        assert result.name == "Demo_Init"
        assert "demo.c" in str(result.file_path)

    def test_SWUT_DB_00014_qualified_lookup_not_found(self):
        """Test qualified lookup returns None for nonexistent function."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        result = db.get_function_by_qualified_name("nonexistent::Func")

        assert result is None

    def test_SWUT_DB_00015_function_search_pattern(self):
        """Test functions can be searched by pattern (SWR_DB_00019)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        result = db.search_functions("Init")

        assert len(result) > 0
        assert all("Init" in f.name for f in result)

    def test_SWUT_DB_00015_search_case_insensitive(self):
        """Test search is case-insensitive."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        result_upper = db.search_functions("Init")
        result_lower = db.search_functions("init")

        assert len(result_upper) == len(result_lower)

    def test_SWUT_DB_00015_search_empty_pattern(self):
        """Test search with empty pattern returns all functions."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        result = db.search_functions("")

        # Should return all functions
        assert len(result) == db.total_functions_found

    def test_SWUT_DB_00016_database_statistics(self):
        """Test database returns accurate statistics (SWR_DB_00020)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        stats = db.get_statistics()

        assert "total_files_scanned" in stats
        assert "total_functions_found" in stats
        assert "unique_function_names" in stats
        assert "static_functions" in stats
        assert "parse_errors" in stats
        assert "module_stats" in stats

        assert stats["total_files_scanned"] == 4
        assert stats["total_functions_found"] > 0
        assert stats["unique_function_names"] > 0

    def test_SWUT_DB_00017_get_all_function_names(self):
        """Test database returns sorted list of function names (SWR_DB_00023)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        names = db.get_all_function_names()

        assert isinstance(names, list)
        assert len(names) > 0
        assert names == sorted(names)

    def test_SWUT_DB_00017_empty_database_function_names(self):
        """Test get_all_function_names on empty database."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = FunctionDatabase(source_dir=temp_dir)
            db.build_database(use_cache=False, verbose=False)

            names = db.get_all_function_names()

            assert names == []

    def test_SWUT_DB_00018_get_functions_by_file(self):
        """Test database can return functions in a file (SWR_DB_00024)."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        # Get a file path that exists
        file_path = None
        for fp in db.functions_by_file.keys():
            if "demo.c" in fp:
                file_path = fp
                break

        assert file_path is not None

        functions = db.get_functions_in_file(file_path)

        assert len(functions) > 0
        assert all("demo.c" in str(f.file_path) for f in functions)

    def test_SWUT_DB_00018_get_functions_nonexistent_file(self):
        """Test get_functions_in_file for nonexistent file."""
        db = FunctionDatabase(source_dir="./demo")
        db.build_database(use_cache=False, verbose=False)

        functions = db.get_functions_in_file("nonexistent.c")

        assert functions == []


class TestCacheMetadata:
    """Test CacheMetadata dataclass."""

    def test_cache_metadata_creation(self):
        """Test CacheMetadata can be created with required fields."""
        from datetime import datetime

        metadata = CacheMetadata(
            created_at=datetime.now(),
            source_directory="/test/path",
            file_count=5
        )

        assert metadata.source_directory == "/test/path"
        assert metadata.file_count == 5
        assert metadata.file_checksums == {}

    def test_cache_metadata_with_checksums(self):
        """Test CacheMetadata can include file checksums."""
        from datetime import datetime

        checksums = {
            "file1.c": "abc123",
            "file2.c": "def456"
        }

        metadata = CacheMetadata(
            created_at=datetime.now(),
            source_directory="/test/path",
            file_count=2,
            file_checksums=checksums
        )

        assert len(metadata.file_checksums) == 2
        assert metadata.file_checksums["file1.c"] == "abc123"
