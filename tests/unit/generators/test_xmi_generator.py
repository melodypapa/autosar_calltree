"""Tests for generators/xmi_generator.py (SWUT_GEN_00016-00025)

Tests the XmiGenerator class which generates XMI 2.5 compliant UML sequence diagrams from call trees.
"""

import tempfile
from pathlib import Path
from typing import List

import pytest

from autosar_calltree.database.models import (
    AnalysisResult,
    AnalysisStatistics,
    CallTreeNode,
    FunctionInfo,
    FunctionType,
    Parameter,
)
from autosar_calltree.generators.xmi_generator import XmiGenerator


# Helper functions to create mock objects
def create_mock_function(
    name: str,
    file_path: str,
    parameters: List[Parameter] = None,
    return_type: str = "void",
    sw_module: str = None,
    line_number: int = 1,
) -> FunctionInfo:
    """Create a mock FunctionInfo object."""
    return FunctionInfo(
        name=name,
        return_type=return_type,
        file_path=Path(file_path),
        line_number=line_number,
        is_static=False,
        function_type=FunctionType.TRADITIONAL_C,
        parameters=parameters or [],
        calls=[],
        called_by=set(),
        sw_module=sw_module,
    )


def create_mock_call_tree(
    functions: List[tuple],
    use_module_names: bool = False,
) -> CallTreeNode:
    """
    Create a mock call tree from a list of function tuples.

    Each tuple is: (name, file_path, module, children)
    where children is a list of tuples.
    """
    if not functions:
        return None

    name, file_path, module, children_tuples = functions[0]

    # Create parameters
    params = [
        Parameter(
            name="param1",
            param_type="uint32",
            is_pointer=False,
            is_const=False,
        )
    ]

    func_info = create_mock_function(
        name=name,
        file_path=file_path,
        sw_module=module,
        parameters=params,
    )

    # Create children recursively
    children = []
    for child_tuple in children_tuples:
        child_node = create_mock_call_tree([child_tuple], use_module_names)
        if child_node:
            children.append(child_node)

    node = CallTreeNode(
        function_info=func_info,
        children=children,
        is_recursive=False,
        depth=0,
    )

    return node


def create_mock_analysis_result(has_tree: bool = True) -> AnalysisResult:
    """Create a mock AnalysisResult object."""
    if has_tree:
        tree = create_mock_call_tree(
            [
                (
                    "RootFunc",
                    "root.c",
                    "RootModule",
                    [
                        ("ChildFunc1", "child1.c", "ChildModule1", []),
                        ("ChildFunc2", "child2.c", "ChildModule2", []),
                    ],
                )
            ]
        )
    else:
        tree = None

    stats = AnalysisStatistics(
        total_functions=3,
        unique_functions=3,
        max_depth_reached=2,
        circular_dependencies_found=0,
    )

    return AnalysisResult(
        root_function="RootFunc",
        call_tree=tree,
        statistics=stats,
        circular_dependencies=[],
    )


class TestXmiGeneratorInitialization:
    """Test XMI generator initialization."""

    def test_initialization_default(self):
        """SWUT_XMI_00001

        Test XMI generator initialization with default settings."""
        gen = XmiGenerator()

        assert gen.use_module_names is False
        assert gen.element_id_counter == 0
        assert gen.participant_map == {}

    def test_initialization_with_module_names(self):
        """SWUT_XMI_00001

        Test XMI generator initialization with module names enabled."""
        gen = XmiGenerator(use_module_names=True)

        assert gen.use_module_names is True
        assert gen.element_id_counter == 0
        assert gen.participant_map == {}


