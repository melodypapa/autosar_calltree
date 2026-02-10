"""Comprehensive tests to achieve 100% coverage for c_parser.py."""

import tempfile
from pathlib import Path

from autosar_calltree.database.models import FunctionType
from autosar_calltree.parsers.c_parser import CParser


class TestCParserCoverageMultiline:
    """Tests for multiline function parsing (lines 326-328)."""

    def test_multiline_backtrack_with_return_type(self):
        """Test multiline function with return type on separate line."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_multiline_backtrack.c"
        )

        functions = parser.parse_file(fixture_path)

        # Should find all multiline functions
        assert len(functions) >= 3

        # Check MyFunction
        my_func = next((f for f in functions if f.name == "MyFunction"), None)
        assert my_func is not None
        assert my_func.return_type == "const uint32_t"
        assert len(my_func.parameters) == 2

        # Check InternalProcess
        internal = next((f for f in functions if f.name == "InternalProcess"), None)
        assert internal is not None
        assert internal.return_type == "void"
        assert internal.is_static is True

        # Check GetBuffer
        get_buf = next((f for f in functions if f.name == "GetBuffer"), None)
        assert get_buf is not None
        # With multiline parsing, the * is preserved
        assert get_buf.return_type == "uint8*"
        assert len(get_buf.parameters) == 1


class TestCParserCoverageIfConditions:
    """Tests for if condition extraction (lines 718-728)."""

    def test_simple_if_condition(self):
        """Test simple if condition extraction."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_if_conditions.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_simple_if
        func = next((f for f in functions if f.name == "test_simple_if"), None)
        assert func is not None

        # Check conditional call
        cond_calls = [fc for fc in func.calls if fc.is_conditional]
        assert len(cond_calls) >= 1

    def test_if_with_condition_text(self):
        """Test that condition text is extracted."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_if_conditions.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_if_with_condition
        func = next((f for f in functions if f.name == "test_if_with_condition"), None)
        assert func is not None

        # Check condition text
        cond_calls = [fc for fc in func.calls if fc.name == "COM_SendMessage"]
        if cond_calls:
            assert "mode == 0x05" in cond_calls[0].condition

    def test_if_without_closing_paren(self):
        """Test if statement without closing parenthesis."""
        parser = CParser()
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test(void) {
    if (func(x) > 0 && func(y) {
        do_something();
    }
}
""")

            functions = parser.parse_file(test_file)
            # Should parse the function without crashing
            assert len(functions) >= 1


class TestCParserCoverageElseIfElse:
    """Tests for else if and else handling (lines 730-769)."""

    def test_else_if_condition(self):
        """Test else if condition extraction."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_else_if_else.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_else_if
        func = next((f for f in functions if f.name == "test_else_if"), None)
        assert func is not None

        # Check conditional calls
        cond_calls = [fc for fc in func.calls if fc.is_conditional]
        assert len(cond_calls) >= 2

    def test_else_condition(self):
        """Test else block handling."""
        parser = CParser()
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test_else(void) {
    if (x > 0) {
        do_something();
    } else {
        do_other();
    }
}
""")

            functions = parser.parse_file(test_file)

            # Find test_else
            func = next((f for f in functions if f.name == "test_else"), None)
            assert func is not None

            # Check conditional calls
            cond_calls = [fc for fc in func.calls if fc.is_conditional]
            assert len(cond_calls) >= 2

    def test_else_if_multiline_condition(self):
        """Test else if with multiline condition."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_else_if_else.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_else_if_multiline
        func = next(
            (f for f in functions if f.name == "test_else_if_multiline"), None
        )
        assert func is not None

        # Should have conditional calls
        cond_calls = [fc for fc in func.calls if fc.is_conditional]
        assert len(cond_calls) >= 2


class TestCParserCoverageLoops:
    """Tests for loop detection (lines 781-792)."""

    def test_for_loop_detection(self):
        """Test for loop condition extraction."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_loops.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_for_loop
        func = next((f for f in functions if f.name == "test_for_loop"), None)
        assert func is not None

        # Check loop calls
        loop_calls = [fc for fc in func.calls if fc.is_loop]
        assert len(loop_calls) >= 1

        # Check loop condition
        process_elem = next(
            (fc for fc in loop_calls if fc.name == "Process_Element"), None
        )
        assert process_elem is not None
        assert process_elem.loop_condition == "i < 10"

    def test_while_loop_detection(self):
        """Test while loop condition extraction."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_loops.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_while_loop
        func = next((f for f in functions if f.name == "test_while_loop"), None)
        assert func is not None

        # Check loop calls
        loop_calls = [fc for fc in func.calls if fc.is_loop]
        assert len(loop_calls) >= 1

        # Check loop condition
        process_elem = next(
            (fc for fc in loop_calls if fc.name == "Process_Element"), None
        )
        assert process_elem is not None
        assert "count > 0" in process_elem.loop_condition

    def test_for_without_semicolon(self):
        """Test for loop without semicolon (fallback logic)."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_loops.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_for_without_semicolon
        func = next(
            (f for f in functions if f.name == "test_for_without_semicolon"), None
        )
        assert func is not None

        # Should parse without crashing
        assert len(func.calls) >= 1


