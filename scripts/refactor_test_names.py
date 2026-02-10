#!/usr/bin/env python3
"""
Script to refactor test function names by removing SWUT IDs from function names
and adding them as docstrings instead.

Transforms test_SWUT_XXXXX_YYYYY_descriptive_name() to test_descriptive_name()
with SWUT_XXXXX_YYYYY added as a docstring.
"""

import re
from pathlib import Path


def extract_swut_id(function_name: str) -> tuple:
    """Extract SWUT ID and descriptive name from test function name.

    Returns:
        tuple: (swut_id, new_function_name, original_function_name)
    """
    # Match pattern: test_SWUT_XXXXX_YYYYY_descriptive_name
    match = re.match(r'(test_)(SWUT_[A-Z_]+_\d+)(_(.+))$', function_name)
    if match:
        swut_id = match.group(2)  # SWUT_XXXXX_YYYYY without test_ prefix
        descriptive_part = match.group(4)
        new_function_name = f"test_{descriptive_part}"
        return swut_id, new_function_name, function_name
    return None, function_name, function_name


def refactor_test_file(file_path: Path) -> int:
    """Refactor test functions in a single file.

    Returns:
        int: Number of functions refactored
    """
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines = []
    refactor_count = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line defines a test function with SWUT ID
        # Matches: [indent]def test_SWUT_XXXXX_YYYYY_descriptive_name(...)[ -> return_type]:
        # Groups: (1=indent, 2='def ', 3=func_name, 4=params, 5=return annotation)
        match = re.search(r'(\s*)(def\s+)(test_SWUT_[A-Z_]+_\d+_[^(]+)(\([^)]*\))(\s*(->\s+[^:]+))?:', line)
        if match:
            indent = match.group(1)
            def_kw = match.group(2)
            original_name = match.group(3).strip()
            params = match.group(4)
            return_annotation = match.group(5) or ''

            swut_id, new_name, _ = extract_swut_id(original_name)

            if swut_id:
                # Replace function definition
                new_def = f"{indent}{def_kw}{new_name}{params}{return_annotation}:"
                new_lines.append(new_def)
                refactor_count += 1

                # Check next line for docstring
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    docstring_match = re.match(r'\s+"""(.+?)"""', next_line)

                    if docstring_match:
                        # Existing docstring - prepend SWUT ID
                        existing_doc = docstring_match.group(1)
                        doc_indent = len(next_line) - len(next_line.lstrip())
                        indent_str = ' ' * doc_indent

                        new_lines.append(f'{indent_str}"""{swut_id}')
                        new_lines.append(f'{indent_str}')
                        new_lines.append(f'{indent_str}{existing_doc}"""')
                        i += 1  # Skip the original docstring line
                    else:
                        # No docstring - add one
                        doc_indent = len(line) - len(line.lstrip()) + 4
                        indent_str = ' ' * doc_indent
                        new_lines.append(f'{indent_str}"""{swut_id}"""')
                else:
                    # End of file, add docstring
                    doc_indent = len(line) - len(line.lstrip()) + 4
                    indent_str = ' ' * doc_indent
                    new_lines.append(f'{indent_str}"""{swut_id}"""')
            else:
                # No SWUT ID found, keep original
                new_lines.append(line)
        else:
            new_lines.append(line)

        i += 1

    # Write back if changes were made
    if refactor_count > 0:
        file_path.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')

    return refactor_count


def main():
    """Main entry point."""
    tests_dir = Path('tests')

    if not tests_dir.exists():
        print(f"Error: {tests_dir} directory not found")
        return 1

    # Find all Python test files
    test_files = list(tests_dir.rglob('test_*.py'))

    print(f"Found {len(test_files)} test files")
    print("=" * 60)

    total_refactored = 0
    files_modified = []

    for test_file in test_files:
        count = refactor_test_file(test_file)
        if count > 0:
            files_modified.append((test_file, count))
            total_refactored += count
            print(f"OK {test_file}: {count} functions refactored")

    print("=" * 60)
    print(f"Total: {total_refactored} functions refactored in {len(files_modified)} files")

    return 0


if __name__ == '__main__':
    exit(main())