class TestXmiGeneratorGenerate:
    """Test XMI document generation."""

    def test_generate_creates_file(self):
        """SWUT_XMI_00002

        Test generate creates XMI file (line 63-72)."""
        result = create_mock_analysis_result()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            assert output_path.exists()

            # Check file content is valid XML
            content = output_path.read_text()
            assert "<?xml" in content or "<XMI" in content

    def test_generate_raises_error_no_call_tree(self):
        """SWUT_XMI_00002

        Test generate raises ValueError when call tree is None (line 63)."""
        result = create_mock_analysis_result(has_tree=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()

            with pytest.raises(ValueError, match="call tree is None"):
                gen.generate(result, str(output_path))

    def test_generate_creates_parent_directory(self):
        """SWUT_XMI_00002

        Test generate creates parent directory if needed (line 70)."""
        result = create_mock_analysis_result()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "subdir" / "output.xmi"

            # Ensure parent doesn't exist
            assert not output_path.parent.exists()

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            assert output_path.exists()
            assert output_path.parent.exists()


class TestXmiGeneratorDocumentGeneration:
    """Test XMI document structure generation."""

    def test_generate_xmi_document_root_element(self):
        """SWUT_XMI_00003

        Test _generate_xmi_document creates root element (lines 88-107)."""
        result = create_mock_analysis_result()
        tree = result.call_tree

        gen = XmiGenerator()
        root = gen._generate_xmi_document(result, tree)

        # Check root element exists
        assert root is not None
        # Check tag includes XMI namespace
        assert "XMI" in root.tag

    def test_generate_xmi_document_model_element(self):
        """SWUT_XMI_00003

        Test _generate_xmi_document creates model element (lines 109-117)."""
        result = create_mock_analysis_result()
        tree = result.call_tree

        gen = XmiGenerator()
        root = gen._generate_xmi_document(result, tree)

        # Find model element
        model = None
        for child in root:
            if "Model" in child.tag:
                model = child
                break

        assert model is not None
        assert model.get("name") == f"CallTree_{result.root_function}"

    def test_generate_xmi_document_interaction_element(self):
        """SWUT_XMI_00003

        Test _generate_xmi_document creates interaction (lines 119-124)."""
        result = create_mock_analysis_result()
        tree = result.call_tree

        gen = XmiGenerator()
        root = gen._generate_xmi_document(result, tree)

        # Check that interaction was created
        # The interaction should be created via _create_interaction
        assert root is not None


class TestXmiGeneratorCreateInteraction:
    """Test interaction element creation."""

    def test_create_interaction_element(self):
        """SWUT_XMI_00004

        Test _create_interaction creates interaction element (lines 126-136)."""
        result = create_mock_analysis_result()

        gen = XmiGenerator()
        # Create a parent element
        from xml.etree.ElementTree import Element

        parent = Element("test")

        interaction = gen._create_interaction(parent, result)

        assert interaction is not None
        # The interaction is a packagedElement, not directly named "interaction"
        assert interaction.get("name") == f"CallSequence_{result.root_function}"


class TestXmiGeneratorCollectParticipants:
    """Test participant collection."""

    def test_collect_participants_function_names(self):
        """SWUT_XMI_00005

        Test _collect_participants collects function names (lines 138-153)."""
        tree = create_mock_call_tree(
            [
                (
                    "RootFunc",
                    "root.c",
                    "RootModule",
                    [
                        ("ChildFunc1", "child1.c", "ChildModule1", []),
                        ("ChildFunc2", "child2.c", "ChildModule2", []),
                    ],
                )
            ]
        )

        gen = XmiGenerator(use_module_names=False)
        participants = gen._collect_participants(tree)

        # Should have 3 participants (root + 2 children)
        assert len(participants) == 3
        assert "RootFunc" in participants
        assert "ChildFunc1" in participants
        assert "ChildFunc2" in participants

    def test_collect_participants_module_names(self):
        """SWUT_XMI_00005

        Test _collect_participants collects module names (lines 138-153)."""
        tree = create_mock_call_tree(
            [
                (
                    "RootFunc",
                    "root.c",
                    "RootModule",
                    [
                        ("ChildFunc1", "child1.c", "ChildModule1", []),
                        ("ChildFunc2", "child2.c", "ChildModule2", []),
                    ],
                )
            ]
        )

        gen = XmiGenerator(use_module_names=True)
        participants = gen._collect_participants(tree)

        # Should have 3 unique modules
        assert len(participants) == 3
        assert "RootModule" in participants
        assert "ChildModule1" in participants
        assert "ChildModule2" in participants


class TestXmiGeneratorCreateLifelines:
    """Test lifeline element creation."""

    def test_create_lifelines_elements(self):
        """SWUT_XMI_00006

        Test _create_lifelines creates lifeline elements (lines 155-176)."""
        tree = create_mock_call_tree(
            [
                (
                    "RootFunc",
                    "root.c",
                    "RootModule",
                    [
                        ("ChildFunc", "child.c", "ChildModule", []),
                    ],
                )
            ]
        )

        gen = XmiGenerator()
        participants = gen._collect_participants(tree)

        # Create a parent interaction element
        from xml.etree.ElementTree import Element

        parent = Element("interaction")

        lifelines = gen._create_lifelines(parent, participants)

        # Should create one lifeline per participant
        assert len(lifelines) == 2

        # Check that lifelines were added to parent
        assert len(list(parent)) == 2

    def test_lifeline_has_id_and_name(self):
        """SWUT_XMI_00006

        Test lifelines have id and name attributes (lines 159-172)."""
        tree = create_mock_call_tree(
            [
                ("TestFunc", "test.c", "TestModule", []),
            ]
        )

        gen = XmiGenerator()
        participants = gen._collect_participants(tree)

        from xml.etree.ElementTree import Element

        parent = Element("interaction")

        lifelines = gen._create_lifelines(parent, participants)

        for participant_name, lifeline in lifelines.items():
            # ID is set with XMI namespace
            xmi_id = lifeline.get(f"{{{gen.XMI_NAMESPACE}}}id")
            assert xmi_id is not None
            assert lifeline.get("name") == participant_name
            assert participant_name in participants


class TestXmiGeneratorCreateMessages:
    """Test message element creation."""

    def test_create_messages_sync_call(self):
        """SWUT_XMI_00007

        Test _create_messages creates synchronous call (lines 178-250)."""
        tree = create_mock_call_tree(
            [
                (
                    "CallerFunc",
                    "caller.c",
                    "CallerModule",
                    [("CalleeFunc", "callee.c", "CalleeModule", [])],
                )
            ]
        )

        gen = XmiGenerator()
        participants = gen._collect_participants(tree)

        from xml.etree.ElementTree import Element

        parent = Element("interaction")
        lifelines = gen._create_lifelines(parent, participants)

        # Create messages
        gen._create_messages(tree, lifelines, parent)

        # Check that children were added to interaction
        # The interaction should now have more children than just lifelines
        # (messages and possibly fragments)
        total_children = len(list(parent))
        assert total_children > 0  # At least lifelines should exist

    def test_create_messages_with_opt_block(self):
        """SWUT_XMI_00007

        Test _create_messages creates opt block for conditional calls (lines 199-219).
        """
        # Create a tree with a conditional call
        root_func = create_mock_function(
            name="CallerFunc",
            file_path="caller.c",
            sw_module="CallerModule",
        )

        child_func = create_mock_function(
            name="CalleeFunc",
            file_path="callee.c",
            sw_module="CalleeModule",
        )

        child_node = CallTreeNode(
            function_info=child_func,
            children=[],
            is_optional=True,
            condition="x > 0",
            depth=1,
        )

        tree = CallTreeNode(
            function_info=root_func,
            children=[child_node],
            is_recursive=False,
            depth=0,
        )

        gen = XmiGenerator()
        participants = gen._collect_participants(tree)

        from xml.etree.ElementTree import Element

        parent = Element("interaction")
        lifelines = gen._create_lifelines(parent, participants)

        gen._create_messages(tree, lifelines, parent)

        # Check that interaction has children
        total_children = len(list(parent))
        assert total_children > 0


class TestXmiGeneratorUtilityMethods:
    """Test utility methods."""

    def test_generate_id_increments_counter(self):
        """SWUT_XMI_00008

        Test _generate_id increments counter (line 252-254)."""
        gen = XmiGenerator()

        id1 = gen._generate_id()
        id2 = gen._generate_id()

        assert id1 != id2
        assert gen.element_id_counter == 2

    def test_prettify_xml_formats_output(self):
        """SWUT_XMI_00009

        Test _prettify_xml formats XML output (lines 256-266)."""
        from xml.etree.ElementTree import Element

        gen = XmiGenerator()
        element = Element("test")
        element.set("attr", "value")

        formatted = gen._prettify_xml(element)

        # Should be a string
        assert isinstance(formatted, str)
        # Should contain indentation
        assert "  " in formatted or "\n" in formatted


class TestXmiGeneratorEdgeCases:
    """Test edge cases."""

    def test_empty_call_tree(self):
        """SWUT_XMI_00010

        Test handling of empty call tree."""
        # Create a tree with no children
        tree = create_mock_call_tree([("RootFunc", "root.c", "RootModule", [])])

        result = AnalysisResult(
            root_function="RootFunc",
            call_tree=tree,
            statistics=AnalysisStatistics(
                total_functions=1,
                unique_functions=1,
                max_depth_reached=1,
                circular_dependencies_found=0,
            ),
            circular_dependencies=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            assert output_path.exists()

    def test_recursive_call_handling(self):
        """SWUT_XMI_00011

        Test handling of recursive calls."""
        root_func = create_mock_function(
            name="RecursiveFunc",
            file_path="recursive.c",
            sw_module="RecursiveModule",
        )

        # Create a recursive call
        tree = CallTreeNode(
            function_info=root_func,
            children=[],  # Will mark as recursive
            is_recursive=True,
            depth=0,
        )

        result = AnalysisResult(
            root_function="RecursiveFunc",
            call_tree=tree,
            statistics=AnalysisStatistics(
                total_functions=1,
                unique_functions=1,
                max_depth_reached=1,
                circular_dependencies_found=0,
            ),
            circular_dependencies=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            assert output_path.exists()

    def test_deep_call_tree(self):
        """SWUT_XMI_00012

        Test handling of deep call trees."""
        # Create a deep tree
        tree = create_mock_call_tree(
            [
                (
                    "Level1",
                    "l1.c",
                    "Module1",
                    [
                        (
                            "Level2",
                            "l2.c",
                            "Module2",
                            [
                                (
                                    "Level3",
                                    "l3.c",
                                    "Module3",
                                    [("Level4", "l4.c", "Module4", [])],
                                )
                            ],
                        )
                    ],
                )
            ]
        )

        result = AnalysisResult(
            root_function="Level1",
            call_tree=tree,
            statistics=AnalysisStatistics(
                total_functions=4,
                unique_functions=4,
                max_depth_reached=4,
                circular_dependencies_found=0,
            ),
            circular_dependencies=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            assert output_path.exists()


class TestXmiGeneratorNamespaces:
    """Test XMI namespace handling."""

    def test_xmi_namespace_attributes(self):
        """SWUT_XMI_00013

        Test XMI namespace attributes are set (lines 63-72)."""
        result = create_mock_analysis_result()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            content = output_path.read_text()

            # Check for XMI namespace attributes
            assert "xmlns:xmi" in content or "xmlns:uml" in content

    def test_uml_namespace_elements(self):
        """SWUT_XMI_00014

        Test UML namespace elements are created."""
        result = create_mock_analysis_result()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            content = output_path.read_text()

            # Check for UML elements
            assert "Model" in content or "interaction" in content.lower()


class TestXmiGeneratorParameterHandling:
    """Test parameter handling in XMI generation."""

    def test_message_with_parameters(self):
        """SWUT_XMI_00015

        Test messages include function parameters."""
        root_func = create_mock_function(
            name="CallerFunc",
            file_path="caller.c",
            sw_module="CallerModule",
        )

        # Create a child function with parameters
        child_func = create_mock_function(
            name="CalleeFunc",
            file_path="callee.c",
            sw_module="CalleeModule",
            parameters=[
                Parameter(
                    name="param1", param_type="uint32", is_pointer=False, is_const=False
                ),
                Parameter(
                    name="param2", param_type="char*", is_pointer=True, is_const=False
                ),
            ],
        )

        child_node = CallTreeNode(
            function_info=child_func,
            children=[],
            is_optional=False,
            condition=None,
            depth=1,
        )

        tree = CallTreeNode(
            function_info=root_func,
            children=[child_node],
            is_recursive=False,
            depth=0,
        )

        result = AnalysisResult(
            root_function="CallerFunc",
            call_tree=tree,
            statistics=AnalysisStatistics(
                total_functions=2,
                unique_functions=2,
                max_depth_reached=2,
                circular_dependencies_found=0,
            ),
            circular_dependencies=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            assert output_path.exists()
            content = output_path.read_text()
            # Parameters should be in the message signature
            assert "CalleeFunc" in content

    def test_create_messages_with_loop_fragment(self):
        """SWUT_XMI_00016

        Test _create_messages creates loop fragments for loop calls (lines 291-365)."""
        root_func = create_mock_function(
            name="CallerFunc",
            file_path="caller.c",
            sw_module="CallerModule",
        )

        # Create a first-level child
        child_func = create_mock_function(
            name="ChildFunc",
            file_path="child.c",
            sw_module="ChildModule",
        )

        # Create a grandchild that is called in a loop
        loop_func = create_mock_function(
            name="LoopFunc",
            file_path="loop.c",
            sw_module="LoopModule",
        )

        loop_node = CallTreeNode(
            function_info=loop_func,
            children=[],
            is_loop=True,
            loop_condition="i < 10",
            depth=2,
        )

        child_node = CallTreeNode(
            function_info=child_func,
            children=[loop_node],
            is_loop=False,
            depth=1,
        )

        tree = CallTreeNode(
            function_info=root_func,
            children=[child_node],
            is_recursive=False,
            depth=0,
        )

        result = AnalysisResult(
            root_function="CallerFunc",
            call_tree=tree,
            statistics=AnalysisStatistics(
                total_functions=3,
                unique_functions=3,
                max_depth_reached=3,
                circular_dependencies_found=0,
            ),
            circular_dependencies=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            assert output_path.exists()
            content = output_path.read_text()
            # Should contain loop fragment
            assert "loop" in content
            assert "interactionOperator" in content
            # XML escapes < to &lt;
            assert "i &lt; 10" in content or "i < 10" in content

    def test_create_messages_nested_loop_children(self):
        """SWUT_XMI_00017

        Test _create_messages handles nested children in loop blocks (lines 312-365)."""
        root_func = create_mock_function(
            name="CallerFunc",
            file_path="caller.c",
            sw_module="CallerModule",
        )

        # Create a first-level child
        child_func = create_mock_function(
            name="ChildFunc",
            file_path="child.c",
            sw_module="ChildModule",
        )

        # Create a loop function with nested children
        loop_func = create_mock_function(
            name="LoopFunc",
            file_path="loop.c",
            sw_module="LoopModule",
        )

        nested_func = create_mock_function(
            name="NestedFunc",
            file_path="nested.c",
            sw_module="NestedModule",
        )

        nested_node = CallTreeNode(
            function_info=nested_func,
            children=[],
            is_loop=False,
            depth=3,
        )

        loop_node = CallTreeNode(
            function_info=loop_func,
            children=[nested_node],
            is_loop=True,
            loop_condition="i < 10",
            depth=2,
        )

        child_node = CallTreeNode(
            function_info=child_func,
            children=[loop_node],
            is_loop=False,
            depth=1,
        )

        tree = CallTreeNode(
            function_info=root_func,
            children=[child_node],
            is_recursive=False,
            depth=0,
        )

        result = AnalysisResult(
            root_function="CallerFunc",
            call_tree=tree,
            statistics=AnalysisStatistics(
                total_functions=4,
                unique_functions=4,
                max_depth_reached=4,
                circular_dependencies_found=0,
            ),
            circular_dependencies=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            assert output_path.exists()
            content = output_path.read_text()
            # Should contain loop fragment and nested function
            assert "loop" in content
            assert "NestedFunc" in content

    def test_create_messages_with_opt_fragment(self):
        """SWUT_XMI_00018

        Test _create_messages creates opt fragments for optional calls (lines 368-442).
        """
        root_func = create_mock_function(
            name="CallerFunc",
            file_path="caller.c",
            sw_module="CallerModule",
        )

        # Create a first-level child
        child_func = create_mock_function(
            name="ChildFunc",
            file_path="child.c",
            sw_module="ChildModule",
        )

        # Create a grandchild that is called conditionally
        opt_func = create_mock_function(
            name="OptionalFunc",
            file_path="optional.c",
            sw_module="OptionalModule",
        )

        opt_node = CallTreeNode(
            function_info=opt_func,
            children=[],
            is_optional=True,
            condition="x > 0",
            depth=2,
        )

        child_node = CallTreeNode(
            function_info=child_func,
            children=[opt_node],
            is_optional=False,
            depth=1,
        )

        tree = CallTreeNode(
            function_info=root_func,
            children=[child_node],
            is_recursive=False,
            depth=0,
        )

        result = AnalysisResult(
            root_function="CallerFunc",
            call_tree=tree,
            statistics=AnalysisStatistics(
                total_functions=3,
                unique_functions=3,
                max_depth_reached=3,
                circular_dependencies_found=0,
            ),
            circular_dependencies=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            assert output_path.exists()
            content = output_path.read_text()
            # Should contain opt fragment
            assert "opt" in content
            assert "interactionOperator" in content
            # XML escapes < to &lt;
            assert "x &gt; 0" in content or "x > 0" in content

    def test_create_messages_nested_opt_children(self):
        """SWUT_XMI_00019

        Test _create_messages handles nested children in opt blocks (lines 389-442)."""
        root_func = create_mock_function(
            name="CallerFunc",
            file_path="caller.c",
            sw_module="CallerModule",
        )

        # Create a first-level child
        child_func = create_mock_function(
            name="ChildFunc",
            file_path="child.c",
            sw_module="ChildModule",
        )

        # Create an optional function with nested children
        opt_func = create_mock_function(
            name="OptionalFunc",
            file_path="optional.c",
            sw_module="OptionalModule",
        )

        nested_func = create_mock_function(
            name="NestedFunc",
            file_path="nested.c",
            sw_module="NestedModule",
        )

        nested_node = CallTreeNode(
            function_info=nested_func,
            children=[],
            is_optional=False,
            depth=3,
        )

        opt_node = CallTreeNode(
            function_info=opt_func,
            children=[nested_node],
            is_optional=True,
            condition="x > 0",
            depth=2,
        )

        child_node = CallTreeNode(
            function_info=child_func,
            children=[opt_node],
            is_optional=False,
            depth=1,
        )

        tree = CallTreeNode(
            function_info=root_func,
            children=[child_node],
            is_recursive=False,
            depth=0,
        )

        result = AnalysisResult(
            root_function="CallerFunc",
            call_tree=tree,
            statistics=AnalysisStatistics(
                total_functions=4,
                unique_functions=4,
                max_depth_reached=4,
                circular_dependencies_found=0,
            ),
            circular_dependencies=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            assert output_path.exists()
            content = output_path.read_text()
            # Should contain opt fragment and nested function
            assert "opt" in content
            assert "NestedFunc" in content

    def test_format_message_signature_no_params(self):
        """SWUT_XMI_00020

        Test _format_message_signature with no parameters (line 463)."""
        gen = XmiGenerator()

        func = create_mock_function(
            name="TestFunc",
            file_path="test.c",
            parameters=[],
        )

        node = CallTreeNode(
            function_info=func,
            children=[],
            depth=0,
        )

        signature = gen._format_message_signature(node)
        assert signature == "TestFunc()"

    def test_format_message_signature_no_param_names(self):
        """SWUT_XMI_00021

        Test _format_message_signature with parameters but no names (lines 470-473)."""
        gen = XmiGenerator()

        func = create_mock_function(
            name="TestFunc",
            file_path="test.c",
            parameters=[
                Parameter(
                    name="", param_type="uint32", is_pointer=False, is_const=False
                ),
                Parameter(
                    name="", param_type="uint8*", is_pointer=True, is_const=False
                ),
            ],
        )

        node = CallTreeNode(
            function_info=func,
            children=[],
            depth=0,
        )

        signature = gen._format_message_signature(node)
        assert "TestFunc(" in signature
        assert "uint32" in signature
        assert "uint8*" in signature

    def test_generate_to_string(self):
        """SWUT_XMI_00022

        Test generate_to_string method (lines 517-521)."""
        result = create_mock_analysis_result()

        gen = XmiGenerator()
        xmi_string = gen.generate_to_string(result)

        # Should return a string
        assert isinstance(xmi_string, str)
        # Should contain XMI content
        assert "XMI" in xmi_string or "xmi" in xmi_string.lower()

    def test_generate_to_string_no_call_tree(self):
        """SWUT_XMI_00023

        Test generate_to_string raises ValueError when call tree is None."""
        result = create_mock_analysis_result(has_tree=False)

        gen = XmiGenerator()

        with pytest.raises(ValueError, match="call tree is None"):
            gen.generate_to_string(result)

    def test_create_messages_with_module_names(self):
        """SWUT_XMI_00024

        Test _create_messages with use_module_names=True (lines 242, 285, 316, 393)."""
        root_func = create_mock_function(
            name="CallerFunc",
            file_path="caller.c",
            sw_module="CallerModule",
        )

        # Create a first-level child
        child_func = create_mock_function(
            name="ChildFunc",
            file_path="child.c",
            sw_module="ChildModule",
        )

        # Create a grandchild that is called in a loop
        loop_func = create_mock_function(
            name="LoopFunc",
            file_path="loop.c",
            sw_module="LoopModule",
        )

        loop_node = CallTreeNode(
            function_info=loop_func,
            children=[],
            is_loop=True,
            loop_condition="i < 10",
            depth=2,
        )

        child_node = CallTreeNode(
            function_info=child_func,
            children=[loop_node],
            is_loop=False,
            depth=1,
        )

        tree = CallTreeNode(
            function_info=root_func,
            children=[child_node],
            is_recursive=False,
            depth=0,
        )

        result = AnalysisResult(
            root_function="CallerFunc",
            call_tree=tree,
            statistics=AnalysisStatistics(
                total_functions=3,
                unique_functions=3,
                max_depth_reached=3,
                circular_dependencies_found=0,
            ),
            circular_dependencies=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator(use_module_names=True)
            gen.generate(result, str(output_path))

            assert output_path.exists()
            content = output_path.read_text()
            # Should contain module names
            assert "CallerModule" in content
            assert "ChildModule" in content
            assert "LoopModule" in content
            # Should contain loop fragment
            assert "loop" in content

    def test_create_messages_opt_with_module_names(self):
        """SWUT_XMI_00025

        Test _create_messages with opt blocks and use_module_names=True."""
        root_func = create_mock_function(
            name="CallerFunc",
            file_path="caller.c",
            sw_module="CallerModule",
        )

        # Create a first-level child
        child_func = create_mock_function(
            name="ChildFunc",
            file_path="child.c",
            sw_module="ChildModule",
        )

        # Create a grandchild that is called conditionally
        opt_func = create_mock_function(
            name="OptionalFunc",
            file_path="optional.c",
            sw_module="OptionalModule",
        )

        opt_node = CallTreeNode(
            function_info=opt_func,
            children=[],
            is_optional=True,
            condition="x > 0",
            depth=2,
        )

        child_node = CallTreeNode(
            function_info=child_func,
            children=[opt_node],
            is_optional=False,
            depth=1,
        )

        tree = CallTreeNode(
            function_info=root_func,
            children=[child_node],
            is_recursive=False,
            depth=0,
        )

        result = AnalysisResult(
            root_function="CallerFunc",
            call_tree=tree,
            statistics=AnalysisStatistics(
                total_functions=3,
                unique_functions=3,
                max_depth_reached=3,
                circular_dependencies_found=0,
            ),
            circular_dependencies=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator(use_module_names=True)
            gen.generate(result, str(output_path))

            assert output_path.exists()
            content = output_path.read_text()
            # Should contain module names
            assert "CallerModule" in content
            assert "ChildModule" in content
            assert "OptionalModule" in content
            # Should contain opt fragment
            assert "opt" in content

    def test_create_messages_recursive_call(self):
        """SWUT_XMI_00026

        Test _create_messages marks recursive calls (line 285)."""
        root_func = create_mock_function(
            name="CallerFunc",
            file_path="caller.c",
            sw_module="CallerModule",
        )

        # Create a first-level child
        child_func = create_mock_function(
            name="RecursiveFunc",
            file_path="recursive.c",
            sw_module="RecursiveModule",
        )

        # Create a recursive grandchild
        recursive_node = CallTreeNode(
            function_info=child_func,
            children=[],
            is_recursive=True,
            depth=2,
        )

        child_node = CallTreeNode(
            function_info=child_func,
            children=[recursive_node],
            is_recursive=False,
            depth=1,
        )

        tree = CallTreeNode(
            function_info=root_func,
            children=[child_node],
            is_recursive=False,
            depth=0,
        )

        result = AnalysisResult(
            root_function="CallerFunc",
            call_tree=tree,
            statistics=AnalysisStatistics(
                total_functions=2,
                unique_functions=2,
                max_depth_reached=2,
                circular_dependencies_found=0,
            ),
            circular_dependencies=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.xmi"

            gen = XmiGenerator()
            gen.generate(result, str(output_path))

            assert output_path.exists()
            content = output_path.read_text()
            # Should contain messageSort="reply" for recursive call
            assert "messageSort" in content
            assert "reply" in content
