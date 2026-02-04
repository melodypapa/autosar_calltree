"""
XMI (XML Metadata Interchange) generator for UML sequence diagrams.

This module generates XMI 2.5 compliant XML documents representing
UML sequence diagrams from call trees. The XMI format can be imported
into UML tools like Enterprise Architect, Visual Paradigm, etc.

Requirements:
- SWR_XMI_00001: XMI 2.5 Compliance
- SWR_XMI_00002: Sequence Diagram Representation
"""

from pathlib import Path
from typing import Dict, List, Optional
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from ..database.models import AnalysisResult, CallTreeNode


class XmiGenerator:
    """
    Generates XMI 2.5 format UML sequence diagrams from call trees.

    This class converts call tree structures into XMI XML documents,
    following the UML 2.5 XMI specification for sequence diagrams.
    """

    # XMI/UML namespaces
    XMI_NAMESPACE = "http://www.omg.org/spec/XMI/20131001"
    XMI_URI = "http://www.omg.org/spec/XMI/20131001"
    UML_NAMESPACE = "http://www.eclipse.org/uml2/5.0.0/UML"
    UML_URI = "http://www.eclipse.org/uml2/5.0.0/UML"

    def __init__(
        self,
        use_module_names: bool = False,
    ):
        """
        Initialize the XMI generator.

        Args:
            use_module_names: Use SW module names as participants instead of function names
        """
        self.use_module_names = use_module_names
        self.element_id_counter = 0
        self.participant_map: Dict[str, str] = {}  # Map names to XMI IDs

    def generate(
        self,
        result: AnalysisResult,
        output_path: str,
    ) -> None:
        """
        Generate XMI document and save to file.

        Args:
            result: Analysis result containing call tree
            output_path: Path to output XMI file
        """
        if not result.call_tree:
            raise ValueError("Cannot generate XMI: call tree is None")

        # Build XMI document
        root_element = self._generate_xmi_document(result, result.call_tree)

        # Pretty print and write to file
        xml_str = self._prettify_xml(root_element)
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(xml_str, encoding="utf-8")

    def _generate_xmi_document(self, result: AnalysisResult, call_tree: CallTreeNode) -> Element:
        """
        Generate XMI root element with complete document structure.

        Args:
            result: Analysis result containing metadata
            call_tree: Root node of the call tree (non-optional)

        Returns:
            Root XML Element for the XMI document
        """
        # Create root element with XMI namespace
        root = Element(
            f"{{{self.XMI_NAMESPACE}}}XMI",
            attrib={
                f"{{{self.XMI_NAMESPACE}}}version": "4.0",
                "xmlns:xmi": self.XMI_URI,
                "xmlns:uml": self.UML_URI,
            },
        )

        # Create UML model
        model = SubElement(root, f"{{{self.UML_NAMESPACE}}}Model", attrib={
            f"{{{self.XMI_NAMESPACE}}}id": self._generate_id(),
            "name": f"CallTree_{result.root_function}",
            "visibility": "public",
        })

        # Package the model
        packaged_element = SubElement(model, f"{{{self.UML_NAMESPACE}}}packagedElement")
        packaged_element.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())
        packaged_element.set("name", f"Sequence_{result.root_function}")
        packaged_element.set("visibility", "public")

        # Create interaction (sequence diagram container)
        interaction = self._create_interaction(packaged_element, result)

        # Collect all participants and create lifelines
        participants = self._collect_participants(call_tree)
        lifeline_elements = self._create_lifelines(interaction, participants)

        # Create messages (function calls)
        self._create_messages(call_tree, lifeline_elements, interaction)

        return root

    def _create_interaction(
        self, parent: Element, result: AnalysisResult
    ) -> Element:
        """
        Create UML interaction element (sequence diagram container).

        Args:
            parent: Parent element
            result: Analysis result

        Returns:
            Interaction element
        """
        interaction = SubElement(parent, f"{{{self.UML_NAMESPACE}}}packagedElement")
        interaction.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())
        interaction.set("name", f"CallSequence_{result.root_function}")
        interaction.set("visibility", "public")
        interaction.set("isReentrant", "false")

        # Set type to Interaction
        interaction_type = SubElement(interaction, f"{{{self.UML_NAMESPACE}}}ownedAttribute")
        interaction_type.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())
        interaction_type.set("name", "interactionType")
        interaction_type.set("visibility", "public")
        interaction_type.set("type", "Interaction")

        return interaction

    def _collect_participants(self, root: CallTreeNode) -> List[str]:
        """
        Collect all unique participants (functions or modules) in tree.

        Args:
            root: Root node of call tree

        Returns:
            List of participant names in the order they are first encountered
        """
        participants = []

        def traverse(node: CallTreeNode):
            # Use module name if enabled, otherwise use function name
            if self.use_module_names:
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

    def _create_lifelines(
        self, interaction: Element, participants: List[str]
    ) -> Dict[str, Element]:
        """
        Create UML lifelines for each participant.

        Args:
            interaction: Interaction element
            participants: List of participant names

        Returns:
            Dictionary mapping participant names to their lifeline elements
        """
        lifeline_elements = {}

        for idx, participant in enumerate(participants):
            # Create lifeline
            lifeline = SubElement(interaction, f"{{{self.UML_NAMESPACE}}}lifeline")
            lifeline_id = self._generate_id()
            lifeline.set(f"{{{self.XMI_NAMESPACE}}}id", lifeline_id)
            lifeline.set("name", participant)
            lifeline.set("visibility", "public")

            # Create represents property (connects to classifier)
            represents = SubElement(lifeline, f"{{{self.UML_NAMESPACE}}}represents")
            represents_id = self._generate_id()
            represents.set(f"{{{self.XMI_NAMESPACE}}}id", represents_id)
            represents.set("name", participant)

            # Store mapping
            self.participant_map[participant] = lifeline_id
            lifeline_elements[participant] = lifeline

        return lifeline_elements

    def _create_messages(
        self,
        root: CallTreeNode,
        lifeline_elements: Dict[str, Element],
        interaction: Element,
    ) -> None:
        """
        Create UML messages (function calls) between lifelines.

        Args:
            root: Root node of call tree
            lifeline_elements: Dictionary of lifeline elements
            interaction: Interaction element
        """
        message_counter = 0

        def traverse(node: CallTreeNode, parent_participant: Optional[str] = None):
            nonlocal message_counter

            # Determine current participant
            if self.use_module_names:
                current_participant = (
                    node.function_info.sw_module
                    or Path(node.function_info.file_path).stem
                )
            else:
                current_participant = node.function_info.name

            # Create message from parent to current
            if parent_participant:
                message = SubElement(interaction, f"{{{self.UML_NAMESPACE}}}message")
                message_id = self._generate_id()
                message.set(f"{{{self.XMI_NAMESPACE}}}id", message_id)
                message.set("name", node.function_info.name)
                message.set("visibility", "public")
                message.set("messageSort", "synchCall")

                # Set message signature
                signature = self._format_message_signature(node)
                message.set("signature", signature)

                # Connect to lifelines
                send_event = SubElement(message, f"{{{self.UML_NAMESPACE}}}sendEvent")
                send_event.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())

                receive_event = SubElement(message, f"{{{self.UML_NAMESPACE}}}receiveEvent")
                receive_event.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())

                # Set source and target
                message.set(
                    "sendEvent",
                    f"{{{self.XMI_NAMESPACE}}}{self.participant_map.get(parent_participant, '')}"
                )
                message.set(
                    "receiveEvent",
                    f"{{{self.XMI_NAMESPACE}}}{self.participant_map.get(current_participant, '')}"
                )

                message_counter += 1

                # Mark recursive calls
                if node.is_recursive:
                    message.set("messageSort", "reply")

            # Traverse children
            for child in node.children:
                traverse(child, current_participant)

        # Start traversal from root's children
        for child in root.children:
            traverse(child, None)

    def _format_message_signature(self, node: CallTreeNode) -> str:
        """
        Format message signature with parameters.

        Args:
            node: Call tree node

        Returns:
            Formatted signature string
        """
        func = node.function_info

        if not func.parameters:
            return f"{func.name}()"

        params = []
        for param in func.parameters:
            if param.name:
                params.append(param.name)
            else:
                type_str = param.param_type
                if param.is_pointer:
                    type_str += "*"
                params.append(type_str)

        return f"{func.name}({', '.join(params)})"

    def _generate_id(self) -> str:
        """
        Generate unique XMI ID.

        Returns:
            Unique identifier string
        """
        self.element_id_counter += 1
        return f"calltree_{self.element_id_counter}"

    def _prettify_xml(self, element: Element) -> str:
        """
        Convert XML element to pretty-printed string.

        Args:
            element: Root XML element

        Returns:
            Pretty-printed XML string
        """
        rough_string = tostring(element, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        # Add XML declaration and comments
        lines = pretty_xml.split('\n')
        filtered_lines = [line for line in lines if line.strip()]

        return '\n'.join(filtered_lines)

    def generate_to_string(self, result: AnalysisResult) -> str:
        """
        Generate XMI document as string without writing to file.

        Args:
            result: Analysis result

        Returns:
            XMI document as string
        """
        if not result.call_tree:
            raise ValueError("Cannot generate XMI: call tree is None")

        root_element = self._generate_xmi_document(result, result.call_tree)
        return self._prettify_xml(root_element)