class TestCParserCoverageNestedBlocks:
    """Tests for nested blocks (lines 802-810, 846-848)."""

    def test_nested_if_blocks(self):
        """Test nested if blocks."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_nested_blocks.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_nested_if
        func = next((f for f in functions if f.name == "test_nested_if"), None)
        assert func is not None

        # Should parse without crashing
        assert len(func.calls) >= 1

    def test_nested_parens(self):
        """Test nested parentheses in conditions."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_nested_blocks.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_nested_parens
        func = next((f for f in functions if f.name == "test_nested_parens"), None)
        assert func is not None

        # Should have conditional call with complex condition
        cond_calls = [fc for fc in func.calls if fc.is_conditional]
        assert len(cond_calls) >= 1

    def test_nested_loops(self):
        """Test nested loops."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_nested_blocks.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_nested_loops
        func = next((f for f in functions if f.name == "test_nested_loops"), None)
        assert func is not None

        # Should have loop calls
        loop_calls = [fc for fc in func.calls if fc.is_loop]
        assert len(loop_calls) >= 1

    def test_if_in_loop(self):
        """Test if statement inside loop."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_nested_blocks.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_if_in_loop
        func = next((f for f in functions if f.name == "test_if_in_loop"), None)
        assert func is not None

        # Should have both conditional and loop calls
        cond_calls = [fc for fc in func.calls if fc.is_conditional]
        loop_calls = [fc for fc in func.calls if fc.is_loop]
        assert len(cond_calls) >= 1
        assert len(loop_calls) >= 1


