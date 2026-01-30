"""
Pytest configuration and fixtures.
"""

from pathlib import Path
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
