"""
Rhapsody XMI generator for IBM Rhapsody UML sequence diagrams.

This module generates Rhapsody-compatible XMI 2.1 UML sequence diagrams
that can be imported into IBM Rhapsody 8.0+ for further editing and visualization.

Unlike the standard XmiGenerator, this implementation uses OMG UML 2.1 namespace
and XMI 2.1 format to match Rhapsody's native export structure.

Requirements:
- SWR_RH_00001: Rhapsody XMI 2.1 Compatibility
- SWR_RH_00002: Rhapsody Profile Support
- SWR_RH_00003: AUTOSAR Stereotype Support
- SWR_RH_00004: UUID-based Element IDs (GUID+ format)
- SWR_RH_00005: Rhapsody-specific Metadata
"""

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List
from uuid import uuid4

from lxml import etree

from autosar_calltree.database.models import (
    AnalysisResult,
    CallTreeNode,
    FunctionInfo,
)

if TYPE_CHECKING:
    from lxml.etree import _Element as Element
else:
    Element = etree.Element

SubElement = etree.SubElement


class RhapsodyXmiGenerator:
    """
    Generates Rhapsody-compatible XMI 2.1 UML sequence diagrams.

    This implementation uses OMG UML 2.1 namespace and XMI 2.1 format
    to match Rhapsody's native export structure for full compatibility.

    Key differences from XmiGenerator:
    - Uses XMI 2.1 instead of XMI 4.0
    - Uses OMG UML namespace instead of Eclipse UML2
    - Uses GUID+<UUID> ID format instead of rhapsody_<UUID>
    - Creates explicit MessageOccurrenceSpecification elements
    - Uses ownedAttribute for lifeline role definitions
    - Complex profile structure with eAnnotations and EPackage references

    Example usage:
        >>> from autosar_calltree.generators import RhapsodyXmiGenerator
        >>> generator = RhapsodyXmiGenerator(use_module_names=True)
        >>> generator.generate(result, "output/rhapsody.xmi")
    """

    # XMI 2.1 namespaces (matching Rhapsody export)
    XMI_NAMESPACE = "http://schema.omg.org/spec/XMI/2.1"
    XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
    UML_NAMESPACE = "http://www.omg.org/spec/UML/20090901"
    ECORE_NAMESPACE = "http://www.eclipse.org/emf/2002/Ecore"

    # Rhapsody-specific namespaces
    RHP_NAMESPACE = "http://RhapsodyStandardModel.RhpProperties/schemas/RHP/_doliYhVTEfGCaP-TK4cK4g/0"
    CG_NAMESPACE = "http://RhapsodyStandardModel.RhpProperties/schemas/CG/_doliYRVTEfGCaP-TK4cK4g/0"
    RHAPSODY_PROFILE_NAMESPACE = (
        "http://RhapsodyStandardModel/schemas/RhapsodyProfile/_doliYBVTEfGCaP-TK4cK4g/0"
    )
    PREDEFINED_TYPES_NAMESPACE = "http://RhapsodyStandardModel.PredefinedTypes/schemas/PredefinedTypes_profile/_doliZBVTEfGCaP-TK4cK4g/0"

    RHP_VERSION = "10.0.1"

    def __init__(self, use_module_names: bool = False):
        """
        Initialize the Rhapsody XMI generator.

        Args:
            use_module_names: Use SW module names as participants instead of function names
        """
        self.use_module_names = use_module_names

    def generate(self, result: AnalysisResult, output_path: str) -> None:
        """
        Generate Rhapsody XMI file from analysis result.

        Args:
            result: Analysis result containing call tree and metadata
            output_path: Path to output XMI file

        Raises:
            ValueError: If call tree is None
            IOError: If file cannot be written
        """
        if result.call_tree is None:
            raise ValueError("call tree is None, cannot generate XMI")

        # Generate XMI document
        root = self._generate_xmi_document(result, result.call_tree)

        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write to file with proper encoding
        xml_string = self._element_to_string(root)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_string)

    def generate_to_string(self, result: AnalysisResult) -> str:
        """
        Generate Rhapsody XMI as string without writing to file.

        Args:
            result: Analysis result containing call tree and metadata

        Returns:
            XML string representation of the XMI document

        Raises:
            ValueError: If call tree is None
        """
        if result.call_tree is None:
            raise ValueError("call tree is None, cannot generate XMI")

        root = self._generate_xmi_document(result, result.call_tree)
        return self._element_to_string(root)

    def _element_to_string(self, element: Element) -> str:
        """
        Convert Element to XML string with proper formatting.

        Args:
            element: XML element to convert

        Returns:
            Formatted XML string
        """
        # Convert to string using lxml
        xml_str = etree.tostring(element, encoding="unicode", pretty_print=False)

        # Add XML declaration
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'

    def _generate_id(self) -> str:
        """
        Generate Rhapsody-compatible UUID-based IDs.

        Rhapsody uses GUID+<UUID> format for element IDs.

        Returns:
            Unique identifier string with GUID+<UUID> format
        """
        # SWR_RH_00004: UUID-based Element IDs (GUID+ format)
        return f"GUID+{uuid4()}"

    def _generate_xmi_document(
        self, result: AnalysisResult, call_tree: CallTreeNode
    ) -> Element:
        """
        Generate the root XMI document element.

        Args:
            result: Analysis result containing metadata
            call_tree: Root node of the call tree

        Returns:
            Root XMI element with complete document structure
        """
        # SWR_RH_00001: XMI 2.1 Compatibility
        # Create namespace map for lxml
        nsmap = {
            "xmi": self.XMI_NAMESPACE,
            "xsi": self.XSI_NAMESPACE,
            "CG": self.CG_NAMESPACE,
            "PredefinedTypes_profile": self.PREDEFINED_TYPES_NAMESPACE,
            "RHP": self.RHP_NAMESPACE,
            "RhapsodyProfile": self.RHAPSODY_PROFILE_NAMESPACE,
            "ecore": self.ECORE_NAMESPACE,
            "uml": self.UML_NAMESPACE,
        }

        root = Element("XMI", nsmap=nsmap)
        root.set(f"{{{self.XMI_NAMESPACE}}}version", "2.1")

        # Create UML model - use prefixed form to force xmlns:uml declaration
        model = SubElement(root, "{http://www.omg.org/spec/UML/20090901}Model")
        model.set(f"{{{self.XMI_NAMESPACE}}}type", "uml:Model")
        model.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())
        model.set("name", f"CallTree_{result.root_function}")

        # Add element imports
        self._add_element_imports(model)

        # Add model constraint
        constraint = SubElement(model, "ownedRule")
        constraint.set(f"{{{self.XMI_NAMESPACE}}}type", "uml:Constraint")
        constraint.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())
        constraint.set("name", "Model1")
        constraint.set("context", model.get(f"{{{self.XMI_NAMESPACE}}}id"))

        # Add profile applications
        self._add_rhapsody_profiles(model)

        # Add metadata
        self._add_rhapsody_metadata(model, result)

        # Create package structure
        package = SubElement(model, "packagedElement")
        package.set(f"{{{self.XMI_NAMESPACE}}}type", "uml:Package")
        package.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())
        package.set("name", "Sequence_Diagram")

        # Create interaction
        interaction = SubElement(package, "packagedElement")
        interaction.set(f"{{{self.XMI_NAMESPACE}}}type", "uml:Interaction")
        interaction.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())
        interaction.set("name", f"seq_{result.root_function}")

        # Collect participants (lifelines)
        participants = self._collect_participants(call_tree)

        # Create role definitions
        role_ids = self._create_role_definitions(interaction, participants)

        # Create lifelines
        lifeline_elements = self._create_lifelines(interaction, participants, role_ids)

        # Create messages and message occurrences
        self._create_messages(interaction, call_tree, lifeline_elements)

        return root  # type: ignore[no-any-return]

    def _collect_participants(self, call_tree: CallTreeNode) -> Dict[str, str]:
        """
        Collect all unique participants (lifelines) from the call tree.

        Args:
            call_tree: Root node of the call tree

        Returns:
            Dictionary mapping participant names to their display names
        """
        participants = {}

        def traverse(node: CallTreeNode):
            if node.is_recursive:
                return

            # Determine participant name
            if self.use_module_names and node.function_info.sw_module:
                name = node.function_info.sw_module
            else:
                name = node.function_info.name

            # Store first occurrence of each participant
            if name not in participants:
                participants[name] = name

            # Traverse children
            for child in node.children:
                traverse(child)

        traverse(call_tree)
        return participants

    def _create_role_definitions(
        self, interaction: Element, participants: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Create ownedAttribute elements for lifeline roles.

        Args:
            interaction: Interaction element
            participants: Dictionary of participant names

        Returns:
            Dictionary mapping participant names to role IDs
        """
        role_ids = {}

        for name in participants.values():
            # Create role definition
            role = SubElement(interaction, "ownedAttribute")
            role.set(f"{{{self.XMI_NAMESPACE}}}type", "uml:Property")
            role.set(f"{{{self.XMI_NAMESPACE}}}id", f"{self._generate_id()}_Role")
            role.set("name", f"{name}Role")

            role_ids[name] = role.get(f"{{{self.XMI_NAMESPACE}}}id")

        return role_ids

    def _create_lifelines(
        self,
        interaction: Element,
        participants: Dict[str, str],
        role_ids: Dict[str, str],
    ) -> Dict[str, Element]:
        """
        Create lifeline elements for each participant.

        Args:
            interaction: Interaction element
            participants: Dictionary of participant names
            role_ids: Dictionary mapping participant names to role IDs

        Returns:
            Dictionary mapping participant names to lifeline elements
        """
        lifeline_elements = {}

        for name in participants.values():
            # Create lifeline
            lifeline = SubElement(interaction, "lifeline")
            lifeline.set(f"{{{self.XMI_NAMESPACE}}}type", "uml:Lifeline")
            lifeline.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())
            lifeline.set("name", name)

            # Reference role
            lifeline.set("represents", role_ids[name])

            # Reference interaction
            lifeline.set("interaction", interaction.get(f"{{{self.XMI_NAMESPACE}}}id"))

            # Initialize coveredBy (will be updated later)
            lifeline.set("coveredBy", "")

            lifeline_elements[name] = lifeline

        return lifeline_elements

    def _create_messages(
        self,
        interaction: Element,
        call_tree: CallTreeNode,
        lifeline_elements: Dict[str, Element],
    ) -> None:
        """
        Create message elements and message occurrence specifications.

        Args:
            interaction: Interaction element
            call_tree: Root node of the call tree
            lifeline_elements: Dictionary of lifeline elements
        """
        # Collect message occurrences for each lifeline
        lifeline_occurrences: Dict[str, List[str]] = {
            name: [] for name in lifeline_elements.keys()
        }

        # Track message index for sequencing
        message_index = 0

        def traverse(node: CallTreeNode, depth: int):
            nonlocal message_index

            if node.is_recursive:
                return

            # Determine source participant
            source_name = self._get_participant_name(node.function_info)

            # Process each child call
            for child in node.children:
                if child.is_recursive:
                    continue

                # Determine target participant
                target_name = self._get_participant_name(child.function_info)

                # Generate message ID
                message_id = self._generate_id()

                # Create message occurrence specifications
                source_occ_id = f"{message_id}_source_MessageOccurrenceSpecification"
                target_occ_id = f"{message_id}_target_MessageOccurrenceSpecification"

                # Create source occurrence
                source_occ = SubElement(interaction, "fragment")
                source_occ.set(
                    f"{{{self.XMI_NAMESPACE}}}type",
                    "uml:MessageOccurrenceSpecification",
                )
                source_occ.set(f"{{{self.XMI_NAMESPACE}}}id", source_occ_id)
                source_occ.set(
                    "covered",
                    lifeline_elements[source_name].get(f"{{{self.XMI_NAMESPACE}}}id"),
                )
                source_occ.set(
                    "enclosingInteraction",
                    interaction.get(f"{{{self.XMI_NAMESPACE}}}id"),
                )
                source_occ.set("message", message_id)

                # Create target occurrence
                target_occ = SubElement(interaction, "fragment")
                target_occ.set(
                    f"{{{self.XMI_NAMESPACE}}}type",
                    "uml:MessageOccurrenceSpecification",
                )
                target_occ.set(f"{{{self.XMI_NAMESPACE}}}id", target_occ_id)
                target_occ.set(
                    "covered",
                    lifeline_elements[target_name].get(f"{{{self.XMI_NAMESPACE}}}id"),
                )
                target_occ.set(
                    "enclosingInteraction",
                    interaction.get(f"{{{self.XMI_NAMESPACE}}}id"),
                )
                target_occ.set("message", message_id)

                # Track occurrences for coveredBy update
                lifeline_occurrences[source_name].append(source_occ_id)
                lifeline_occurrences[target_name].append(target_occ_id)

                # Create message element
                message = SubElement(interaction, "message")
                message.set(f"{{{self.XMI_NAMESPACE}}}type", "uml:Message")
                message.set(f"{{{self.XMI_NAMESPACE}}}id", message_id)
                message.set("name", child.function_info.name)
                message.set("receiveEvent", target_occ_id)
                message.set("sendEvent", source_occ_id)
                message.set(
                    "interaction", interaction.get(f"{{{self.XMI_NAMESPACE}}}id")
                )
                message.set("messageSort", "synchCall")

                # Add signature if available
                signature = self._format_message_signature(child.function_info)
                if signature:
                    message.set("signature", signature)

                message_index += 1

                # Handle conditional blocks (opt/loop/alt)
                if child.is_optional or child.is_loop:
                    self._create_combined_fragment(
                        interaction, child, message, message_index, lifeline_elements
                    )
                    message_index += 1

                # Recursively process children
                traverse(child, depth + 1)

        traverse(call_tree, 0)

        # Update coveredBy attributes on lifelines
        for name, occurrences in lifeline_occurrences.items():
            if name in lifeline_elements and occurrences:
                lifeline_elements[name].set("coveredBy", " ".join(occurrences))

    def _get_participant_name(self, function_info: FunctionInfo) -> str:
        """
        Get participant name for a function.

        Args:
            function_info: Function information

        Returns:
            Participant name (module name or function name)
        """
        if self.use_module_names and function_info.sw_module:
            return function_info.sw_module
        return function_info.name

    def _format_message_signature(self, function_info: FunctionInfo) -> str:
        """
        Format function signature for message.

        Args:
            function_info: Function information

        Returns:
            Formatted signature string
        """
        params = ", ".join(p.name for p in function_info.parameters)
        return f"{function_info.name}({params})"

    def _create_combined_fragment(
        self,
        interaction: Element,
        node: CallTreeNode,
        message: Element,
        index: int,
        lifeline_elements: Dict[str, Element],
    ) -> None:
        """
        Create combined fragment for conditional or loop blocks.

        Args:
            interaction: Interaction element
            node: Call tree node with conditional/loop flag
            message: Message element to wrap
            index: Message index
            lifeline_elements: Dictionary of lifeline elements
        """
        # Determine operator
        if node.is_loop:
            operator = "loop"
            condition = node.loop_condition or "condition"
        else:
            operator = "opt"
            condition = node.condition or "condition"

        # Create combined fragment
        fragment = SubElement(interaction, "fragment")
        fragment.set(f"{{{self.XMI_NAMESPACE}}}type", "uml:CombinedFragment")
        fragment.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())
        fragment.set("interactionOperator", operator)

        # Create operand
        operand = SubElement(fragment, "operand")
        operand.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())
        operand.set("name", condition)

        # Add message to operand (reparent from interaction)
        interaction.remove(message)
        operand.append(message)

    def _add_element_imports(self, model: Element) -> None:
        """
        Add element import elements for profile metaclasses.

        Args:
            model: Model element
        """
        # Standard element imports for UML metaclasses
        imports = [
            ("GUID_ROOT_Model_packagedElement_1799671379", "RhapsodyProfile"),
            ("GUID+RhpProperties_Package_packagedElement_2148", "RhpProperties"),
            ("GUID+RhpProperties_Package_packagedElement_81114", "CG"),
        ]

        for elem_id, name in imports:
            elem_import = SubElement(model, "elementImport")
            elem_import.set(f"{{{self.XMI_NAMESPACE}}}type", "uml:ElementImport")
            elem_import.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())
            elem_import.set("importedElement", elem_id)
            elem_import.set(
                "importingNamespace", model.get(f"{{{self.XMI_NAMESPACE}}}id")
            )

    def _add_rhapsody_profiles(self, model: Element) -> None:
        """
        Add Rhapsody profile applications with complex structure.

        Args:
            model: Model element
        """
        # SWR_RH_00002: Rhapsody Profile Support

        # Profile applications with eAnnotations and EPackage references
        profile_apps = [
            (
                "GUID+d8897902-b378-4014-9644-eb845d4ced6f_elementImport_1743488573_0",
                "GUID_ROOT_Model_packagedElement_1799671379",
                "GUID_ROOT_Model_packagedElement_1799671379_eAnnotations_0_contents_0",
            ),
            (
                "GUID+d8897902-b378-4014-9644-eb845d4ced6f_elementImport_1542580283_0",
                "GUID+RhpProperties_Package_packagedElement_2148",
                "GUID+RhpProperties_Package_packagedElement_2148_eAnnotations_0_contents_0",
            ),
        ]

        for app_id, profile_id, epackage_id in profile_apps:
            profile_app = SubElement(model, "profileApplication")
            profile_app.set(f"{{{self.XMI_NAMESPACE}}}type", "uml:ProfileApplication")
            profile_app.set(f"{{{self.XMI_NAMESPACE}}}id", app_id)
            profile_app.set("appliedProfile", profile_id)
            profile_app.set("applyingPackage", model.get(f"{{{self.XMI_NAMESPACE}}}id"))

            # Add xmi:Extension - use {namespace}tag format
            extension = SubElement(profile_app, f"{{{self.XMI_NAMESPACE}}}Extension")
            extension.set("extender", self.ECORE_NAMESPACE)

            # Add eAnnotations
            eannot = SubElement(extension, "eAnnotations")
            eannot.set(f"{{{self.XMI_NAMESPACE}}}type", "ecore:EAnnotation")
            eannot.set(f"{{{self.XMI_NAMESPACE}}}id", f"{app_id}_eAnnotations_0")
            eannot.set("source", "http://www.eclipse.org/uml2/2.0.0/UML")

            # Add references
            references = SubElement(eannot, "references")
            references.set(f"{{{self.XMI_NAMESPACE}}}type", "ecore:EPackage")
            references.set("href", epackage_id)

    def _add_rhapsody_metadata(self, model: Element, result: AnalysisResult) -> None:
        """
        Add Rhapsody-specific metadata.

        Args:
            model: Model element
            result: Analysis result
        """
        # SWR_RH_00005: Rhapsody-specific Metadata

        # Add tool comment
        comment = SubElement(model, "ownedComment")
        comment.set(f"{{{self.XMI_NAMESPACE}}}type", "uml:Comment")
        comment.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())

        body = SubElement(comment, "body")
        body.text = (
            f"Generated by AUTOSAR Call Tree Analyzer\n"
            f"Target: IBM Rhapsody {self.RHP_VERSION}\n"
            f"Analysis: {result.root_function}\n"
            f"Depth: {result.statistics.max_depth_reached}"
        )

        # Add Rhapsody settings comment
        settings = SubElement(model, "ownedComment")
        settings.set(f"{{{self.XMI_NAMESPACE}}}type", "uml:Comment")
        settings.set(f"{{{self.XMI_NAMESPACE}}}id", self._generate_id())

        settings_body = SubElement(settings, "body")
        settings_body.text = (
            "Rhapsody Settings:\n"
            "- Theme: Default\n"
            "- Layout: Automatic\n"
            "- Profile: AUTOSAR"
        )
