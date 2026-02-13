"""
Rhapsody XMI generator for IBM Rhapsody UML sequence diagrams.

This module extends XmiGenerator to produce Rhapsody-compatible XMI 2.5 files
that can be imported into IBM Rhapsody for further editing and visualization.

Requirements:
- SWR_RH_00001: Rhapsody XMI 2.5 Compatibility
- SWR_RH_00002: Rhapsody Profile Support
- SWR_RH_00003: AUTOSAR Stereotype Support
- SWR_RH_00004: UUID-based Element IDs
- SWR_RH_00005: Rhapsody-specific Metadata
"""

import uuid
from xml.etree.ElementTree import Element

from .xmi_generator import XmiGenerator


class RhapsodyXmiGenerator(XmiGenerator):
    """
    Generates Rhapsody-compatible XMI 2.5 UML sequence diagrams.

    Extends XmiGenerator to add:
    - Rhapsody-specific metamodel attributes
    - AUTOSAR stereotype support
    - Rhapsody profile imports
    - UUID-based element IDs (Rhapsody preference)
    - Rhapsody-specific metadata

    Example usage:
        >>> from autosar_calltree.generators import RhapsodyXmiGenerator
        >>> generator = RhapsodyXmiGenerator(use_module_names=True)
        >>> generator.generate(result, "output/rhapsody.xmi")
    """

    # Rhapsody-specific namespaces
    RHAPSODY_PROFILE = "http://www.ibm.com/Rhapsody/profile"
    RHAPSODY_NAMESPACE = "http://www.ibm.com/Rhapsody/profile"
    RHAPSODY_VERSION = "10.0.1"

    def __init__(
        self,
        use_module_names: bool = False,
    ):
        """
        Initialize the Rhapsody XMI generator.

        Args:
            use_module_names: Use SW module names as participants instead of function names
        """
        super().__init__(use_module_names=use_module_names)
        self.rhapsody_extensions_enabled = True

    def _generate_id(self) -> str:
        """
        Generate Rhapsody-compatible UUID-based IDs.

        Rhapsody prefers UUID-based IDs over sequential numeric IDs
        for better compatibility with its internal architecture.

        Returns:
            Unique identifier string with UUID format
        """
        # SWR_RH_00004: UUID-based Element IDs
        return f"rhapsody_{uuid.uuid4().hex}"

    def _generate_xmi_document(self, result, call_tree):
        """
        Override to add Rhapsody-specific metadata and profiles.

        Args:
            result: Analysis result containing metadata
            call_tree: Root node of the call tree (non-optional)

        Returns:
            Root XML Element for the XMI document with Rhapsody extensions
        """
        # SWR_RH_00005: Rhapsody-specific Metadata
        # Call parent implementation first
        root = super()._generate_xmi_document(result, call_tree)

        # Add Rhapsody-specific extensions
        self._add_rhapsody_profiles(root)
        self._add_rhapsody_metadata(root, result)

        return root

    def _add_rhapsody_profiles(self, root: Element) -> None:
        """
        Add Rhapsody profile imports to the XMI document.

        Rhapsody uses specific profiles for AUTOSAR and UML extensions.
        This method adds the necessary profile references.

        Args:
            root: Root XMI element
        """
        # SWR_RH_00002: Rhapsody Profile Support

        # Find the UML model element
        uml_namespace = self.UML_NAMESPACE
        model = root.find(f"{{{uml_namespace}}}Model")

        if model is not None:
            # Add profile application
            profile_application = self._create_element(
                model, "profileApplication", uml_namespace
            )

            # Reference to Rhapsody profile
            profile_ref = self._create_element(
                profile_application, "eAnnotations", uml_namespace
            )
            profile_ref.set("source", "http://www.ibm.com/Rhapsody/profile")

            # Add AUTOSAR stereotype application
            stereotype_application = self._create_element(
                model, "profileApplication", uml_namespace
            )

            autosar_ref = self._create_element(
                stereotype_application, "eAnnotations", uml_namespace
            )
            autosar_ref.set("source", "http://www.ibm.com/Rhapsody/profile/AUTOSAR")

    def _add_rhapsody_metadata(self, root: Element, result) -> None:
        """
        Add Rhapsody-specific tool metadata to the XMI document.

        This includes tool information, version details, and creation timestamps
        that Rhapsody uses for tracking and versioning.

        Args:
            root: Root XMI element
            result: Analysis result containing metadata
        """
        # SWR_RH_00005: Rhapsody-specific Metadata

        # Add tool information
        uml_namespace = self.UML_NAMESPACE
        xmi_namespace = self.XMI_NAMESPACE

        # Find the model element
        model = root.find(f"{{{uml_namespace}}}Model")

        if model is not None:
            # Add tool-specific annotations
            tool_annotation = self._create_element(
                model, "ownedComment", uml_namespace
            )
            tool_annotation.set(f"{{{xmi_namespace}}}id", self._generate_id())

            # Add body with tool information
            body = self._create_element(tool_annotation, "body", uml_namespace)
            body.text = (
                f"Generated by AUTOSAR Call Tree Analyzer\n"
                f"Target: IBM Rhapsody {self.RHAPSODY_VERSION}\n"
                f"Analysis: {result.root_function}\n"
                f"Depth: {result.statistics.max_depth_reached}"
            )

            # Add tagged values for Rhapsody-specific settings
            tagged_values = self._create_element(
                model, "ownedComment", uml_namespace
            )
            tagged_values.set(f"{{{xmi_namespace}}}id", self._generate_id())

            tagged_body = self._create_element(
                tagged_values, "body", uml_namespace
            )
            tagged_body.text = (
                "Rhapsody Settings:\n"
                "- Theme: Default\n"
                "- Layout: Automatic\n"
                "- Profile: AUTOSAR"
            )

    def _create_element(self, parent: Element, name: str, namespace: str) -> Element:
        """
        Helper method to create XML elements with proper namespace.

        Args:
            parent: Parent element
            name: Element name
            namespace: XML namespace URI

        Returns:
            Created element
        """
        from xml.etree.ElementTree import SubElement

        element = SubElement(parent, f"{{{namespace}}}{name}")
        return element

    def _add_autosar_stereotype(self, element: Element, stereotype: str) -> None:
        """
        Add AUTOSAR stereotype to a UML element.

        Rhapsody supports AUTOSAR-specific stereotypes for automotive modeling.
        This method applies stereotypes to lifelines and messages.

        Args:
            element: UML element to stereotype
            stereotype: Stereotype name (e.g., "SWC", "RunnableEntity")
        """
        # SWR_RH_00003: AUTOSAR Stereotype Support

        uml_namespace = self.UML_NAMESPACE
        xmi_namespace = self.XMI_NAMESPACE

        # Create stereotype application
        stereotype_app = self._create_element(
            element, "ownedComment", uml_namespace
        )
        stereotype_app.set(f"{{{xmi_namespace}}}id", self._generate_id())

        # Add stereotype as comment
        body = self._create_element(stereotype_app, "body", uml_namespace)
        body.text = f"<<{stereotype}>>"
