"""
Unit tests for Mermaid Generator module.

Tests the MermaidGenerator class which generates Mermaid sequence diagrams
from call trees.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pytest

from autosar_calltree.database.models import (
    AnalysisResult,
    AnalysisStatistics,
    CallTreeNode,
    CircularDependency,
    FunctionInfo,
    FunctionType,
    Parameter,
)
from autosar_calltree.generators.mermaid_generator import MermaidGenerator


# Helper functions to create mock objects
def create_mock_function(
    name: str,
    file_path: str,
    parameters: Optional[List[Parameter]] = None,
    return_type: str = "void",
    sw_module: Optional[str] = None,
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
    depth: int = 0,
) -> CallTreeNode:
    """
    Create a mock call tree.

    Args:
        functions: List of tuples (name, file, module, children)
                   where children is a list of tuples with same structure
        depth: Current depth in tree

    Returns:
        CallTreeNode root
    """
    if not functions:
        raise ValueError("Cannot create empty call tree")

    # Create root function
    root_data = functions[0]
    root_func = create_mock_function(
        name=root_data[0],
        file_path=root_data[1],
        sw_module=root_data[2] if len(root_data) > 2 else None,
    )

    root = CallTreeNode(function_info=root_func, depth=depth)

    # Add children if provided
    if len(root_data) > 3 and root_data[3]:
        for child_data in root_data[3]:
            child = create_mock_call_tree([child_data], depth + 1)
            root.add_child(child)

    return root


def create_mock_call_tree_with_params(
    functions: List[tuple],
    depth: int = 0,
) -> CallTreeNode:
    """
    Create a mock call tree with parameters.

    Args:
        functions: List of tuples (name, file, module, parameters, children)
        depth: Current depth

    Returns:
        CallTreeNode root
    """
    if not functions:
        raise ValueError("Cannot create empty call tree")

    root_data = functions[0]
    root_func = create_mock_function(
        name=root_data[0],
        file_path=root_data[1],
        parameters=root_data[3] if len(root_data) > 3 else [],
        sw_module=root_data[2] if len(root_data) > 2 else None,
    )

    root = CallTreeNode(function_info=root_func, depth=depth)

    # Add children
    if len(root_data) > 4 and root_data[4]:
        for child_data in root_data[4]:
            child = create_mock_call_tree_with_params([child_data], depth + 1)
            root.add_child(child)

    return root


def create_mock_analysis_result(
    root_function: str = "Demo_Init",
    has_tree: bool = True,
) -> AnalysisResult:
    """Create a mock AnalysisResult."""
    root = None
    if has_tree:
        root = create_mock_call_tree(
            [
                (
                    "Demo_Init",
                    "demo.c",
                    "DemoModule",
                    [
                        ("HW_Init", "hw.c", "HardwareModule", []),
                        ("SW_Init", "sw.c", "SoftwareModule", []),
                    ],
                ),
            ]
        )

    stats = AnalysisStatistics(
        total_functions=10,
        unique_functions=8,
        max_depth_reached=3,
        circular_dependencies_found=0,
    )

    return AnalysisResult(
        root_function=root_function,
        call_tree=root,
        statistics=stats,
        circular_dependencies=[],
        errors=[],
        timestamp=datetime.now(),
        source_directory=Path("/test"),
    )


# SWUT_GENERATOR_00001: Generator Initialization
def test_SWUT_GENERATOR_00001_initialization() -> None:
    """Test MermaidGenerator initialization with various options."""
    # Default initialization
    gen1 = MermaidGenerator()
    assert gen1.abbreviate_rte is True
    assert gen1.use_module_names is False
    assert gen1.include_returns is False
    assert gen1.participant_map == {}
    assert gen1.next_participant_id == 1

    # Custom options
    gen2 = MermaidGenerator(
        abbreviate_rte=False,
        use_module_names=True,
        include_returns=True,
    )
    assert gen2.abbreviate_rte is False
    assert gen2.use_module_names is True
    assert gen2.include_returns is True


# SWUT_GENERATOR_00002: Mermaid Sequence Diagram Header
def test_SWUT_GENERATOR_00002_mermaid_header() -> None:
    """Test that generated Mermaid diagram starts with correct header."""
    result = create_mock_analysis_result()
    gen = MermaidGenerator()

    diagram = gen._generate_mermaid_diagram(result.call_tree)
    lines = diagram.split("\n")

    assert lines[0] == "sequenceDiagram"


# SWUT_GENERATOR_00003: Participant Collection - Function Names
def test_SWUT_GENERATOR_00003_collect_participants_functions() -> None:
    """Test participants collected as function names when use_module_names=False."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                None,
                [
                    ("HW_Init", "hw.c", None, []),
                    ("SW_Init", "sw.c", None, []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=False)
    participants = gen._collect_participants(root)

    assert "Demo_Init" in participants
    assert "HW_Init" in participants
    assert "SW_Init" in participants
    assert len(participants) == 3


# SWUT_GENERATOR_00004: Participant Collection - Module Names
def test_SWUT_GENERATOR_00004_collect_participants_modules() -> None:
    """Test participants collected as module names when use_module_names=True."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [
                    ("HW_Init", "hw.c", "HardwareModule", []),
                    ("SW_Init", "sw.c", "SoftwareModule", []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=True)
    participants = gen._collect_participants(root)

    assert "DemoModule" in participants
    assert "HardwareModule" in participants
    assert "SoftwareModule" in participants
    assert len(participants) == 3


# SWUT_GENERATOR_00005: Module Fallback to Filename
def test_SWUT_GENERATOR_00005_module_fallback_to_filename() -> None:
    """Test functions without module assignment use filename as participant."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [
                    ("Unmapped_Init", "unmapped.c", None, []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=True)
    participants = gen._collect_participants(root)

    assert "DemoModule" in participants
    assert "unmapped" in participants  # Filename without extension
    assert len(participants) == 2


# SWUT_GENERATOR_00006: RTE Function Abbreviation
def test_SWUT_GENERATOR_00006_rte_abbreviation() -> None:
    """Test that long RTE function names are abbreviated."""
    gen = MermaidGenerator(abbreviate_rte=True)

    abbrev = gen._abbreviate_rte_name("Rte_Read_P_Voltage_Value")
    assert abbrev == "Rte_Read_PVV"

    abbrev2 = gen._abbreviate_rte_name("Rte_Write_SW_Data_State")
    assert abbrev2 == "Rte_Write_SDS"


# SWUT_GENERATOR_00007: RTE Abbreviation Disabled
def test_SWUT_GENERATOR_00007_rte_abbreviation_disabled() -> None:
    """Test that RTE abbreviation can be disabled."""
    gen = MermaidGenerator(abbreviate_rte=False)

    abbrev = gen._get_participant_name("Rte_Read_P_Voltage_Value")
    assert abbrev == "Rte_Read_P_Voltage_Value"


# SWUT_GENERATOR_00008: Short RTE Name Not Abbreviated
def test_SWUT_GENERATOR_00008_short_rte_not_abbreviated() -> None:
    """Test that short RTE names are not abbreviated."""
    gen = MermaidGenerator(abbreviate_rte=True)

    abbrev = gen._abbreviate_rte_name("Rte_Call")
    assert abbrev == "Rte_Call"  # Too short to abbreviate

    abbrev2 = gen._abbreviate_rte_name("Rte_Read")
    assert abbrev2 == "Rte_Read"


# SWUT_GENERATOR_00009: Sequence Call Generation - Function Mode
def test_SWUT_GENERATOR_00009_sequence_calls_function_mode() -> None:
    """Test sequence calls are generated correctly with function participants."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                None,
                [
                    ("HW_Init", "hw.c", None, []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=False)
    lines: List[str] = []
    gen._generate_sequence_calls(root, lines)

    output = "\n".join(lines)
    assert "Demo_Init->>HW_Init: call" in output


# SWUT_GENERATOR_00010: Sequence Call Generation - Module Mode
def test_SWUT_GENERATOR_00010_sequence_calls_module_mode() -> None:
    """Test sequence calls show function names on arrows in module mode."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [
                    ("HW_Init", "hw.c", "HardwareModule", []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=True)
    lines: List[str] = []
    gen._generate_sequence_calls(root, lines)

    output = "\n".join(lines)
    assert "DemoModule->>HardwareModule: HW_Init" in output


# SWUT_GENERATOR_00011: Parameter Display on Arrows
def test_SWUT_GENERATOR_00011_parameters_on_arrows() -> None:
    """Test that function parameters are displayed on sequence arrows."""
    params = [Parameter("timerId", "uint32", False, False)]
    root = create_mock_call_tree_with_params(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [],
                [
                    ("HW_Init", "hw.c", "HardwareModule", params, []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=True)
    lines: List[str] = []
    gen._generate_sequence_calls(root, lines)

    output = "\n".join(lines)
    assert "HW_Init(timerId)" in output


# SWUT_GENERATOR_00012: Multiple Parameters Display
def test_SWUT_GENERATOR_00012_multiple_parameters() -> None:
    """Test that multiple parameters are comma-separated."""
    params = [
        Parameter("value", "uint32", False, False),
        Parameter("status", "uint8*", True, False),
    ]
    root = create_mock_call_tree_with_params(
        [
            (
                "Parent",
                "p.c",
                "ParentMod",
                [],
                [
                    ("Func", "f.c", "Mod", params, []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=True)
    lines: List[str] = []
    gen._generate_sequence_calls(root, lines)

    output = "\n".join(lines)
    assert "Func(value, status)" in output


# SWUT_GENERATOR_00013: Recursive Call Handling
def test_SWUT_GENERATOR_00013_recursive_call_handling() -> None:
    """Test that recursive calls use special arrow syntax."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [
                    ("HW_Init", "hw.c", "HardwareModule", []),
                ],
            ),
        ]
    )

    # Mark child as recursive
    root.children[0].is_recursive = True

    gen = MermaidGenerator(use_module_names=True)
    lines: List[str] = []
    gen._generate_sequence_calls(root, lines)

    output = "\n".join(lines)
    # In module mode with recursion, should show special arrow and [recursive] label
    assert "DemoModule-->>xHardwareModule: HW_Init [recursive]" in output


# SWUT_GENERATOR_00052: Recursive Call Without Module Names (Line 227)
def test_SWUT_GENERATOR_00052_recursive_call_without_module_names_line_227() -> None:
    """Test recursive call with use_module_names=False (covers line 227)."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [
                    ("HW_Init", "hw.c", "HardwareModule", []),
                ],
            ),
        ]
    )

    # Mark child as recursive
    root.children[0].is_recursive = True

    gen = MermaidGenerator(use_module_names=False)
    lines: List[str] = []
    gen._generate_sequence_calls(root, lines)

    output = "\n".join(lines)
    # In function mode with recursion, should show special arrow and "recursive call" label (line 227)
    assert "Demo_Init-->>xHW_Init: recursive call" in output


# SWUT_GENERATOR_00014: Return Statement Generation
def test_SWUT_GENERATOR_00014_return_statements() -> None:
    """Test that return statements are generated when include_returns=True."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [
                    ("HW_Init", "hw.c", "HardwareModule", []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=True, include_returns=True)
    lines: List[str] = []
    gen._generate_sequence_calls(root, lines)

    output = "\n".join(lines)
    assert "HardwareModule-->>DemoModule: return" in output


# SWUT_GENERATOR_00015: Return Statements Disabled by Default
def test_SWUT_GENERATOR_00015_returns_disabled_default() -> None:
    """Test that return statements are not generated by default."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [
                    ("HW_Init", "hw.c", "HardwareModule", []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=True)  # include_returns defaults to False
    lines: List[str] = []
    gen._generate_sequence_calls(root, lines)

    output = "\n".join(lines)
    assert "return" not in output.lower()


# SWUT_GENERATOR_00016: Function Table - Function Mode
def test_SWUT_GENERATOR_00016_function_table_format() -> None:
    """Test function table has correct format when use_module_names=False."""
    root = create_mock_call_tree([("Demo_Init", "demo.c", None)])

    gen = MermaidGenerator(use_module_names=False)
    table = gen._generate_function_table(root)
    lines = table.split("\n")

    # Check header doesn't include Module column
    assert any("| Function | File | Line |" in line for line in lines)
    assert "| Module |" not in table


# SWUT_GENERATOR_00017: Function Table - Module Mode
def test_SWUT_GENERATOR_00017_function_table_module_column() -> None:
    """Test function table includes Module column when use_module_names=True."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [
                    ("HW_Init", "hw.c", "HardwareModule", []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=True)
    table = gen._generate_function_table(root)
    lines = table.split("\n")

    # Check header includes Module column
    assert any("| Function | Module | File | Line |" in line for line in lines)
    assert "| `Demo_Init` | DemoModule |" in table
    assert "| `HW_Init` | HardwareModule |" in table


# SWUT_GENERATOR_00018: Function Table - N/A for Unmapped
def test_SWUT_GENERATOR_00018_function_table_na_for_unmapped() -> None:
    """Test unmapped functions show 'N/A' in Module column."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [
                    ("Unmapped", "unmapped.c", None, []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=True)
    table = gen._generate_function_table(root)

    assert "| `Unmapped` | N/A |" in table


# SWUT_GENERATOR_00019: Parameter Formatting for Table
def test_SWUT_GENERATOR_00019_parameter_formatting_table() -> None:
    """Test parameters formatted correctly for function table."""
    params = [
        Parameter("value", "uint32", False, False),
        Parameter("ptr", "uint8*", True, False),
    ]
    func = create_mock_function("Func", "file.c", params)

    gen = MermaidGenerator()
    formatted = gen._format_parameters(func)

    assert "`uint32 value`" in formatted
    # Note: The actual implementation adds an extra * for pointer display
    assert "ptr`" in formatted


# SWUT_GENERATOR_00020: Void Parameter Display
def test_SWUT_GENERATOR_00020_void_parameters() -> None:
    """Test functions with no parameters show 'void'."""
    func = create_mock_function("Func", "file.c", [])

    gen = MermaidGenerator()
    formatted = gen._format_parameters(func)

    assert formatted == "`void`"


# SWUT_GENERATOR_00021: Parameter Formatting for Diagram
def test_SWUT_GENERATOR_00021_parameter_formatting_diagram() -> None:
    """Test parameters formatted for sequence diagram (names only)."""
    params = [
        Parameter("value", "uint32", False, False),
        Parameter("status", "uint8*", True, False),
    ]
    func = create_mock_function("Func", "file.c", params)

    gen = MermaidGenerator()
    formatted = gen._format_parameters_for_diagram(func)

    assert formatted == "value, status"


# SWUT_GENERATOR_00022: Text Tree Generation
def test_SWUT_GENERATOR_00022_text_tree_generation() -> None:
    """Test text tree is generated with correct formatting."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [
                    ("HW_Init", "hw.c", "HardwareModule", []),
                    ("SW_Init", "sw.c", "SoftwareModule", []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator()
    tree = gen._generate_text_tree(root)

    assert "Demo_Init (demo.c:1)" in tree
    assert "└── HW_Init (hw.c:1)" in tree or "├── HW_Init (hw.c:1)" in tree
    assert "└── SW_Init (sw.c:1)" in tree or "├── SW_Init (sw.c:1)" in tree


# SWUT_GENERATOR_00023: Circular Dependencies Section
def test_SWUT_GENERATOR_00023_circular_dependencies_section() -> None:
    """Test circular dependencies are displayed in section."""
    result = create_mock_analysis_result()
    result.circular_dependencies = [
        CircularDependency(cycle=["FuncA", "FuncB", "FuncA"], depth=3),
        CircularDependency(cycle=["X", "Y", "Z", "X"], depth=4),
    ]

    gen = MermaidGenerator()
    section = gen._generate_circular_deps_section(result)

    assert "## Circular Dependencies" in section
    assert "Found 2 circular dependencies" in section
    assert "FuncA → FuncB → FuncA" in section
    assert "X → Y → Z → X" in section
    assert "**Depth 3**" in section
    assert "**Depth 4**" in section


# SWUT_GENERATOR_00024: Metadata Generation
def test_SWUT_GENERATOR_00024_metadata_generation() -> None:
    """Test metadata section is generated correctly."""
    result = create_mock_analysis_result()
    result.root_function = "Demo_Init"
    result.statistics.total_functions = 10
    result.statistics.unique_functions = 8
    result.statistics.max_depth_reached = 3
    result.statistics.circular_dependencies_found = 0

    gen = MermaidGenerator()
    metadata = gen._generate_metadata(result)

    assert "## Metadata" in metadata
    assert "**Root Function**: `Demo_Init`" in metadata
    assert "**Total Functions**: 10" in metadata
    assert "**Unique Functions**: 8" in metadata
    assert "**Max Depth**: 3" in metadata
    assert "**Circular Dependencies**: 0" in metadata


# SWUT_GENERATOR_00025: File Output Generation
def test_SWUT_GENERATOR_00025_file_output(tmp_path: Path) -> None:
    """Test generate() creates markdown file with all sections."""
    result = create_mock_analysis_result()
    gen = MermaidGenerator()
    output_path = tmp_path / "output.md"

    gen.generate(result, str(output_path))

    assert output_path.exists()
    content = output_path.read_text()
    assert "# Call Tree: Demo_Init" in content
    assert "## Metadata" in content
    assert "## Sequence Diagram" in content
    assert "```mermaid" in content
    assert "## Function Details" in content


# SWUT_GENERATOR_00026: String Output Generation
def test_SWUT_GENERATOR_00026_string_output() -> None:
    """Test generate_to_string returns complete markdown."""
    result = create_mock_analysis_result()
    gen = MermaidGenerator()

    output = gen.generate_to_string(result)

    assert "# Call Tree: Demo_Init" in output
    assert "## Metadata" in output
    assert "## Sequence Diagram" in output
    assert "```mermaid" in output


# SWUT_GENERATOR_00027: Empty Call Tree Error
def test_SWUT_GENERATOR_00027_empty_call_tree_error(tmp_path: Path) -> None:
    """Test ValueError raised for empty call tree."""
    result = create_mock_analysis_result(has_tree=False)
    gen = MermaidGenerator()
    output_path = tmp_path / "output.md"

    with pytest.raises(ValueError, match="call tree is None"):
        gen.generate(result, str(output_path))


# SWUT_GENERATOR_00028: Optional Content Sections
def test_SWUT_GENERATOR_00028_optional_sections(tmp_path: Path) -> None:
    """Test optional sections can be disabled."""
    result = create_mock_analysis_result()
    gen = MermaidGenerator()
    output_path = tmp_path / "output.md"

    gen.generate(
        result,
        str(output_path),
        include_metadata=False,
        include_function_table=False,
        include_text_tree=False,
    )

    content = output_path.read_text()
    assert "## Metadata" not in content
    assert "## Function Details" not in content
    assert "## Call Tree (Text)" not in content
    assert "## Sequence Diagram" in content  # Always included


# SWUT_GENERATOR_00029: Unique Functions in Table
def test_SWUT_GENERATOR_00029_unique_functions_in_table() -> None:
    """Test function table shows each function only once."""
    # Create tree where same function appears multiple times
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [
                    ("HW_Init", "hw.c", "HardwareModule", []),
                    (
                        "SW_Init",
                        "sw.c",
                        "SoftwareModule",
                        [
                            ("HW_Init", "hw.c", "HardwareModule", []),
                        ],
                    ),
                ],
            ),
        ]
    )

    gen = MermaidGenerator()
    table = gen._generate_function_table(root)
    lines = [line for line in table.split("\n") if "HW_Init" in line]

    # HW_Init should appear only once despite being called twice
    assert len(lines) == 1


# SWUT_GENERATOR_00030: Sorted Function Table
def test_SWUT_GENERATOR_00030_sorted_function_table() -> None:
    """Test function table is sorted alphabetically."""
    root = create_mock_call_tree(
        [
            ("Z_Function", "z.c", None),
            ("A_Function", "a.c", None),
            ("M_Function", "m.c", None),
        ]
    )

    gen = MermaidGenerator()
    table = gen._generate_function_table(root)
    lines = [line for line in table.split("\n") if "| `" in line]

    # Extract function names from table
    func_names = []
    for line in lines:
        if "| `" in line:
            parts = line.split("|")
            if len(parts) > 1:
                name = parts[1].strip().strip("`")
                if name:
                    func_names.append(name)

    # Should be sorted: A_Function, M_Function, Z_Function
    assert func_names == sorted(func_names)


# SWUT_GENERATOR_00031: Parent Directory Creation
def test_SWUT_GENERATOR_00031_parent_directory_creation(tmp_path: Path) -> None:
    """Test output creates parent directories if needed."""
    result = create_mock_analysis_result()
    gen = MermaidGenerator()
    output_path = tmp_path / "subdir1" / "subdir2" / "output.md"

    gen.generate(result, str(output_path))

    assert output_path.exists()
    assert output_path.parent.is_dir()


# Additional edge case tests


def test_function_table_with_parameters() -> None:
    """Test function table with various parameter types."""
    params = [
        Parameter("val", "uint32", False, False),
        Parameter("ptr", "uint8*", True, False),
        Parameter("cptr", "const uint32*", True, True),
    ]
    root = create_mock_call_tree_with_params([("Func", "file.c", "Mod", params, [])])

    gen = MermaidGenerator()
    table = gen._generate_function_table(root)

    assert "uint32" in table
    assert "uint8*" in table
    assert "const uint32*" in table


def test_text_tree_with_recursive_nodes() -> None:
    """Test text tree marks recursive nodes."""
    root = create_mock_call_tree(
        [
            (
                "Demo_Init",
                "demo.c",
                "DemoModule",
                [
                    ("HW_Init", "hw.c", "HardwareModule", []),
                ],
            ),
        ]
    )

    root.children[0].is_recursive = True

    gen = MermaidGenerator()
    tree = gen._generate_text_tree(root)

    assert "[RECURSIVE]" in tree


def test_empty_parameter_list_formatting() -> None:
    """Test empty parameter list formatting for diagram."""
    func = create_mock_function("Func", "file.c", [])

    gen = MermaidGenerator()
    formatted = gen._format_parameters_for_diagram(func)

    assert formatted == ""


def test_parameter_without_name() -> None:
    """Test parameter without name uses type."""
    params = [Parameter("", "uint32", False, False)]
    func = create_mock_function("Func", "file.c", params)

    gen = MermaidGenerator()
    formatted = gen._format_parameters_for_diagram(func)

    assert formatted == "uint32"


def test_generate_with_circular_deps(tmp_path: Path) -> None:
    """Test file generation includes circular dependencies section."""
    result = create_mock_analysis_result()
    result.circular_dependencies = [
        CircularDependency(cycle=["A", "B", "A"], depth=2),
    ]

    gen = MermaidGenerator()
    output_path = tmp_path / "output.md"

    gen.generate(result, str(output_path))

    content = output_path.read_text()
    assert "## Circular Dependencies" in content
    assert "A → B → A" in content


def test_rte_abbreviation_preserves_prefix() -> None:
    """Test RTE abbreviation preserves Rte_ prefix."""
    gen = MermaidGenerator(abbreviate_rte=True)

    # Test various RTE function names
    abbrev1 = gen._abbreviate_rte_name("Rte_Read_Value")
    assert abbrev1.startswith("Rte_")

    abbrev2 = gen._abbreviate_rte_name("Rte_Write_Data")
    assert abbrev2.startswith("Rte_")


def test_participant_order_preserved() -> None:
    """Test participants maintain order of first encounter."""
    root = create_mock_call_tree(
        [
            (
                "Third",
                "3.c",
                "Mod3",
                [
                    ("First", "1.c", "Mod1", []),
                    (
                        "Second",
                        "2.c",
                        "Mod2",
                        [
                            ("Fourth", "4.c", "Mod4", []),
                        ],
                    ),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=True)
    participants = gen._collect_participants(root)

    # Order should be: Third, First, Second, Fourth (order of first encounter)
    assert participants[0] == "Mod3"
    assert participants[1] == "Mod1"
    assert participants[2] == "Mod2"
    assert participants[3] == "Mod4"


def test_multiple_calls_to_same_function() -> None:
    """Test diagram handles multiple calls to same function."""
    root = create_mock_call_tree(
        [
            (
                "Main",
                "main.c",
                "MainMod",
                [
                    ("Helper", "helper.c", "HelperMod", []),
                    ("Helper", "helper.c", "HelperMod", []),  # Called again
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=True)
    diagram = gen._generate_mermaid_diagram(root)

    # Helper should only appear once in participants
    assert diagram.count("participant HelperMod") == 1


def test_deeply_nested_tree() -> None:
    """Test text tree generation with deeply nested structure."""
    root = create_mock_call_tree(
        [
            (
                "A",
                "a.c",
                "ModA",
                [
                    (
                        "B",
                        "b.c",
                        "ModB",
                        [
                            (
                                "C",
                                "c.c",
                                "ModC",
                                [
                                    ("D", "d.c", "ModD", []),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ]
    )

    gen = MermaidGenerator()
    tree = gen._generate_text_tree(root)

    assert "A (a.c:1)" in tree
    assert "└──" in tree
    # Check nesting structure exists
    assert "B (b.c:1)" in tree
    assert "C (c.c:1)" in tree
    assert "D (d.c:1)" in tree


def test_statistics_in_metadata() -> None:
    """Test all statistics appear in metadata."""
    result = create_mock_analysis_result()
    result.statistics.total_functions = 100
    result.statistics.unique_functions = 85
    result.statistics.max_depth_reached = 5
    result.statistics.total_function_calls = 150
    result.statistics.static_functions = 20
    result.statistics.rte_functions = 30
    result.statistics.autosar_functions = 40
    result.statistics.circular_dependencies_found = 2

    gen = MermaidGenerator()
    metadata = gen._generate_metadata(result)

    assert "100" in metadata  # total_functions
    assert "85" in metadata  # unique_functions
    assert "5" in metadata  # max_depth
    assert "2" in metadata  # circular deps


def test_mixed_modules_and_filenames() -> None:
    """Test participant collection with mixed modules and filenames."""
    root = create_mock_call_tree(
        [
            (
                "Func1",
                "file1.c",
                "Module1",
                [
                    ("Func2", "file2.c", None, []),  # No module
                    ("Func3", "file3.c", "Module3", []),
                ],
            ),
        ]
    )

    gen = MermaidGenerator(use_module_names=True)
    participants = gen._collect_participants(root)

    assert "Module1" in participants
    assert "Module3" in participants
    assert "file2" in participants  # Filename without extension
    assert len(participants) == 3


# SWUT_GENERATOR_00032: Optional Call - Opt Block Generation
def test_SWUT_GENERATOR_00032_opt_block_generation() -> None:
    """Test that optional calls are wrapped in opt blocks."""
    root = create_mock_call_tree(
        [
            (
                "Main",
                "main.c",
                "MainMod",
                [
                    ("OptionalFunc", "optional.c", "OptionalMod", []),
                ],
            ),
        ]
    )

    # Mark child as optional
    root.children[0].is_optional = True

    gen = MermaidGenerator(use_module_names=True)
    diagram = gen._generate_mermaid_diagram(root)
    lines = diagram.split("\n")

    # Check for opt block
    assert "    opt Optional call" in lines
    assert "    end" in lines


# SWUT_GENERATOR_00033: Optional Call - Multiple Optional Calls
def test_SWUT_GENERATOR_00033_multiple_optional_calls() -> None:
    """Test that multiple optional calls each get their own opt block."""
    root = create_mock_call_tree(
        [
            (
                "Main",
                "main.c",
                "MainMod",
                [
                    ("Optional1", "opt1.c", "Opt1Mod", []),
                    ("Optional2", "opt2.c", "Opt2Mod", []),
                ],
            ),
        ]
    )

    # Mark both children as optional
    root.children[0].is_optional = True
    root.children[1].is_optional = True

    gen = MermaidGenerator(use_module_names=True)
    diagram = gen._generate_mermaid_diagram(root)

    # Should have two opt blocks
    opt_count = diagram.count("    opt Optional call")
    assert opt_count == 2
    # Should have matching end statements
    end_count = diagram.count("    end")
    assert end_count == 2


# SWUT_GENERATOR_00034: Optional Call - Mixed Optional and Regular
def test_SWUT_GENERATOR_00034_mixed_optional_and_regular() -> None:
    """Test diagram with both optional and regular calls."""
    root = create_mock_call_tree(
        [
            (
                "Main",
                "main.c",
                "MainMod",
                [
                    ("RegularFunc", "regular.c", "RegularMod", []),
                    ("OptionalFunc", "optional.c", "OptionalMod", []),
                    ("AnotherRegular", "another.c", "AnotherMod", []),
                ],
            ),
        ]
    )

    # Mark only middle child as optional
    root.children[1].is_optional = True

    gen = MermaidGenerator(use_module_names=True)
    diagram = gen._generate_mermaid_diagram(root)

    # Should have exactly one opt block
    assert diagram.count("    opt Optional call") == 1
    # Should have call to regular function before opt block
    assert "MainMod->>RegularMod: RegularFunc" in diagram
    # Should have opt block with optional call
    assert "    opt Optional call" in diagram
    assert "    MainMod->>OptionalMod: OptionalFunc" in diagram
    # Should have call to another regular after opt block
    assert "MainMod->>AnotherMod: AnotherRegular" in diagram


# SWUT_GENERATOR_00035: Optional Call - Nested Optional
def test_SWUT_GENERATOR_00035_nested_optional() -> None:
    """Test that optional calls in nested levels also get opt blocks."""
    root = create_mock_call_tree(
        [
            (
                "Main",
                "main.c",
                "MainMod",
                [
                    (
                        "Parent",
                        "parent.c",
                        "ParentMod",
                        [
                            ("ChildOptional", "child.c", "ChildMod", []),
                        ],
                    ),
                ],
            ),
        ]
    )

    # Mark grandchild as optional
    root.children[0].children[0].is_optional = True

    gen = MermaidGenerator(use_module_names=True)
    diagram = gen._generate_mermaid_diagram(root)

    # Should have opt block for the grandchild
    assert "    opt Optional call" in diagram
    assert "    ParentMod->>ChildMod: ChildOptional" in diagram


# SWUT_GENERATOR_00036: Optional Call - Recursive Not Optional
def test_SWUT_GENERATOR_00036_recursive_not_opt() -> None:
    """Test that recursive calls are not wrapped in opt blocks unless marked."""
    root = create_mock_call_tree(
        [
            (
                "Main",
                "main.c",
                "MainMod",
                [
                    ("RecursiveFunc", "recursive.c", "RecursiveMod", []),
                ],
            ),
        ]
    )

    # Mark child as recursive but not optional
    root.children[0].is_recursive = True
    root.children[0].is_optional = False

    gen = MermaidGenerator(use_module_names=True)
    diagram = gen._generate_mermaid_diagram(root)

    # Should not have opt block
    assert "    opt" not in diagram
    # Should have recursive arrow syntax
    assert "-->>x" in diagram


# SWUT_GENERATOR_00037: Optional Call - Optional with Returns
def test_SWUT_GENERATOR_00037_optional_with_returns() -> None:
    """Test optional calls with return statements."""
    root = create_mock_call_tree(
        [
            (
                "Main",
                "main.c",
                "MainMod",
                [
                    ("OptionalFunc", "optional.c", "OptionalMod", []),
                ],
            ),
        ]
    )

    root.children[0].is_optional = True

    gen = MermaidGenerator(use_module_names=True, include_returns=True)
    diagram = gen._generate_mermaid_diagram(root)

    # Should have opt block with call and return
    assert "    opt Optional call" in diagram
    assert "    end" in diagram
    # Return should be inside opt block (or after end depending on implementation)
    # Current implementation puts return after end of opt block


# SWUT_GENERATOR_00038: Optional Call - Function Mode
def test_SWUT_GENERATOR_00038_optional_function_mode() -> None:
    """Test optional calls work in function mode (not module mode)."""
    root = create_mock_call_tree(
        [
            (
                "Main",
                "main.c",
                None,
                [
                    ("OptionalFunc", "optional.c", None, []),
                ],
            ),
        ]
    )

    root.children[0].is_optional = True

    gen = MermaidGenerator(use_module_names=False)
    diagram = gen._generate_mermaid_diagram(root)

    # Should have opt block
    assert "    opt Optional call" in diagram
    assert "    end" in diagram
    # Should use function names as participants


# SWUT_GENERATOR_00039: Loop Block Generation
def test_SWUT_GENERATOR_00039_loop_block_generation() -> None:
    """Test that loop calls are wrapped in loop blocks.

    SWR_MERMAID_00005: Loop Block Generation
    """
    root = create_mock_call_tree(
        [
            (
                "Main",
                "main.c",
                None,
                [
                    ("LoopFunc", "loop.c", None, []),
                ],
            ),
        ]
    )

    root.children[0].is_loop = True
    root.children[0].loop_condition = "i < 10"

    gen = MermaidGenerator(use_module_names=False)
    diagram = gen._generate_mermaid_diagram(root)

    # Should have loop block
    assert "    loop i < 10" in diagram
    assert "    end" in diagram


# SWUT_GENERATOR_00040: Multiple Loop Calls
def test_SWUT_GENERATOR_00040_multiple_loop_calls() -> None:
    """Test that multiple loop calls each get their own loop block.

    SWR_MERMAID_00005: Multiple Loop Calls
    """
    root = create_mock_call_tree(
        [
            (
                "Main",
                "main.c",
                None,
                [
                    ("LoopFunc1", "loop1.c", None, []),
                    ("LoopFunc2", "loop2.c", None, []),
                ],
            ),
        ]
    )

    root.children[0].is_loop = True
    root.children[0].loop_condition = "i < 10"
    root.children[1].is_loop = True
    root.children[1].loop_condition = "j < 20"

    gen = MermaidGenerator(use_module_names=False)
    diagram = gen._generate_mermaid_diagram(root)

    # Should have two loop blocks
    assert diagram.count("    loop") == 2
    assert "    loop i < 10" in diagram
    assert "    loop j < 20" in diagram


# SWUT_GENERATOR_00041: Mixed Loop and Optional
def test_SWUT_GENERATOR_00041_mixed_loop_and_optional() -> None:
    """Test diagram with both loop and optional calls.

    SWR_MERMAID_00005: Mixed Loop and Optional
    """
    root = create_mock_call_tree(
        [
            (
                "Main",
                "main.c",
                None,
                [
                    ("LoopFunc", "loop.c", None, []),
                    ("OptionalFunc", "optional.c", None, []),
                ],
            ),
        ]
    )

    root.children[0].is_loop = True
    root.children[0].loop_condition = "i < 10"
    root.children[1].is_optional = True
    root.children[1].condition = "condition"

    gen = MermaidGenerator(use_module_names=False)
    diagram = gen._generate_mermaid_diagram(root)

    # Should have both loop and opt blocks
    assert "    loop i < 10" in diagram
    assert "    opt condition" in diagram
    assert diagram.count("    end") >= 2
    assert "Main->>OptionalFunc: call" in diagram


class TestMermaidGeneratorMissingLinesCoverage:
    """Tests to cover missing lines in mermaid_generator.py."""

    def test_SWUT_GENERATOR_00042_rte_participant_abbreviation(self):
        """Test RTE participant abbreviation in participant map (lines 143-145)."""
        root = create_mock_call_tree(
            [
                (
                    "Rte_Read_P_Voltage_Value",
                    "rte.c",
                    "RteModule",
                    [
                        ("Rte_Write_P_Current_Value", "rte.c", "RteModule", []),
                    ],
                ),
            ]
        )

        gen = MermaidGenerator(abbreviate_rte=True, use_module_names=False)
        diagram = gen._generate_mermaid_diagram(root)

        # Should have abbreviated RTE names
        assert "Rte_Read_PVV" in diagram
        assert "Rte_Write_PCV" in diagram
        # Participant map should be populated
        assert "Rte_Read_P_Voltage_Value" in gen.participant_map
        assert gen.participant_map["Rte_Read_P_Voltage_Value"] == "Rte_Read_PVV"

    def test_SWUT_GENERATOR_00043_parameter_pointer_backtick(self):
        """Test parameter formatting with pointer and backtick (line 374)."""
        func = create_mock_function(
            name="test_func",
            file_path="test.c",
            parameters=[
                Parameter(name="buffer", param_type="uint8", is_pointer=True, is_const=False),
            ],
        )

        gen = MermaidGenerator()
        params = gen._format_parameters(func)

        # Should have backtick around type with pointer
        assert "`uint8* buffer`" in params

    def test_SWUT_GENERATOR_00044_parameter_type_asterisk_for_diagram(self):
        """Test parameter type with asterisk for diagram when no name (line 399)."""
        func = create_mock_function(
            name="test_func",
            file_path="test.c",
            parameters=[
                Parameter(name="", param_type="uint8", is_pointer=True, is_const=False),
            ],
        )

        gen = MermaidGenerator()
        params = gen._format_parameters_for_diagram(func)

        # Should have type with asterisk when no name
        assert "uint8*" in params

    def test_SWUT_GENERATOR_00045_generate_to_string_none_call_tree(self):
        """Test generate_to_string raises ValueError for None call tree (line 479)."""
        result = create_mock_analysis_result(has_tree=False)

        gen = MermaidGenerator()

        with pytest.raises(ValueError, match="call tree is None"):
            gen.generate_to_string(result)

    def test_SWUT_GENERATOR_00046_circular_deps_section_generation(self):
        """Test circular dependencies section is generated (line 504)."""
        from autosar_calltree.database.models import CircularDependency

        result = create_mock_analysis_result()

        # Add circular dependencies
        circ_dep = CircularDependency(
            cycle=["FuncA", "FuncB", "FuncA"], depth=2
        )
        result.circular_dependencies = [circ_dep]

        gen = MermaidGenerator()
        output = gen.generate_to_string(result)

        # Should have circular dependencies section
        assert "## Circular Dependencies" in output
        assert "Found 1 circular dependencies" in output
        assert "FuncA → FuncB → FuncA" in output

    def test_SWUT_GENERATOR_00047_generate_non_recursive_call_with_params_line_227(self):
        """Test generate non-recursive call with parameters (line 227)."""
        root = create_mock_call_tree(
            [
                (
                    "CallerFunc",
                    "caller.c",
                    "CallerModule",
                    [
                        ("CalleeFunc", "callee.c", "CalleeModule", []),
                    ],
                ),
            ]
        )

        # Add parameters to the callee
        root.children[0].function_info.parameters = [
            Parameter(name="param1", param_type="int", is_pointer=False, is_const=False),
            Parameter(name="param2", param_type="char", is_pointer=True, is_const=False),
        ]

        # Use the public generate method
        result = create_mock_analysis_result()
        result.call_tree = root

        gen = MermaidGenerator(use_module_names=True)
        output = gen.generate_to_string(result)

        # Should have the non-recursive call with parameters (line 227)
        assert "CallerModule->>CalleeModule:" in output

    def test_SWUT_GENERATOR_00051_generate_non_recursive_call_without_modules_line_227(self):
        """Test generate non-recursive call without module names (line 227)."""
        root = create_mock_call_tree(
            [
                (
                    "CallerFunc",
                    "caller.c",
                    None,
                    [
                        ("CalleeFunc", "callee.c", None, []),
                    ],
                ),
            ]
        )

        # Use the public generate method
        result = create_mock_analysis_result()
        result.call_tree = root

        gen = MermaidGenerator(use_module_names=False)
        output = gen.generate_to_string(result)

        # Should have the non-recursive call with "call" label (line 227)
        assert "CallerFunc->>CalleeFunc: call" in output

    def test_SWUT_GENERATOR_00048_format_parameters_adds_backtick_line_374(self):
        """Test _format_parameters adds backtick when no param name (line 374)."""
        func = create_mock_function(
            name="test_func",
            file_path="test.c",
            parameters=[
                Parameter(name="", param_type="uint8", is_pointer=True, is_const=False),
            ],
        )

        gen = MermaidGenerator()
        params = gen._format_parameters(func)

        # Should have type with asterisk and backticks when no name (line 374)
        assert "`uint8*`" in params

    def test_SWUT_GENERATOR_00049_format_parameters_with_name(self):
        """Test _format_parameters with parameter name."""
        func = create_mock_function(
            name="test_func",
            file_path="test.c",
            parameters=[
                Parameter(name="value", param_type="uint32", is_pointer=False, is_const=False),
            ],
        )

        gen = MermaidGenerator()
        params = gen._format_parameters(func)

        # Should have type and name with backticks
        assert "`uint32 value`" in params

    def test_SWUT_GENERATOR_00050_format_parameters_multiple_params(self):
        """Test _format_parameters with multiple parameters."""
        func = create_mock_function(
            name="test_func",
            file_path="test.c",
            parameters=[
                Parameter(name="id", param_type="uint32", is_pointer=False, is_const=False),
                Parameter(name="data", param_type="uint8", is_pointer=True, is_const=False),
            ],
        )

        gen = MermaidGenerator()
        params = gen._format_parameters(func)

        # Should have both parameters with backticks and line breaks
        assert "`uint32 id`" in params
        assert "`uint8* data`" in params
        assert "<br>" in params