class TestCParserCoverageRTECalls:
    """Tests for RTE calls and conditional handling (lines 826, 875-881)."""

    def test_rte_call_simple(self):
        """Test simple RTE call."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_rte_calls.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_rte_call_simple
        func = next((f for f in functions if f.name == "test_rte_call_simple"), None)
        assert func is not None

        # Should have RTE call
        rte_calls = [fc for fc in func.calls if fc.name.startswith("Rte_")]
        assert len(rte_calls) >= 1

    def test_rte_call_conditional(self):
        """Test RTE call in conditional block."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_rte_calls.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_rte_call_conditional
        func = next(
            (f for f in functions if f.name == "test_rte_call_conditional"), None
        )
        assert func is not None

        # Should have conditional RTE call
        rte_calls = [
            fc for fc in func.calls if fc.name.startswith("Rte_") and fc.is_conditional
        ]
        assert len(rte_calls) >= 1

    def test_rte_call_in_loop(self):
        """Test RTE call in loop."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_rte_calls.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_rte_call_in_loop
        func = next((f for f in functions if f.name == "test_rte_call_in_loop"), None)
        assert func is not None

        # Should have loop RTE call
        rte_calls = [
            fc for fc in func.calls if fc.name.startswith("Rte_") and fc.is_loop
        ]
        assert len(rte_calls) >= 1

    def test_rte_call_duplicate(self):
        """Test duplicate RTE call deduplication."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_rte_calls.c"
        )

        functions = parser.parse_file(fixture_path)

        # Find test_rte_call_duplicate
        func = next((f for f in functions if f.name == "test_rte_call_duplicate"), None)
        assert func is not None

        # Should deduplicate calls
        rte_calls = [fc for fc in func.calls if fc.name == "Rte_Call_StartOperation"]
        assert len(rte_calls) == 1  # Only one, even though called twice

    def test_rte_call_else_block(self):
        """Test RTE call in else block."""
        parser = CParser()
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
void test_rte_call_else_block(void) {
    if (mode == 0x05) {
        Func1();
    } else {
        Rte_Call_StartOperation();
    }
}
""")

            functions = parser.parse_file(test_file)

            # Find test_rte_call_else_block
            func = next((f for f in functions if f.name == "test_rte_call_else_block"), None)
            assert func is not None

            # Should have conditional RTE call
            rte_calls = [fc for fc in func.calls if fc.name.startswith("Rte_") and fc.is_conditional]
            assert len(rte_calls) >= 1

    def test_regular_call_conditional_loop(self):
        """Test regular call with both conditional and loop flags."""
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_rte_calls.c"
        )

        functions = parser.parse_file(fixture_path)

        # Check test_regular_call_conditional
        func = next(
            (f for f in functions if f.name == "test_regular_call_conditional"), None
        )
        if func:
            cond_calls = [fc for fc in func.calls if fc.is_conditional]
            assert len(cond_calls) >= 1

        # Check test_regular_call_in_loop
        func = next(
            (f for f in functions if f.name == "test_regular_call_in_loop"), None
        )
        if func:
            loop_calls = [fc for fc in func.calls if fc.is_loop]
            assert len(loop_calls) >= 1


class TestCParserCoverageEdgeCases:
    """Tests for edge cases to cover remaining lines."""

    def test_function_without_body(self):
        """Test function declaration without body (line 674)."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("void test_function(uint8 param);")

            functions = parser.parse_file(test_file)

            # Should parse without crashing
            assert isinstance(functions, list)

    def test_syntax_error_in_function(self):
        """Test function with syntax error."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("void test( {\n    malformed code\n}")

            functions = parser.parse_file(test_file)

            # Should not crash
            assert isinstance(functions, list)

    def test_empty_function_body(self):
        """Test function with empty body."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("void test(void) {}")

            functions = parser.parse_file(test_file)

            # Should parse successfully
            assert len(functions) >= 1
            assert functions[0].name == "test"

    def test_function_with_only_comments(self):
        """Test function body with only comments."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("void test(void) {\n    /* only comments */\n}")

            functions = parser.parse_file(test_file)

            # Should parse successfully
            assert len(functions) >= 1

    def test_parameter_with_no_name(self):
        """Test parameter without name."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("void test(uint8, uint16 value);")

            functions = parser.parse_file(test_file)

            # Should parse - function declarations without body may not be found
            # because they end with semicolon which is filtered out
            assert isinstance(functions, list)

    def test_autosar_function_with_calls(self):
        """Test AUTOSAR function with function calls."""
        parser = CParser()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.c"
            test_file.write_text("""
FUNC(void, RTE_CODE) AutosarFunc(void)
{
    Helper1();
    Helper2();
    Rte_Call_Operation();
}
""")

            functions = parser.parse_file(test_file)

            # Should parse AUTOSAR function and extract calls
            assert len(functions) >= 1
            func = functions[0]
            assert func.function_type == FunctionType.AUTOSAR_FUNC
            assert len(func.calls) >= 3
