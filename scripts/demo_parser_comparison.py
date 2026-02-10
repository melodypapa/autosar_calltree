#!/usr/bin/env python
"""
Demo script comparing regex-based C parser vs pycparser-based parser.

This script demonstrates the differences between the two parsing approaches
and helps you decide which one to use.

Usage:
    python scripts/demo_parser_comparison.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def create_test_cases():
    """Create test C code snippets for comparison."""
    test_cases = {
        "simple_function": """
            int add(int a, int b) {
                return a + b;
            }
            """,

        "static_function": """
            static void helper(void) {
                // Do something
            }
            """,

        "pointers": """
            void process_buffer(uint8* data, const uint32* length) {
                *data = 0;
            }
            """,

        "complex_declaration": """
            const uint8* get_buffer(const uint32 offset, void* context) {
                return NULL;
            }
            """,

        "nested_calls": """
            void complex_function(void) {
                initialize();
                if (condition) {
                    process_data();
                } else {
                    handle_error();
                }
                cleanup();
            }
            """,

        "function_pointer_param": """
            void register_callback(void (*callback)(int), int priority) {
                // Register callback
            }
            """,

        "array_parameter": """
            void process_array(int data[10], int size) {
                for (int i = 0; i < size; i++) {
                    data[i] *= 2;
                }
            }
            """,
    }

    return test_cases


def test_regex_parser(test_code: str):
    """Test with regex-based parser."""
    from autosar_calltree.parsers.c_parser import CParser

    parser = CParser()

    # Create temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write(test_code)
        temp_path = Path(f.name)

    try:
        functions = parser.parse_file(temp_path)
        return functions
    finally:
        temp_path.unlink(missing_ok=True)


def test_pycparser_parser(test_code: str):
    """Test with pycparser-based parser."""
    try:
        from autosar_calltree.parsers.c_parser_pycparser import CParserPyCParser
    except ImportError:
        return None

    parser = CParserPyCParser()

    # Create temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write(test_code)
        temp_path = Path(f.name)

    try:
        functions = parser.parse_file(temp_path)
        return functions
    finally:
        temp_path.unlink(missing_ok=True)


def format_function_info(func):
    """Format function info for display."""
    from autosar_calltree.database.models import FunctionInfo

    if not isinstance(func, FunctionInfo):
        return f"  {func}"

    lines = [
        f"  Function: {func.name}",
        f"    Return: {func.return_type}",
        f"    Static: {func.is_static}",
        f"    Type: {func.function_type.value}",
    ]

    if func.parameters:
        lines.append("    Parameters:")
        for param in func.parameters:
            ptr_str = "*" if param.is_pointer else ""
            lines.append(f"      - {param.param_type}{ptr_str} {param.name}")
    else:
        lines.append("    Parameters: (void)")

    if func.calls:
        lines.append(f"    Calls ({len(func.calls)}):")
        for call in func.calls:
            cond_str = " [conditional]" if call.is_conditional else ""
            loop_str = " [loop]" if call.is_loop else ""
            lines.append(f"      - {call.name}{cond_str}{loop_str}")

    return "\n".join(lines)


def compare_parsers():
    """Compare both parsers on various test cases."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax

    console = Console()
    test_cases = create_test_cases()

    console.print("\n[bold cyan]AUTOSAR Call Tree Analyzer - Parser Comparison[/bold cyan]\n")

    # Check which parsers are available
    pycparser_available = True
    try:
        from autosar_calltree.parsers.c_parser_pycparser import CParserPyCParser
    except ImportError:
        pycparser_available = False
        console.print("[yellow]⚠ pycparser not installed. Install with: pip install -e \".[parser]\"[/yellow]\n")

    for test_name, test_code in test_cases.items():
        console.print(Panel(
            Syntax(test_code, "c", theme="monokai", line_numbers=False),
            title=f"[bold green]Test Case: {test_name}[/bold green]",
            border_style="blue",
        ))

        # Test regex parser
        console.print("[bold yellow]Regex-based Parser:[/bold yellow]")
        try:
            regex_functions = test_regex_parser(test_code)
            if regex_functions:
                for func in regex_functions:
                    console.print(format_function_info(func))
            else:
                console.print("  [dim]No functions found[/dim]")
        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")

        console.print()

        # Test pycparser parser
        if pycparser_available:
            console.print("[bold yellow]pycparser-based Parser:[/bold yellow]")
            try:
                pyc_functions = test_pycparser_parser(test_code)
                if pyc_functions:
                    for func in pyc_functions:
                        console.print(format_function_info(func))
                else:
                    console.print("  [dim]No functions found[/dim]")
            except Exception as e:
                console.print(f"  [red]Error: {e}[/red]")

            console.print()

        console.print("=" * 80)
        console.print()

    # Summary
    console.print(Panel(
        "[bold]Summary:[/bold]\n\n"
        "• [cyan]Regex parser[/cyan]: Fast, no dependencies, but less accurate\n"
        "• [cyan]pycparser[/cyan]: Proper C parsing, handles complex cases\n\n"
        "[bold]Recommendation:[/bold] Use pycparser for production code analysis.\n"
        "Install with: [green]pip install -e \".[parser]\"[/green]\n",
        title="[bold]Parser Comparison Summary[/bold]",
        border_style="green",
    ))


if __name__ == "__main__":
    compare_parsers()
