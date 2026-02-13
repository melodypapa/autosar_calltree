#!/usr/bin/env python3
"""
Rhapsody Import Helper Script

This script provides helper functions for importing XMI files into IBM Rhapsody.
Note: This is a utility script - actual import must be done manually in Rhapsody
via File > Import > OMG XMI.

Usage:
    python scripts/rhapsody_import_helper.py validate <xmi_file>
    python scripts/rhapsody_import_helper.py info <xmi_file>
    python scripts/rhapsody_import_helper.py prepare <xmi_file> [output_dir]

Requirements:
    - Python 3.9+
    - Generated XMI file from AUTOSAR Call Tree Analyzer
"""

import sys
from pathlib import Path
from xml.etree import ElementTree
from typing import Optional


def validate_xmi(xmi_file: Path) -> bool:
    """
    Validate XMI file structure and content.

    Args:
        xmi_file: Path to XMI file

    Returns:
        True if valid, False otherwise
    """
    try:
        # Parse XML
        tree = ElementTree.parse(str(xmi_file))
        root = tree.getroot()

        # Check for XMI root element
        if "XMI" not in root.tag:
            print(f"❌ Invalid XMI file: Missing XMI root element")
            return False

        # Check for UML model
        uml_model = root.find(".//{http://www.eclipse.org/uml2/5.0.0/UML}Model")
        if uml_model is None:
            print(f"❌ Invalid XMI file: Missing UML Model element")
            return False

        # Check for interaction (sequence diagram)
        interaction = root.find(".//{http://www.eclipse.org/uml2/5.0.0/UML}interaction")
        if interaction is None:
            print(f"⚠️  Warning: No interaction element found")

        # Count elements
        lifelines = root.findall(".//{http://www.eclipse.org/uml2/5.0.0/UML}lifeline")
        messages = root.findall(".//{http://www.eclipse.org/uml2/5.0.0/UML}message")
        fragments = root.findall(".//{http://www.eclipse.org/uml2/5.0.0/UML}fragment")

        print(f"✅ XMI file appears valid")
        print(f"   Lifelines: {len(lifelines)}")
        print(f"   Messages: {len(messages)}")
        print(f"   Fragments: {len(fragments)}")

        return True

    except ElementTree.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False


def show_info(xmi_file: Path) -> None:
    """
    Show detailed information about XMI file.

    Args:
        xmi_file: Path to XMI file
    """
    try:
        tree = ElementTree.parse(str(xmi_file))
        root = tree.getroot()

        # File size
        size_kb = xmi_file.stat().st_size / 1024
        print(f"📄 File: {xmi_file}")
        print(f"   Size: {size_kb:.1f} KB")

        # XMI version
        xmi_version = root.get("{http://www.omg.org/spec/XMI/20131001}version")
        print(f"   XMI Version: {xmi_version or 'Unknown'}")

        # Model information
        model = root.find(".//{http://www.eclipse.org/uml2/5.0.0/UML}Model")
        if model is not None:
            model_name = model.get("name")
            print(f"   Model: {model_name}")

        # Lifelines
        lifelines = root.findall(".//{http://www.eclipse.org/uml2/5.0.0/UML}lifeline")
        print(f"   Lifelines ({len(lifelines)}):")
        for lifeline in lifelines[:10]:  # Show first 10
            name = lifeline.get("name")
            visibility = lifeline.get("visibility")
            print(f"      - {name} ({visibility})")
        if len(lifelines) > 10:
            print(f"      ... and {len(lifelines) - 10} more")

        # Messages
        messages = root.findall(".//{http://www.eclipse.org/uml2/5.0.0/UML}message")
        print(f"   Messages: {len(messages)}")

        # Fragments (opt/loop blocks)
        fragments = root.findall(".//{http://www.eclipse.org/uml2/5.0.0/UML}fragment")
        if fragments:
            print(f"   Combined Fragments ({len(fragments)}):")
            for frag in fragments[:10]:  # Show first 10
                op = frag.get("interactionOperator")
                name = frag.get("name")
                print(f"      - {op} block: {name}")
            if len(fragments) > 10:
                print(f"      ... and {len(fragments) - 10} more")

        # Check for Rhapsody-specific elements
        print(f"   Rhapsody Elements:")
        has_uuid = any(
            elem.get("{http://www.omg.org/spec/XMI/20131001}id", "").startswith("rhapsody_")
            for elem in root.iter()
        )
        print(f"      UUID-based IDs: {'Yes' if has_uuid else 'No'}")

        # Check for profiles
        profile_apps = root.findall(".//{http://www.eclipse.org/uml2/5.0.0/UML}profileApplication")
        print(f"      Profile Applications: {len(profile_apps)}")

        # Check for comments/metadata
        comments = root.findall(".//{http://www.eclipse.org/uml2/5.0.0/UML}ownedComment")
        print(f"      Metadata Comments: {len(comments)}")

    except Exception as e:
        print(f"❌ Error reading XMI file: {e}")


