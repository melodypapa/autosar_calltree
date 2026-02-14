"""
Pytest configuration and fixtures.
"""

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

import pytest


@pytest.fixture
def test_fixtures_dir() -> Path:
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def demo_dir() -> Path:
    """Path to demo directory with AUTOSAR C source files."""
    # Get the project root (parent of tests directory)
    project_root = Path(__file__).parent.parent
    demo_path = project_root / "demo"
    return demo_path


@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
    """
    Fixture that provides a temporary directory for test outputs.

    Uses the system's temporary directory (e.g., /tmp on Unix, C:\Temp on Windows).
    Automatically cleaned up after the test completes.

    Use this fixture for tests that need to write actual output files
    to disk instead of using Click's isolated_filesystem().
    """
    with TemporaryDirectory(prefix="autosar_calltree_test_") as temp_dir:
        yield Path(temp_dir)
        # Temp directory automatically cleaned up by context manager


@pytest.fixture(autouse=True)
def cleanup_temp_files() -> Generator[None, None, None]:
    """
    Auto-use fixture that cleans up temporary test files after each test.

    Removes common test output files that may be created during testing:
    - call_tree.md
    - call_tree.mermaid.md
    - call_tree.xmi
    - Any other call_tree.* files

    This fixture runs automatically after every test to ensure
    working directory remains clean.

    Note: Most tests should use temp_output_dir or isolated_filesystem()
    to avoid creating files in the project root. This is a safety net.
    """
    yield  # Run the test

    # Cleanup: Remove any call_tree.* files from project root
    project_root = Path(__file__).parent.parent

    # Remove specific known files
    temp_files = [
        project_root / "call_tree.md",
        project_root / "call_tree.mermaid.md",
        project_root / "call_tree.xmi",
    ]

    for temp_file in temp_files:
        if temp_file.exists():
            try:
                temp_file.unlink()
            except Exception:
                # Silently fail if cleanup doesn't work
                pass

    # Also clean up any wildcard call_tree.* files if any remain
    try:
        for call_tree_file in project_root.glob("call_tree.*"):
            try:
                call_tree_file.unlink()
            except Exception:
                pass
    except Exception:
        pass
