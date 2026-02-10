"""Tests to cover remaining missing lines in c_parser.py.

This file targets specific uncovered lines:
- 326-328: Multiline function with non-type return type line
- 440: Function with C keyword as return type
- 458: Function with control structure as name
- 730-766: else if with multiline condition
- 788: for loop without semicolon (fallback)
- 805-806: while loop fallback without closing paren
- 826: RTE call update existing with conditional
- 846-848: nested blocks with brace depth
- 875: function call with AUTOSAR type name
- 879-881: RTE call update loop condition
"""

from pathlib import Path

from autosar_calltree.parsers.c_parser import CParser


class TestCParserRemainingLines:
    """Tests for the remaining uncovered lines in c_parser.py."""

    def test_line_326_328_multiline_with_non_type_return_type(self):
        r"""Test multiline function with struct type (lines 326-328).

        This triggers the else: break branch when prev_line
        doesn't match ^[\w\s\*]+$ pattern.
        """
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_remaining.c"
        )

        functions = parser.parse_file(fixture_path)

        # Should find the multiline function
        func = next(
            (f for f in functions if f.name == "multiline_with_struct"), None
        )
        assert func is not None
        assert func.return_type == "struct ComplexType"

    def test_line_440_c_keyword_as_return_type(self):
        """Test function with C keyword as return type (line 440).

        Tests the 'if return_type in self.C_KEYWORDS' check by directly
        calling _parse_function_match with crafted input.
        """
        parser = CParser()

        # Create a match that would have 'if' as return_type
        # This is a synthetic scenario to test the code path
        test_declaration = "if TestFunction(void) { return; }"

        # Use the function_pattern to get a match
        match = parser.function_pattern.search(test_declaration)
        if match:
            result = parser._parse_function_match(match, test_declaration, Path("test.c"))
            # Should return None because 'if' is a C keyword
            assert result is None

    def test_line_458_control_structure_as_function_name(self):
        """Test function with control structure as name (line 458).

        Tests the 'if function_name in ["if", "for", "while", ...]' check.
        """
        parser = CParser()

        # Create a match that would have 'if' as function name
        test_declaration = "void if(void) { return; }"

        # Use the function_pattern to get a match
        match = parser.function_pattern.search(test_declaration)
        if match:
            result = parser._parse_function_match(match, test_declaration, Path("test.c"))
            # Should return None because 'if' is a control structure
            assert result is None

    def test_line_730_766_else_if_multiline_condition(self):
        """Test else if with multiline condition (lines 730-766).

        Tests the multi-line condition collection for else if statements.
        """
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_remaining.c"
        )

        functions = parser.parse_file(fixture_path)

        func = next(
            (f for f in functions if f.name == "test_else_if_multiline_condition"),
            None,
        )
        assert func is not None

        # Should have conditional calls
        cond_calls = [fc for fc in func.calls if fc.is_conditional]
        assert len(cond_calls) >= 2

    def test_line_788_for_loop_no_semicolon(self):
        """Test for loop without semicolon (line 788).

        Tests the fallback 'else: current_loop_condition = "condition"' branch.
        """
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_remaining.c"
        )

        functions = parser.parse_file(fixture_path)

        func = next((f for f in functions if f.name == "test_for_no_semicolon"), None)
        assert func is not None

        # Should parse without crashing
        assert len(func.calls) >= 1

    def test_line_805_806_while_loop_no_closing_paren(self):
        """Test while loop without closing paren (lines 805-806).

        Tests the fallback 'else: current_loop_condition = "condition"' branch
        in while loop parsing.
        """
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_remaining.c"
        )

        functions = parser.parse_file(fixture_path)

        func = next(
            (f for f in functions if f.name == "test_while_no_closing_paren"), None
        )
        assert func is not None

        # Should parse without crashing
        assert len(func.calls) >= 1

    def test_line_826_rte_update_conditional(self):
        """Test RTE call update with conditional (line 826).

        Tests updating existing RTE call with conditional flag.
        """
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_remaining.c"
        )

        functions = parser.parse_file(fixture_path)

        func = next((f for f in functions if f.name == "test_rte_update_conditional"), None)
        assert func is not None

        # Should have only one RTE call (deduplicated)
        rte_calls = [fc for fc in func.calls if fc.name == "Rte_Call_StartOperation"]
        assert len(rte_calls) == 1

        # But it should be marked as conditional
        assert rte_calls[0].is_conditional is True

    def test_line_846_848_nested_blocks_depth(self):
        """Test nested blocks with brace depth (lines 846-848).

        Tests brace depth tracking with nested braces.
        """
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_remaining.c"
        )

        functions = parser.parse_file(fixture_path)

        func = next((f for f in functions if f.name == "test_nested_blocks_depth"), None)
        assert func is not None

        # Should parse without crashing
        assert len(func.calls) >= 1

    def test_line_875_autosar_type_as_call(self):
        """Test function call with AUTOSAR type name (line 875).

        Tests 'if function_name in self.AUTOSAR_TYPES' check.
        """
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_remaining.c"
        )

        functions = parser.parse_file(fixture_path)

        func = next((f for f in functions if f.name == "test_autosar_type_as_call"), None)
        assert func is not None

        # 'uint8' is AUTOSAR type, should not be detected as function call
        uint8_call = next((fc for fc in func.calls if fc.name == "uint8"), None)
        assert uint8_call is None

        # Func1 should be detected
        func1_call = next((fc for fc in func.calls if fc.name == "Func1"), None)
        assert func1_call is not None

    def test_line_879_881_rte_update_loop(self):
        """Test RTE call update with loop (lines 879-881).

        Tests updating existing RTE call with loop flag.
        """
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_remaining.c"
        )

        functions = parser.parse_file(fixture_path)

        func = next((f for f in functions if f.name == "test_rte_update_loop"), None)
        assert func is not None

        # Should have only one RTE call (deduplicated)
        rte_calls = [fc for fc in func.calls if fc.name == "Rte_Call_Process"]
        assert len(rte_calls) == 1

        # But it should be marked as in loop
        assert rte_calls[0].is_loop is True

    def test_combined_conditional_loop_on_rte(self):
        """Test RTE call with both conditional and loop flags.

        Tests all the update logic paths.
        """
        parser = CParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "traditional_c"
            / "coverage_remaining.c"
        )

        functions = parser.parse_file(fixture_path)

        func = next((f for f in functions if f.name == "test_rte_conditional_loop"), None)
        assert func is not None

        # Should have RTE call
        rte_calls = [fc for fc in func.calls if fc.name == "Rte_Call_Operation"]
        assert len(rte_calls) == 1

        # Should have both conditional and loop flags
        assert rte_calls[0].is_conditional is True
        assert rte_calls[0].is_loop is True
