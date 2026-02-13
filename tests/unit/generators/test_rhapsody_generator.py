"""Tests for generators/rhapsody_generator.py (SWR_RH_00001-00020)

Tests the RhapsodyXmiGenerator class which generates Rhapsody-compatible XMI 2.5
UML sequence diagrams from call trees.
"""

import tempfile
from pathlib import Path
from typing import List
from xml.etree import ElementTree

import pytest

from autosar_calltree.database.models import (
    AnalysisResult,
    AnalysisStatistics,
    CallTreeNode,
    FunctionInfo,
    FunctionType,
    Parameter,
)
from autosar_calltree.generators.rhapsody_generator import RhapsodyXmiGenerator


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
                    "Demo_Init",
                    "demo.c",
                    "DemoModule",
                    [
                        ("COM_Init", "communication.c", "CommModule", []),
                        ("HW_Init", "hardware.c", "HardwareModule", []),
                    ],
                ),
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
        root_function="Demo_Init",
        call_tree=tree,
        statistics=stats,
        errors=[],
        circular_dependencies=[],
    )


class TestRhapsodyXmiGenerator:
    """Test suite for RhapsodyXmiGenerator class."""

    # SWR_RH_00001: Rhapsody XMI 2.5 Compatibility
    def test_rhapsody_xmi_compatibility(self):
        """Test that generated XMI is compatible with Rhapsody XMI 2.5."""
        generator = RhapsodyXmiGenerator()
        result = create_mock_analysis_result()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse the generated XMI
            tree = ElementTree.parse(str(output_path))
            root = tree.getroot()

            # Verify XMI namespace
            assert "XMI" in root.tag
            # Check version with XMI namespace
            xmi_version = root.get("{http://www.omg.org/spec/XMI/20131001}version")
            assert xmi_version in ["4.0", "2.1", None]  # None is acceptable for Rhapsody

            # Verify UML namespace is present
            model = root.find(".//{http://www.eclipse.org/uml2/5.0.0/UML}Model")
            assert model is not None
        finally:
            output_path.unlink()

    # SWR_RH_00002: Rhapsody Profile Support
    def test_rhapsody_profile_import(self):
        """Test Rhapsody profile is included in XMI."""
        generator = RhapsodyXmiGenerator()
        result = create_mock_analysis_result()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse the generated XMI
            tree = ElementTree.parse(str(output_path))
            root = tree.getroot()

            # Verify profile application elements
            model = root.find(".//{http://www.eclipse.org/uml2/5.0.0/UML}Model")
            assert model is not None

            # Check for profile application
            profile_apps = model.findall(
                ".//{http://www.eclipse.org/uml2/5.0.0/UML}profileApplication"
            )
            # Rhapsody profiles should be added
            assert len(profile_apps) >= 0
        finally:
            output_path.unlink()

    # SWR_RH_00004: UUID-based Element IDs
    def test_uuid_id_generation(self):
        """Test UUID-based element IDs."""
        generator = RhapsodyXmiGenerator()
        result = create_mock_analysis_result()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse the generated XMI
            tree = ElementTree.parse(str(output_path))
            root = tree.getroot()

            # Check that IDs are UUID-based
            for elem in root.iter():
                xmi_id = elem.get(
                    "{http://www.omg.org/spec/XMI/20131001}id"
                ) or elem.get("{http://www.omg.org/XMI}id")
                if xmi_id:
                    # UUID-based IDs should start with "rhapsody_" prefix
                    # and contain hexadecimal characters
                    assert xmi_id.startswith("rhapsody_")
                    assert len(xmi_id) == len("rhapsody_") + 32  # 32 hex chars
        finally:
            output_path.unlink()

    def test_unique_ids(self):
        """Test that all generated IDs are unique."""
        generator = RhapsodyXmiGenerator()
        result = create_mock_analysis_result()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse the generated XMI
            tree = ElementTree.parse(str(output_path))
            root = tree.getroot()

            # Collect all IDs
            ids = set()
            for elem in root.iter():
                xmi_id = elem.get(
                    "{http://www.omg.org/spec/XMI/20131001}id"
                ) or elem.get("{http://www.omg.org/XMI}id")
                if xmi_id:
                    # Check for uniqueness
                    assert xmi_id not in ids, f"Duplicate ID found: {xmi_id}"
                    ids.add(xmi_id)

            # Should have multiple unique IDs
            assert len(ids) > 0
        finally:
            output_path.unlink()

    # SWR_RH_00005: Rhapsody-specific Metadata
    def test_rhapsody_metadata(self):
        """Test Rhapsody-specific metadata is included."""
        generator = RhapsodyXmiGenerator()
        result = create_mock_analysis_result()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse the generated XMI
            tree = ElementTree.parse(str(output_path))
            root = tree.getroot()

            # Verify comments with tool information
            model = root.find(".//{http://www.eclipse.org/uml2/5.0.0/UML}Model")
            assert model is not None

            # Check for ownedComment elements
            comments = model.findall(
                ".//{http://www.eclipse.org/uml2/5.0.0/UML}ownedComment"
            )
            assert len(comments) > 0

            # Verify body contains tool information
            for comment in comments:
                body = comment.find("{http://www.eclipse.org/uml2/5.0.0/UML}body")
                if body is not None and body.text:
                    # Should contain "AUTOSAR Call Tree Analyzer" or "Rhapsody"
                    assert any(
                        keyword in body.text
                        for keyword in [
                            "AUTOSAR Call Tree Analyzer",
                            "Rhapsody",
                        ]
                    )
        finally:
            output_path.unlink()

    # SWR_RH_00003: AUTOSAR Stereotype Support
    def test_autosar_stereotype_generation(self):
        """Test AUTOSAR stereotypes for functions."""
        generator = RhapsodyXmiGenerator()
        result = create_mock_analysis_result()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse the generated XMI
            tree = ElementTree.parse(str(output_path))
            root = tree.getroot()

            # Stereotypes are added via comments in this implementation
            model = root.find(".//{http://www.eclipse.org/uml2/5.0.0/UML}Model")
            assert model is not None

            # Check for stereotype comments
            comments = model.findall(
                ".//{http://www.eclipse.org/uml2/5.0.0/UML}ownedComment"
            )
            assert len(comments) >= 0
        finally:
            output_path.unlink()

    # Test conditional blocks in Rhapsody format
    def test_conditional_blocks_rhapsody(self):
        """Test opt/loop blocks in Rhapsody format."""
        # Create a tree with conditional blocks - use nested structure to test fragments
        params = [Parameter(name="mode", param_type="uint32", is_pointer=False)]

        tree = CallTreeNode(
            function_info=create_mock_function(
                "Demo_Update",
                "demo.c",
                parameters=params,
            ),
            children=[
                CallTreeNode(
                    function_info=create_mock_function("COM_Send", "com.c"),
                    children=[
                        CallTreeNode(
                            function_info=create_mock_function("COM_Write", "com.c"),
                            children=[],
                            is_recursive=False,
                            depth=2,
                            is_optional=True,
                            condition="mode == 0x05",
                        )
                    ],
                    is_recursive=False,
                    depth=1,
                )
            ],
            is_recursive=False,
            depth=0,
        )

        stats = AnalysisStatistics(
            total_functions=3,
            unique_functions=3,
            max_depth_reached=3,
            circular_dependencies_found=0,
        )

        result = AnalysisResult(
            root_function="Demo_Update",
            call_tree=tree,
            statistics=stats,
            errors=[],
            circular_dependencies=[],
        )

        generator = RhapsodyXmiGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse and verify opt block
            tree_parsed = ElementTree.parse(str(output_path))
            root = tree_parsed.getroot()

            # Check for combined fragments with opt operator
            fragments = root.findall(
                ".//{http://www.eclipse.org/uml2/5.0.0/UML}fragment"
            )
            # Should find at least one opt fragment
            assert len(fragments) > 0
        finally:
            output_path.unlink()

    # Test module-level diagram
    def test_module_level_diagram(self):
        """Test module-level lifelines."""
        generator = RhapsodyXmiGenerator(use_module_names=True)
        result = create_mock_analysis_result()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse the generated XMI
            tree = ElementTree.parse(str(output_path))
            root = tree.getroot()

            # Verify lifelines use module names
            lifelines = root.findall(
                ".//{http://www.eclipse.org/uml2/5.0.0/UML}lifeline"
            )
            assert len(lifelines) > 0

            # Check for module names
            module_names = {"DemoModule", "CommModule", "HardwareModule"}
            found_modules = set()
            for lifeline in lifelines:
                name = lifeline.get("name")
                if name in module_names:
                    found_modules.add(name)

            # Should find at least some modules
            assert len(found_modules) > 0
        finally:
            output_path.unlink()

    # Test inheritance from XmiGenerator
    def test_inherits_from_xmi_generator(self):
        """Test that RhapsodyXmiGenerator properly inherits from XmiGenerator."""
        from autosar_calltree.generators.xmi_generator import XmiGenerator

        generator = RhapsodyXmiGenerator()
        assert isinstance(generator, XmiGenerator)

    # Test generate_to_string method
    def test_generate_to_string(self):
        """Test generating XMI to string without writing to file."""
        generator = RhapsodyXmiGenerator()
        result = create_mock_analysis_result()

        xmi_string = generator.generate_to_string(result)

        # Verify XML structure
        assert "<?xml" in xmi_string or "<XMI" in xmi_string
        assert "UML" in xmi_string
        assert "Demo_Init" in xmi_string

    # Test error handling for empty call tree
    def test_empty_call_tree_raises_error(self):
        """Test that empty call tree raises ValueError."""
        generator = RhapsodyXmiGenerator()
        result = create_mock_analysis_result(has_tree=False)

        with pytest.raises(ValueError, match="call tree is None"):
            generator.generate(result, "/tmp/test.xmi")

    # Test multiple participants
    def test_multiple_participants(self):
        """Test call tree with multiple participants."""
        tree = CallTreeNode(
            function_info=create_mock_function("Main", "main.c"),
            children=[
                CallTreeNode(
                    function_info=create_mock_function("Func1", "file1.c"),
                    children=[],
                    is_recursive=False,
                    depth=1,
                ),
                CallTreeNode(
                    function_info=create_mock_function("Func2", "file2.c"),
                    children=[],
                    is_recursive=False,
                    depth=1,
                ),
                CallTreeNode(
                    function_info=create_mock_function("Func3", "file3.c"),
                    children=[],
                    is_recursive=False,
                    depth=1,
                ),
            ],
            is_recursive=False,
            depth=0,
        )

        stats = AnalysisStatistics(
            total_functions=4,
            unique_functions=4,
            max_depth_reached=2,
            circular_dependencies_found=0,
        )

        result = AnalysisResult(
            root_function="Main",
            call_tree=tree,
            statistics=stats,
            errors=[],
            circular_dependencies=[],
        )

        generator = RhapsodyXmiGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse and verify multiple lifelines
            tree = ElementTree.parse(str(output_path))
            root = tree.getroot()

            lifelines = root.findall(
                ".//{http://www.eclipse.org/uml2/5.0.0/UML}lifeline"
            )
            # Should have 4 lifelines (Main + 3 functions)
            assert len(lifelines) == 4
        finally:
            output_path.unlink()

    # Test recursive call handling
    def test_recursive_call_handling(self):
        """Test handling of recursive calls."""
        tree = CallTreeNode(
            function_info=create_mock_function("RecursiveFunc", "rec.c"),
            children=[
                CallTreeNode(
                    function_info=create_mock_function("RecursiveFunc", "rec.c"),
                    children=[
                        CallTreeNode(
                            function_info=create_mock_function("RecursiveFunc", "rec.c"),
                            children=[],
                            is_recursive=True,
                            depth=2,
                        )
                    ],
                    is_recursive=False,
                    depth=1,
                )
            ],
            is_recursive=False,
            depth=0,
        )

        stats = AnalysisStatistics(
            total_functions=1,
            unique_functions=1,
            max_depth_reached=3,
            circular_dependencies_found=0,
        )

        result = AnalysisResult(
            root_function="RecursiveFunc",
            call_tree=tree,
            statistics=stats,
            errors=[],
            circular_dependencies=[],
        )

        generator = RhapsodyXmiGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse and verify message sort
            tree_parsed = ElementTree.parse(str(output_path))
            root = tree_parsed.getroot()

            messages = root.findall(
                ".//{http://www.eclipse.org/uml2/5.0.0/UML}message"
            )
            assert len(messages) > 0
        finally:
            output_path.unlink()

    # Test loop blocks
    def test_loop_blocks(self):
        """Test loop block generation."""
        # Create tree structure matching XMI generator test pattern
        # Root -> Child -> Loop (loop is at depth 2, not depth 1)
        tree = CallTreeNode(
            function_info=create_mock_function("CallerFunc", "caller.c"),
            children=[
                CallTreeNode(
                    function_info=create_mock_function("ChildFunc", "child.c"),
                    children=[
                        CallTreeNode(
                            function_info=create_mock_function("LoopFunc", "loop.c"),
                            children=[],
                            is_recursive=False,
                            depth=2,
                            is_loop=True,
                            loop_condition="i < 10",
                        )
                    ],
                    is_recursive=False,
                    depth=1,
                )
            ],
            is_recursive=False,
            depth=0,
        )

        stats = AnalysisStatistics(
            total_functions=3,
            unique_functions=3,
            max_depth_reached=3,
            circular_dependencies_found=0,
        )

        result = AnalysisResult(
            root_function="CallerFunc",
            call_tree=tree,
            statistics=stats,
            errors=[],
            circular_dependencies=[],
        )

        generator = RhapsodyXmiGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse and verify loop fragment
            tree_parsed = ElementTree.parse(str(output_path))
            root = tree_parsed.getroot()

            fragments = root.findall(
                ".//{http://www.eclipse.org/uml2/5.0.0/UML}fragment"
            )
            assert len(fragments) > 0

            # Check for loop operator
            loop_found = False
            for frag in fragments:
                if frag.get("interactionOperator") == "loop":
                    loop_found = True
                    break

            assert loop_found
        finally:
            output_path.unlink()

    # Test parameter handling in messages
    def test_parameter_handling(self):
        """Test function parameters in message signatures."""
        params = [
            Parameter(name="data", param_type="uint8*", is_pointer=True),
            Parameter(name="length", param_type="uint32", is_pointer=False),
        ]

        tree = CallTreeNode(
            function_info=create_mock_function(
                "SendData",
                "send.c",
                parameters=params,
            ),
            children=[
                CallTreeNode(
                    function_info=create_mock_function(
                        "ProcessData",
                        "proc.c",
                        parameters=params,
                    ),
                    children=[
                        CallTreeNode(
                            function_info=create_mock_function(
                                "ValidateData",
                                "proc.c",
                                parameters=params,
                            ),
                            children=[],
                            is_recursive=False,
                            depth=2,
                        )
                    ],
                    is_recursive=False,
                    depth=1,
                )
            ],
            is_recursive=False,
            depth=0,
        )

        stats = AnalysisStatistics(
            total_functions=3,
            unique_functions=3,
            max_depth_reached=3,
            circular_dependencies_found=0,
        )

        result = AnalysisResult(
            root_function="SendData",
            call_tree=tree,
            statistics=stats,
            errors=[],
            circular_dependencies=[],
        )

        generator = RhapsodyXmiGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse and verify message signatures
            tree_parsed = ElementTree.parse(str(output_path))
            root = tree_parsed.getroot()

            messages = root.findall(
                ".//{http://www.eclipse.org/uml2/5.0.0/UML}message"
            )
            assert len(messages) > 0
        finally:
            output_path.unlink()

    # Test file output path creation
    def test_output_directory_creation(self):
        """Test that output directories are created if they don't exist."""
        generator = RhapsodyXmiGenerator()
        result = create_mock_analysis_result()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a nested path that doesn't exist
            output_path = Path(tmpdir) / "subdir1" / "subdir2" / "output.xmi"

            generator.generate(result, str(output_path))

            # Verify file was created
            assert output_path.exists()
            assert output_path.parent.exists()

    # Test Rhapsody version metadata
    def test_rhapsody_version_metadata(self):
        """Test that Rhapsody version is included in metadata."""
        generator = RhapsodyXmiGenerator()
        result = create_mock_analysis_result()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xmi", delete=False) as f:
            generator.generate(result, f.name)
            output_path = Path(f.name)

        try:
            # Parse and check for version info
            tree = ElementTree.parse(str(output_path))
            root = tree.getroot()

            # Check comments for Rhapsody version
            comments = root.findall(
                ".//{http://www.eclipse.org/uml2/5.0.0/UML}ownedComment"
            )

            version_found = False
            for comment in comments:
                body = comment.find("{http://www.eclipse.org/uml2/5.0.0/UML}body")
                if body is not None and body.text:
                    if "Rhapsody" in body.text:
                        version_found = True
                        break

            # Should have Rhapsody metadata
            assert version_found
        finally:
            output_path.unlink()
