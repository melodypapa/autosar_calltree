#!/usr/bin/env python3
"""Validate requirements traceability (SWUT_XXX → SWR_XXX)."""

import re
import sys
from pathlib import Path
from typing import Dict, Set, Tuple


def extract_swut_from_tests(tests_dir: Path) -> Set[str]:
    """Extract all SWUT_ references from test files."""
    swut_refs = set()

    for test_file in tests_dir.rglob("test_*.py"):
        content = test_file.read_text()
        # Match comments like: # SWUT_MODEL_00001
        matches = re.findall(r'#\s*SWUT_[A-Z_]+_\d+', content)
        swut_refs.update(m.strip() for m in matches)

    return swut_refs


def extract_swr_from_requirements(reqs_dir: Path) -> Set[str]:
    """Extract all SWR_ definitions from requirement documents."""
    swr_defs = set()

    for req_file in reqs_dir.glob("*.md"):
        content = req_file.read_text()
        # Match definitions like: ### SWR_MODEL_00001
        matches = re.findall(r'#+\s*SWR_[A-Z_]+_\d+', content)
        swr_defs.update(m.strip().replace('#', '').strip() for m in matches)

    return swr_defs


def parse_traceability(traceability_file: Path) -> Dict[str, str]:
    """Parse existing traceability matrix."""
    trace_map = {}

    if not traceability_file.exists():
        return trace_map

    content = traceability_file.read_text()
    # Parse markdown table rows with SWR and SWUT
    rows = re.findall(r'\|\s*(SWR_[A-Z_]+_\d+)\s*\|\s*(SWUT_[A-Z_]+_\d+)', content)
    for swr, swut in rows:
        trace_map[swut] = swr

    return trace_map


def validate_traceability(
    swut_refs: Set[str],
    swr_defs: Set[str],
    trace_map: Dict[str, str]
) -> Tuple[int, int, Set[str], Set[str]]:
    """Validate traceability and return statistics."""
    orphaned_tests = set()
    untested_requirements = set()

    # Check for orphaned tests (SWUT without mapped SWR)
    for swut in swut_refs:
        if swut not in trace_map:
            orphaned_tests.add(swut)
        elif trace_map[swut] not in swr_defs:
            orphaned_tests.add(swut)

    # Check for untested requirements (SWR without mapped SWUT)
    mapped_swrs = set(trace_map.values())
    for swr in swr_defs:
        if swr not in mapped_swrs:
            untested_requirements.add(swr)

    return len(swut_refs), len(swr_defs), orphaned_tests, untested_requirements


def main() -> int:
    """Run traceability validation."""
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "tests"
    reqs_dir = project_root / "docs" / "requirements"
    traceability_file = project_root / "docs" / "TRACEABILITY.md"

    print("=== Checking Requirements Traceability ===\n")

    # Extract references
    swut_refs = extract_swut_from_tests(tests_dir)
    swr_defs = extract_swr_from_requirements(reqs_dir)
    trace_map = parse_traceability(traceability_file)

    # Validate
    test_count, req_count, orphaned_tests, untested_reqs = validate_traceability(
        swut_refs, swr_defs, trace_map
    )

    print(f"Test cases found: {test_count}")
    print(f"Requirements found: {req_count}")
    print(f"Traceability links: {len(trace_map)}")

    # Report issues
    exit_code = 0

    if orphaned_tests:
        print(f"\n❌ Orphaned tests ({len(orphaned_tests)}):")
        for swut in sorted(orphaned_tests):
            print(f"  - {swut}")
        exit_code = 1
    else:
        print("\n✅ All tests trace to requirements")

    if untested_reqs:
        print(f"\n⚠️  Untested requirements ({len(untested_reqs)}):")
        for swr in sorted(untested_reqs)[:10]:  # Show first 10
            print(f"  - {swr}")
        if len(untested_reqs) > 10:
            print(f"  ... and {len(untested_reqs) - 10} more")
    else:
        print("✅ All requirements have tests")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