def prepare_import(xmi_file: Path, output_dir: Optional[Path] = None) -> None:
    """
    Prepare XMI file for import into Rhapsody.

    This function creates a copy with optimized formatting and generates
    import instructions.

    Args:
        xmi_file: Path to source XMI file
        output_dir: Directory for prepared file (default: same as source)
    """
    if output_dir is None:
        output_dir = xmi_file.parent

    output_file = output_dir / f"{xmi_file.stem}_prepared.xmi"

    try:
        # Parse and re-format XML
        tree = ElementTree.parse(str(xmi_file))

        # Write with pretty formatting
        from xml.dom import minidom

        rough_string = ElementTree.tostring(tree.getroot(), encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        # Remove empty lines
        lines = [line for line in pretty_xml.split("\n") if line.strip()]
        formatted_xml = "\n".join(lines)

        # Write prepared file
        output_file.write_text(formatted_xml, encoding="utf-8")

        print(f"✅ Prepared file created: {output_file}")
        print(f"\n📋 Import Instructions:")
        print(f"   1. Open IBM Rhapsody (version 8.0+)")
        print(f"   2. Select File > Import > OMG XMI...")
        print(f"   3. Browse to: {output_file.absolute()}")
        print(f"   4. Click Open")
        print(f"\n💡 Tips:")
        print(f"   - Use the prepared file for better formatting")
        print(f"   - If import fails, try validating first: python {sys.argv[0]} validate {xmi_file}")
        print(f"   - Check documentation: docs/rhapsody_export.md")

    except Exception as e:
        print(f"❌ Error preparing file: {e}")


def print_usage() -> None:
    """Print usage information."""
    print(__doc__)
    print(f"\nCommands:")
    print(f"   validate  <xmi_file>    Validate XMI file structure")
    print(f"   info      <xmi_file>    Show detailed XMI information")
    print(f"   prepare   <xmi_file> [output_dir]  Prepare XMI for import")
    print(f"\nExamples:")
    print(f"   # Validate XMI file")
    print(f"   python {sys.argv[0]} validate diagrams/demo.xmi")
    print(f"\n   # Show XMI information")
    print(f"   python {sys.argv[0]} info diagrams/demo.xmi")
    print(f"\n   # Prepare for import")
    print(f"   python {sys.argv[0]} prepare diagrams/demo.xmi diagrams/prepared/")
    print(f"\nDocumentation:")
    print(f"   docs/rhapsody_export.md")
    print(f"   docs/rhapsody_troubleshooting.md")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 3:
        print_usage()
        return 1

    command = sys.argv[1]
    xmi_file = Path(sys.argv[2])

    # Check if file exists
    if not xmi_file.exists():
        print(f"❌ Error: File not found: {xmi_file}")
        return 1

    # Execute command
    if command == "validate":
        success = validate_xmi(xmi_file)
        return 0 if success else 1

    elif command == "info":
        show_info(xmi_file)
        return 0

    elif command == "prepare":
        output_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else None
        prepare_import(xmi_file, output_dir)
        return 0

    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
