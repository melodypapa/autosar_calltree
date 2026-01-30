"""
Pytest configuration and fixtures.
"""

from pathlib import Path
import pytest


@pytest.fixture
def test_fixtures_dir() -> Path:
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"
