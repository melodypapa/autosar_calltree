r"""Test to cover lines 326-328 in c_parser.py.

Lines 326-328 are in the multiline function parsing backtrack logic.
They are triggered when the previous line doesn't match the pattern ^[\w\s\*]+$
"""

from pathlib import Path

from autosar_calltree.parsers.c_parser import CParser


def test_swut_parser_c_line_326_328_multiline_with_non_type_return_line():
    r"""Test multiline function where previous line doesn't match type pattern.

    This tests lines 326-328:
    - Line 326: else:
    - Line 327: break
    - Line 328: (closing brace of if)

    The code checks if prev_line matches r"^[\w\s\*]+$" before including it.
    If it doesn't match (e.g., contains a comment or special chars), it breaks.

    We need to create a scenario where:
    1. The function declaration spans multiple lines
    2. The line before the function name looks like a return type
    3. But when checking the line before that, it has special chars that break the pattern
    """
    parser = CParser()

    # Create a file with a multiline function where the return type line
    # has a comment that breaks the pattern
    # The pattern should match: return_type function_name(params)
    # But return_type is on a separate line with a comment
    with open("/tmp/test_line_326.c", "w") as f:
        f.write("""
const char* // Comment breaks pattern
test_function(int param)
{
    return "hello";
}
""")

    functions = parser.parse_file(Path("/tmp/test_line_326.c"))

    # The function should be parsed
    assert len(functions) >= 1
    func = next((f for f in functions if f.name == "test_function"), None)
    assert func is not None
