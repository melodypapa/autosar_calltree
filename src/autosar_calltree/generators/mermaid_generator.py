"""
Mermaid sequence diagram generator.

This module generates Mermaid sequence diagram syntax from call trees,
outputting markdown files with embedded diagrams.

Requirements:
- SWR_MERMAID_00001: Module-Based Participants
- SWR_MERMAID_00002: Module Column in Function Table
- SWR_MERMAID_00003: Fallback Behavior
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..database.models import AnalysisResult, CallTreeNode, FunctionInfo


class MermaidGenerator:
    """
    Generates Mermaid sequence diagrams from call trees.

    This class converts call tree structures into Mermaid diagram syntax,
    creates markdown documents with metadata, and handles formatting options.
    """

    def __init__(
        self,
        abbreviate_rte: bool = True,
        use_module_names: bool = False,
        include_returns: bool = False,
    ):
        """
        Initialize the Mermaid generator.

        Args:
            abbreviate_rte: Whether to abbreviate long RTE function names
            use_module_names: Use SW module names as participants instead of function names
            include_returns: Whether to include return statements in the sequence diagram (default: False)
        """
        self.abbreviate_rte = abbreviate_rte
        self.use_module_names = use_module_names
        self.include_returns = include_returns
        self.participant_map: Dict[str, str] = {}  # Map full names to abbreviated names
        self.next_participant_id = 1

    def generate(
        self,
        result: AnalysisResult,
        output_path: str,
        include_metadata: bool = True,
        include_function_table: bool = True,
        include_text_tree: bool = True,
    ) -> None:
        """
        Generate Mermaid diagram and save to markdown file.

        Args:
            result: Analysis result containing call tree
            output_path: Path to output markdown file
            include_metadata: Include metadata section
            include_function_table: Include function details table
            include_text_tree: Include text-based tree representation
        """
        if not result.call_tree:
            raise ValueError("Cannot generate diagram: call tree is None")

        # Build content sections
        content = []

        # Add title
        content.append(f"# Call Tree: {result.root_function}\n")

        # Add metadata
        if include_metadata:
            content.append(self._generate_metadata(result))

        # Add sequence diagram
        content.append("## Sequence Diagram\n")
        diagram = self._generate_mermaid_diagram(result.call_tree)
        content.append("```mermaid")
        content.append(diagram)
        content.append("```\n")

        # Add function details table
        if include_function_table:
            content.append(self._generate_function_table(result.call_tree))

        # Add text tree
        if include_text_tree:
            content.append(self._generate_text_tree(result.call_tree))

        # Add circular dependencies if any
        if result.circular_dependencies:
            content.append(self._generate_circular_deps_section(result))

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(content), encoding="utf-8")

    def _generate_metadata(self, result: AnalysisResult) -> str:
        """
        Generate metadata section.

        Args:
            result: Analysis result

        Returns:
            Markdown formatted metadata
        """
        lines = [
            "## Metadata\n",
            f"- **Root Function**: `{result.root_function}`",
            f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Total Functions**: {result.statistics.total_functions}",
            f"- **Unique Functions**: {result.statistics.unique_functions}",
            f"- **Max Depth**: {result.statistics.max_depth_reached}",
            f"- **Circular Dependencies**: {result.statistics.circular_dependencies_found}",
            "",
        ]
        return "\n".join(lines)

    def _generate_mermaid_diagram(self, root: CallTreeNode) -> str:
        """
        Generate Mermaid sequence diagram syntax.

        Args:
            root: Root node of call tree

        Returns:
            Mermaid diagram as string
        """
        lines = ["sequenceDiagram"]

        # Collect all participants
        participants = self._collect_participants(root)

        # Add participant declarations
        for participant in participants:
            if self.abbreviate_rte and participant.startswith("Rte_"):
                abbrev = self._abbreviate_rte_name(participant)
                self.participant_map[participant] = abbrev
                lines.append(f"    participant {abbrev} as {participant}")
            else:
                lines.append(f"    participant {participant}")

        lines.append("")

        # Generate sequence calls
        self._generate_sequence_calls(root, lines)

        return "\n".join(lines)

    def _collect_participants(self, root: CallTreeNode) -> List[str]:
        """
        Collect all unique participants (functions or modules) in tree.

        Implements: SWR_MERMAID_00001 (Module-Based Participants)

        Args:
            root: Root node of call tree

        Returns:
            List of participant names in the order they are first encountered
        """
        participants = []

        def traverse(node: CallTreeNode):
            # Use module name if enabled, otherwise use function name
            if self.use_module_names:
                # Use module name if available, otherwise fallback to filename
                participant = (
                    node.function_info.sw_module
                    or Path(node.function_info.file_path).stem
                )
            else:
                participant = node.function_info.name

            # Add participant only if not already in the list
            if participant not in participants:
                participants.append(participant)

            for child in node.children:
                traverse(child)

        traverse(root)
        return participants

    def _generate_sequence_calls(
        self, node: CallTreeNode, lines: List[str], caller: Optional[str] = None
    ) -> None:
        """
        Generate sequence call statements recursively.

        Implements: SWR_MERMAID_00001 (Module-Based Participants with function names on arrows)

        Args:
            node: Current node in call tree
            lines: List of lines to append to
            caller: Name of calling function or module (None for root)
        """
        # Determine current participant (module or function name)
        if self.use_module_names:
            current_participant = (
                node.function_info.sw_module or Path(node.function_info.file_path).stem
            )
            # When using modules, show function name on arrows
            call_label = node.function_info.name
        else:
            current_participant = self._get_participant_name(node.function_info.name)
            # When using function names, show generic "call" label
            call_label = "call"

        # Add parameters to the call label
        if node.function_info.parameters:
            params_str = self._format_parameters_for_diagram(node.function_info)
            call_label = f"{call_label}({params_str})"

        # Generate call from caller to current
        if caller:
            if node.is_recursive:
                if self.use_module_names:
                    label = f"{call_label} [recursive]"
                else:
                    label = "recursive call"
                lines.append(f"    {caller}-->>x{current_participant}: {label}")
            else:
                lines.append(f"    {caller}->>{current_participant}: {call_label}")

        # Generate calls to children
        for child in node.children:
            self._generate_sequence_calls(child, lines, current_participant)

        # Generate return from current to caller (only if include_returns is True)
        if caller and not node.is_recursive and self.include_returns:
            lines.append(f"    {current_participant}-->>{caller}: return")

    def _get_participant_name(self, function_name: str) -> str:
        """
        Get participant name (possibly abbreviated).

        Args:
            function_name: Original function name

        Returns:
            Participant name to use in diagram
        """
        return str(self.participant_map.get(function_name, function_name))

    def _abbreviate_rte_name(self, rte_function: str) -> str:
        """
        Abbreviate RTE function name.

        Args:
            rte_function: Full RTE function name

        Returns:
            Abbreviated name
        """
        # Simple abbreviation: Rte_Read_P_Voltage_Value -> Rte_Read_PVV
        parts = rte_function.split("_")
        if len(parts) <= 2:
            return rte_function

        # Keep Rte_ prefix and first operation, abbreviate rest
        prefix = "_".join(parts[:2])  # e.g., "Rte_Read"
        abbrev_parts = [p[0].upper() for p in parts[2:] if p]
        abbrev = "".join(abbrev_parts)

        return f"{prefix}_{abbrev}"

    def _generate_function_table(self, root: CallTreeNode) -> str:
        """
        Generate markdown table of function details.

        Args:
            root: Root node of call tree

        Returns:
            Markdown formatted table
        """
        # Build header based on whether we're showing modules
        if self.use_module_names:
            lines = [
                "## Function Details\n",
                "| Function | Module | File | Line | Return Type | Parameters |",
                "|----------|--------|------|------|-------------|------------|",
            ]
        else:
            lines = [
                "## Function Details\n",
                "| Function | File | Line | Return Type | Parameters |",
                "|----------|------|------|-------------|------------|",
            ]

        # Collect all unique functions
        functions = []
        seen = set()

        def traverse(node: CallTreeNode):
            if node.function_info.name not in seen:
                seen.add(node.function_info.name)
                functions.append(node.function_info)
            for child in node.children:
                traverse(child)

        traverse(root)

        # Sort by function name
        functions.sort(key=lambda f: f.name)

        # Add table rows
        for func in functions:
            file_name = Path(func.file_path).name
            params = self._format_parameters(func)

            if self.use_module_names:
                module = func.sw_module or "N/A"
                lines.append(
                    f"| `{func.name}` | {module} | {file_name} | {func.line_number} | "
                    f"`{func.return_type}` | {params} |"
                )
            else:
                lines.append(
                    f"| `{func.name}` | {file_name} | {func.line_number} | "
                    f"`{func.return_type}` | {params} |"
                )

        lines.append("")
        return "\n".join(lines)

    def _format_parameters(self, func: FunctionInfo) -> str:
        """
        Format function parameters for table.

        Args:
            func: Function information

        Returns:
            Formatted parameter string
        """
        if not func.parameters:
            return "`void`"

        param_strs = []
        for param in func.parameters:
            type_str = param.param_type
            if param.is_pointer:
                type_str += "*"

            if param.name:
                param_strs.append(f"`{type_str} {param.name}`")
            else:
                param_strs.append(f"`{type_str}`")

        return "<br>".join(param_strs)

    def _format_parameters_for_diagram(self, func: FunctionInfo) -> str:
        """
        Format function parameters for sequence diagram display.

        Args:
            func: Function information

        Returns:
            Formatted parameter string for diagram
        """
        if not func.parameters:
            return ""

        param_strs = []
        for param in func.parameters:
            if param.name:
                param_strs.append(param.name)
            else:
                # If no parameter name, use the type
                type_str = param.param_type
                if param.is_pointer:
                    type_str += "*"
                param_strs.append(type_str)

        return ", ".join(param_strs)

    def _generate_text_tree(self, root: CallTreeNode) -> str:
        """
        Generate text-based tree representation.

        Args:
            root: Root node of call tree

        Returns:
            Markdown formatted text tree
        """
        lines = ["## Call Tree (Text)\n", "```"]

        def traverse(node: CallTreeNode, prefix: str = "", is_last: bool = True):
            connector = "└── " if is_last else "├── "

            func_name = node.function_info.name
            file_name = Path(node.function_info.file_path).name
            line = f"{prefix}{connector}{func_name} ({file_name}:{node.function_info.line_number})"

            if node.is_recursive:
                line += " [RECURSIVE]"

            lines.append(line)

            if node.children:
                new_prefix = prefix + ("    " if is_last else "│   ")
                for idx, child in enumerate(node.children):
                    is_last_child = idx == len(node.children) - 1
                    traverse(child, new_prefix, is_last_child)

        # Start with root
        func_name = root.function_info.name
        file_name = Path(root.function_info.file_path).name
        lines.append(f"{func_name} ({file_name}:{root.function_info.line_number})")

        for idx, child in enumerate(root.children):
            is_last = idx == len(root.children) - 1
            traverse(child, "", is_last)

        lines.append("```\n")
        return "\n".join(lines)

    def _generate_circular_deps_section(self, result: AnalysisResult) -> str:
        """
        Generate section for circular dependencies.

        Args:
            result: Analysis result

        Returns:
            Markdown formatted circular dependencies section
        """
        lines = [
            "## Circular Dependencies\n",
            f"Found {len(result.circular_dependencies)} circular dependencies:\n",
        ]

        for idx, circ_dep in enumerate(result.circular_dependencies, 1):
            cycle_str = " → ".join(circ_dep.cycle)
            lines.append(f"{idx}. **Depth {circ_dep.depth}**: `{cycle_str}`")

        lines.append("")
        return "\n".join(lines)

    def generate_to_string(self, result: AnalysisResult) -> str:
        """
        Generate Mermaid diagram as string without writing to file.

        Args:
            result: Analysis result

        Returns:
            Complete markdown document as string
        """
        if not result.call_tree:
            raise ValueError("Cannot generate diagram: call tree is None")

        content = []

        # Add title
        content.append(f"# Call Tree: {result.root_function}\n")

        # Add metadata
        content.append(self._generate_metadata(result))

        # Add sequence diagram
        content.append("## Sequence Diagram\n")
        diagram = self._generate_mermaid_diagram(result.call_tree)
        content.append("```mermaid")
        content.append(diagram)
        content.append("```\n")

        # Add function table
        content.append(self._generate_function_table(result.call_tree))

        # Add text tree
        content.append(self._generate_text_tree(result.call_tree))

        # Add circular dependencies
        if result.circular_dependencies:
            content.append(self._generate_circular_deps_section(result))

        return "\n".join(content)
